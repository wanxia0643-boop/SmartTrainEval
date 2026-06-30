"""Schemas for AI-assisted achievement review."""
from pydantic import BaseModel, Field


class AIReviewRequest(BaseModel):
    training_requirement: str | None = Field(default=None, description="Training requirement")
    student_content: str | None = Field(default=None, description="Submitted content")
    achievement_id: int | None = Field(default=None, description="Related achievement ID")


class FunctionCheck(BaseModel):
    is_complete: bool = Field(description="Whether all required functions are complete")
    problem_list: list[str] = Field(default_factory=list, description="Missing/problem points")


class LogicCheck(BaseModel):
    has_risk: bool = Field(description="Whether logic risks are found")
    risk_list: list[str] = Field(default_factory=list, description="Logic risks")


class StepCheck(BaseModel):
    is_complete: bool = Field(description="Whether implementation steps are complete")
    missing_steps: list[str] = Field(default_factory=list, description="Missing steps")


class ReviewResult(BaseModel):
    function_check: FunctionCheck
    logic_check: LogicCheck
    step_check: StepCheck
    standard_score: int = Field(ge=0, le=100, description="Standard score")
    standard_suggestion: str = Field(description="Improvement suggestion")
    summary: str = Field(description="Overall summary")
