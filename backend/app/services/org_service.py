"""组织业务逻辑。"""
from app.models.org import Org
from app.services.base import CRUDBase


class OrgService(CRUDBase[Org]):
    def __init__(self) -> None:
        super().__init__(Org)


org_service = OrgService()
