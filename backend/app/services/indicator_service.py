"""评价指标业务逻辑。"""
from app.models.indicator import EvalIndicator
from app.services.base import CRUDBase


class IndicatorService(CRUDBase[EvalIndicator]):
    def __init__(self) -> None:
        super().__init__(EvalIndicator)


indicator_service = IndicatorService()
