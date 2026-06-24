"""评价结果路由。"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.exceptions import BusinessException
from app.core.response import success
from app.schemas.auth import CurrentUser
from app.schemas.eval_result import EvalResultCreate, EvalResultOut, EvalResultUpdate
from app.services.eval_result_service import eval_result_service
from app.utils.enums import RoleCode

router = APIRouter(prefix="/eval-results", tags=["评价结果"])

# 可录入评价的角色：教师、企业导师、管理员（AI 评价由服务内部写入）
_EVALUATOR_ROLES = (RoleCode.TEACHER, RoleCode.ENTERPRISE, RoleCode.ADMIN)


@router.post("", summary="录入评价（教师/企业导师/管理员）",
             dependencies=[Depends(require_roles(*_EVALUATOR_ROLES))])
def create_eval_result(
    payload: EvalResultCreate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(*_EVALUATOR_ROLES)),
):
    data = payload.model_dump()
    if data.get("evaluator_id") is None:
        data["evaluator_id"] = current.user_id
    data["eval_time"] = datetime.now(timezone.utc)
    obj = eval_result_service.create(db, data)
    # 录入后实时汇总加权得分并回填成果 final_score
    final = eval_result_service.recalc_final_score(db, obj.achievement_id)
    return success(
        data={**EvalResultOut.model_validate(obj).model_dump(), "final_score": final},
        msg="评价成功",
    )


@router.get("", summary="评价结果列表（按成果过滤）",
            dependencies=[Depends(get_current_user)])
def list_eval_results(
    achievement_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    filters = {"achievement_id": achievement_id} if achievement_id is not None else {}
    items = eval_result_service.list(
        db, offset=(page - 1) * page_size, limit=page_size, **filters
    )
    return success(data={
        "total": eval_result_service.count(db, **filters),
        "page": page,
        "page_size": page_size,
        "items": [EvalResultOut.model_validate(r).model_dump() for r in items],
    })


@router.put("/{result_id}", summary="修订评价（教师/企业导师/管理员）",
            dependencies=[Depends(require_roles(*_EVALUATOR_ROLES))])
def update_eval_result(
    result_id: int, payload: EvalResultUpdate, db: Session = Depends(get_db)
):
    obj = eval_result_service.get(db, result_id)
    if not obj:
        raise BusinessException("评价结果不存在", code=404)
    obj = eval_result_service.update(db, obj, payload.model_dump(exclude_unset=True))
    final = eval_result_service.recalc_final_score(db, obj.achievement_id)
    return success(
        data={**EvalResultOut.model_validate(obj).model_dump(), "final_score": final},
        msg="更新成功",
    )


@router.delete("/{result_id}", summary="删除评价（管理员）",
               dependencies=[Depends(require_roles(RoleCode.ADMIN))])
def delete_eval_result(result_id: int, db: Session = Depends(get_db)):
    obj = eval_result_service.get(db, result_id)
    if not obj:
        raise BusinessException("评价结果不存在", code=404)
    achievement_id = obj.achievement_id
    eval_result_service.remove(db, result_id)
    # 删除后重新汇总，保证 final_score 与剩余评价一致
    eval_result_service.recalc_final_score(db, achievement_id)
    return success(msg="删除成功")


@router.post("/recalc/{achievement_id}", summary="重新汇总成果得分（教师/企业导师/管理员）",
             dependencies=[Depends(require_roles(*_EVALUATOR_ROLES))])
def recalc_final_score(achievement_id: int, db: Session = Depends(get_db)):
    final = eval_result_service.recalc_final_score(db, achievement_id)
    return success(data={"achievement_id": achievement_id, "final_score": final},
                   msg="汇总完成")
