from pydantic import BaseModel, Field, model_validator

from app.schemas.knowledge import Citation


class CoachRequest(BaseModel):
    course_id: int
    project_id: int | None = None
    achievement_id: int | None = None
    session_id: int | None = None
    message: str = Field(min_length=1, max_length=4000)


class ProjectDraftRequest(BaseModel):
    course_id: int
    objective: str = Field(min_length=2, max_length=2000)
    difficulty: int = Field(default=2, ge=1, le=3)
    duration_days: int = Field(default=14, ge=1, le=180)


class ProjectDraftIndicator(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    weight: int = Field(ge=1, le=100)
    rule: str = Field(min_length=1, max_length=1000)


class ProjectDraftApplyRequest(BaseModel):
    analysis_id: int
    course_id: int
    project_name: str = Field(min_length=2, max_length=150)
    project_code: str = Field(min_length=2, max_length=64)
    category: str | None = Field(default="软件开发", max_length=50)
    difficulty: int = Field(default=2, ge=1, le=3)
    duration_days: int = Field(default=14, ge=1, le=180)
    description: str = Field(min_length=2, max_length=5000)
    milestones: list[str] = Field(min_length=1, max_length=12)
    submission_requirements: list[str] = Field(min_length=1, max_length=12)
    indicators: list[ProjectDraftIndicator] = Field(min_length=1, max_length=12)

    @model_validator(mode="after")
    def validate_draft(self):
        if sum(item.weight for item in self.indicators) != 100:
            raise ValueError("评价指标权重合计必须为 100")
        if any(not item.strip() for item in self.milestones + self.submission_requirements):
            raise ValueError("里程碑和提交要求不能为空")
        return self


class CoachResponse(BaseModel):
    session_id: int
    answer: str
    hints: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    available: bool = True
