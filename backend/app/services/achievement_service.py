"""实训成果业务逻辑。"""
from app.models.achievement import TrainAchievement
from app.services.base import CRUDBase


class AchievementService(CRUDBase[TrainAchievement]):
    def __init__(self) -> None:
        super().__init__(TrainAchievement)


achievement_service = AchievementService()
