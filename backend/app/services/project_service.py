"""实训项目业务逻辑。"""
from app.models.project import TrainProject
from app.services.base import CRUDBase


class ProjectService(CRUDBase[TrainProject]):
    def __init__(self) -> None:
        super().__init__(TrainProject)


project_service = ProjectService()
