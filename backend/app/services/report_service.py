"""报表记录业务逻辑。"""
from app.models.report import ReportRecord
from app.services.base import CRUDBase


class ReportService(CRUDBase[ReportRecord]):
    def __init__(self) -> None:
        super().__init__(ReportRecord)


report_service = ReportService()
