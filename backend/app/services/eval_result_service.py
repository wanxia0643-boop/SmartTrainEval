"""评价结果业务逻辑。"""
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.achievement import TrainAchievement
from app.models.eval_result import EvalResult
from app.models.indicator import EvalIndicator
from app.services.base import CRUDBase

# 默认各评价方式等权；可按需调整，如教师评价权重更高
DEFAULT_TYPE_WEIGHTS: dict[int, Decimal] = {
    1: Decimal("1"),  # AI
    2: Decimal("1"),  # 教师
    3: Decimal("1"),  # 企业导师
    4: Decimal("1"),  # 学生自评
}


class EvalResultService(CRUDBase[EvalResult]):
    def __init__(self) -> None:
        super().__init__(EvalResult)

    def list_by_achievement(
        self, db: Session, achievement_id: int
    ) -> list[EvalResult]:
        """查询某成果的全部有效评价结果。"""
        stmt = select(EvalResult).where(
            EvalResult.achievement_id == achievement_id,
            EvalResult.is_deleted == 0,
        )
        return list(db.scalars(stmt).all())

    def recalc_final_score(
        self,
        db: Session,
        achievement_id: int,
        type_weights: dict[int, Decimal] | None = None,
    ) -> Decimal | None:
        """按指标权重汇总成果得分，并回填 train_achievement.final_score。

        计算逻辑（百分制 0-100）：
          1. 同一指标下若有多条评价（AI/教师/企业导师/自评），按 eval_type 权重求加权平均；
          2. 将该指标平均分换算为得分率 score / max_score（0~1）；
          3. 以指标权重 weight 对各指标得分率做加权平均；
          4. 乘以 100 得到最终得分。该口径与权重是否合计为 100 无关。

        Args:
            db: 数据库会话。
            achievement_id: 实训成果ID。
            type_weights: 各 eval_type 的权重，默认等权。

        Returns:
            回填后的最终得分；若无有效评价则返回 None（final_score 置空）。
        """
        achievement = db.get(TrainAchievement, achievement_id)
        if not achievement or achievement.is_deleted == 1:
            return None

        weights = type_weights or DEFAULT_TYPE_WEIGHTS
        results = self.list_by_achievement(db, achievement_id)

        # 按指标聚合：indicator_id -> [(score, type_weight), ...]
        grouped: dict[int, list[tuple[Decimal, Decimal]]] = {}
        for r in results:
            tw = weights.get(r.eval_type, Decimal("1"))
            if tw <= 0:
                continue
            grouped.setdefault(r.indicator_id, []).append((Decimal(r.score), tw))

        if not grouped:
            achievement.final_score = None
            db.add(achievement)
            db.commit()
            return None

        # 加载相关指标
        indicators = db.scalars(
            select(EvalIndicator).where(
                EvalIndicator.id.in_(grouped.keys()),
                EvalIndicator.is_deleted == 0,
            )
        ).all()
        indicator_map = {i.id: i for i in indicators}

        weighted_ratio_sum = Decimal("0")  # Σ(得分率 × 指标权重)
        indicator_weight_sum = Decimal("0")  # Σ(指标权重)

        for indicator_id, items in grouped.items():
            indicator = indicator_map.get(indicator_id)
            if not indicator or Decimal(indicator.max_score) <= 0:
                continue

            # 该指标的评分按 eval_type 加权平均
            tw_sum = sum((w for _, w in items), Decimal("0"))
            if tw_sum <= 0:
                continue
            avg_score = sum((s * w for s, w in items), Decimal("0")) / tw_sum

            ratio = avg_score / Decimal(indicator.max_score)  # 0~1
            ind_weight = Decimal(indicator.weight) or Decimal("1")  # 权重为0时退化为等权

            weighted_ratio_sum += ratio * ind_weight
            indicator_weight_sum += ind_weight

        if indicator_weight_sum <= 0:
            achievement.final_score = None
            db.add(achievement)
            db.commit()
            return None

        final = (weighted_ratio_sum / indicator_weight_sum) * Decimal("100")
        final = final.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        achievement.final_score = final
        db.add(achievement)
        db.commit()
        db.refresh(achievement)
        return final


eval_result_service = EvalResultService()
