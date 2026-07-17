"""评价结果业务逻辑。"""
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.achievement import TrainAchievement
from app.models.eval_result import EvalResult
from app.models.indicator import EvalIndicator
from app.models.project import TrainProject
from app.services.base import CRUDBase

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
    ) -> Decimal | None:
        """汇总教师与企业评价；AI和自评不计分，缺少必需评价时保持评价中。"""
        achievement = db.get(TrainAchievement, achievement_id)
        if not achievement or achievement.is_deleted == 1:
            return None

        project = db.get(TrainProject, achievement.project_id)
        if not project or project.is_deleted == 1:
            return None
        indicators = list(db.scalars(select(EvalIndicator).where(
            EvalIndicator.project_id == project.id,
            EvalIndicator.status == 1,
            EvalIndicator.is_deleted == 0,
        )).all())
        results = [r for r in self.list_by_achievement(db, achievement_id) if r.eval_type in (2, 3)]
        if not indicators or not results:
            achievement.final_score = None
            achievement.status = 2 if results else 1
            db.add(achievement)
            db.commit()
            return None

        required_types = [2, 3] if project.enterprise_id else [2]
        indicator_ids = {item.id for item in indicators}
        for eval_type in required_types:
            covered = {r.indicator_id for r in results if r.eval_type == eval_type}
            if not indicator_ids.issubset(covered):
                achievement.final_score = None
                achievement.status = 2
                db.add(achievement)
                db.commit()
                return None

        def role_score(eval_type: int) -> Decimal:
            weighted = Decimal("0")
            weight_sum = Decimal("0")
            for indicator in indicators:
                values = [Decimal(r.score) for r in results if r.eval_type == eval_type and r.indicator_id == indicator.id]
                if not values or Decimal(indicator.max_score) <= 0:
                    continue
                avg = sum(values, Decimal("0")) / Decimal(len(values))
                weight = Decimal(indicator.weight) or Decimal("1")
                weighted += (avg / Decimal(indicator.max_score)) * weight
                weight_sum += weight
            return (weighted / weight_sum) * Decimal("100") if weight_sum else Decimal("0")

        teacher_score = role_score(2)
        if project.enterprise_id:
            final = teacher_score * Decimal("0.6") + role_score(3) * Decimal("0.4")
        else:
            final = teacher_score
        if final < 0:
            final = Decimal("0")
        if final > 100:
            final = Decimal("100")
        if final.is_nan():
            achievement.final_score = None
            db.add(achievement)
            db.commit()
            return None
        final = final.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        achievement.final_score = final
        achievement.status = 3
        db.add(achievement)
        db.commit()
        db.refresh(achievement)
        return final

    def is_role_complete(self, db: Session, achievement_id: int, eval_type: int) -> bool:
        achievement = db.get(TrainAchievement, achievement_id)
        if not achievement:
            return False
        required = set(db.scalars(select(EvalIndicator.id).where(
            EvalIndicator.project_id == achievement.project_id,
            EvalIndicator.status == 1,
            EvalIndicator.is_deleted == 0,
        )).all())
        covered = set(db.scalars(select(EvalResult.indicator_id).where(
            EvalResult.achievement_id == achievement_id,
            EvalResult.eval_type == eval_type,
            EvalResult.is_deleted == 0,
        )).all())
        return bool(required) and required.issubset(covered)


eval_result_service = EvalResultService()
