"""大模型调用日志业务逻辑。"""
from app.models.llm_log import LlmCallLog
from app.services.base import CRUDBase


class LlmLogService(CRUDBase[LlmCallLog]):
    def __init__(self) -> None:
        super().__init__(LlmCallLog)


llm_log_service = LlmLogService()
