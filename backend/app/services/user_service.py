"""用户业务逻辑。"""
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.base import CRUDBase


class UserService(CRUDBase[User]):
    """用户服务，复用 CRUDBase 并补充业务规则。"""

    def __init__(self) -> None:
        super().__init__(User)

    def get_by_username(self, db: Session, username: str) -> User | None:
        return self.get_by(db, username=username)

    def create_user(self, db: Session, payload: UserCreate) -> User:
        if self.get_by_username(db, payload.username):
            raise BusinessException("用户名已存在", code=409)
        data = payload.model_dump()
        data["password"] = hash_password(data.pop("password"))
        return self.create(db, data)

    def update_user(self, db: Session, user_id: int, payload: UserUpdate) -> User:
        obj = self.get(db, user_id)
        if not obj:
            raise BusinessException("用户不存在", code=404)
        return self.update(db, obj, payload.model_dump(exclude_unset=True))


user_service = UserService()
