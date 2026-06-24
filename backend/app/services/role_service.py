"""角色业务逻辑。"""
from app.models.role import Role
from app.services.base import CRUDBase


class RoleService(CRUDBase[Role]):
    def __init__(self) -> None:
        super().__init__(Role)


role_service = RoleService()
