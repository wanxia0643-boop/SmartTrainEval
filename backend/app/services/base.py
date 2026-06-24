"""通用 CRUD 封装：支持逻辑删除、分页，供各业务 service 复用。"""
from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    """基础 CRUD 操作。

    约定：所有查询默认过滤 is_deleted == 0；删除为逻辑删除。
    """

    def __init__(self, model: type[ModelType]):
        self.model = model

    def get(self, db: Session, obj_id: int) -> ModelType | None:
        """按主键查询（未删除）。"""
        stmt = select(self.model).where(
            self.model.id == obj_id, self.model.is_deleted == 0
        )
        return db.scalars(stmt).first()

    def get_by(self, db: Session, **filters: Any) -> ModelType | None:
        """按等值条件查询单条（未删除）。"""
        stmt = select(self.model).where(self.model.is_deleted == 0)
        for field, value in filters.items():
            stmt = stmt.where(getattr(self.model, field) == value)
        return db.scalars(stmt).first()

    def list(
        self, db: Session, *, offset: int = 0, limit: int = 10, **filters: Any
    ) -> list[ModelType]:
        """分页列表查询（未删除）。"""
        stmt = select(self.model).where(self.model.is_deleted == 0)
        for field, value in filters.items():
            stmt = stmt.where(getattr(self.model, field) == value)
        stmt = stmt.order_by(self.model.id.desc()).offset(offset).limit(limit)
        return list(db.scalars(stmt).all())

    def count(self, db: Session, **filters: Any) -> int:
        """统计条数（未删除）。"""
        stmt = select(func.count()).select_from(self.model).where(
            self.model.is_deleted == 0
        )
        for field, value in filters.items():
            stmt = stmt.where(getattr(self.model, field) == value)
        return db.scalar(stmt) or 0

    def create(self, db: Session, data: dict[str, Any]) -> ModelType:
        """新增。"""
        obj = self.model(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(
        self, db: Session, obj: ModelType, data: dict[str, Any]
    ) -> ModelType:
        """更新（仅更新传入的非 None 字段）。"""
        for field, value in data.items():
            if value is not None and hasattr(obj, field):
                setattr(obj, field, value)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def remove(self, db: Session, obj_id: int) -> bool:
        """逻辑删除。"""
        obj = self.get(db, obj_id)
        if not obj:
            return False
        obj.is_deleted = 1
        db.add(obj)
        db.commit()
        return True
