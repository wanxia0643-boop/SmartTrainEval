"""AI 智能核查 schema：请求与结构化结果。"""
from pydantic import BaseModel, Field


class AIReviewRequest(BaseModel):
    """智能核查请求。"""

    training_requirement: str = Field(..., description="实训要求")
    student_content: str = Field(..., description="学生提交的代码/文档内容")
    achievement_id: int | None = Field(default=None, description="关联成果ID（用于日志追溯）")


class FunctionCheck(BaseModel):
    """功能实现校验。"""

    is_complete: bool = Field(description="是否完成所有要求功能")
    problem_list: list[str] = Field(default_factory=list, description="未完成/问题功能点")


class LogicCheck(BaseModel):
    """逻辑漏洞识别。"""

    has_risk: bool = Field(description="是否存在逻辑风险")
    risk_list: list[str] = Field(default_factory=list, description="逻辑错误/异常缺失/潜在bug")


class StepCheck(BaseModel):
    """步骤完整性。"""

    is_complete: bool = Field(description="开发步骤是否全部完成")
    missing_steps: list[str] = Field(default_factory=list, description="缺失步骤")


class ReviewResult(BaseModel):
    """智能核查结构化结果（与提示词约定的 JSON 一一对应）。"""

    function_check: FunctionCheck
    logic_check: LogicCheck
    step_check: StepCheck
    standard_score: int = Field(ge=0, le=100, description="代码/文档规范得分（0-100）")
    standard_suggestion: str = Field(description="规范优化建议")
    summary: str = Field(description="整体核查总结")
