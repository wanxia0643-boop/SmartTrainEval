from pydantic import BaseModel, Field

from app.schemas.knowledge import Citation


class CoachRequest(BaseModel):
    course_id: int
    project_id: int | None = None
    session_id: int | None = None
    message: str = Field(min_length=1, max_length=4000)


class ProjectDraftRequest(BaseModel):
    course_id: int
    objective: str = Field(min_length=2, max_length=2000)
    difficulty: int = Field(default=2, ge=1, le=3)
    duration_days: int = Field(default=14, ge=1, le=180)


class CoachResponse(BaseModel):
    session_id: int
    answer: str
    hints: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    available: bool = True

