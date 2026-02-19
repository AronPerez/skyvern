from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class FeedbackValue(StrEnum):
    """Feedback value enum - thumbs up or thumbs down."""

    thumbs_up = "thumbs_up"
    thumbs_down = "thumbs_down"


class FeedbackCategory(StrEnum):
    """Feedback categories for thumbs down feedback."""

    wrong_element = "wrong_element"
    missed_step = "missed_step"
    wrong_data = "wrong_data"
    got_stuck = "got_stuck"
    wrong_page = "wrong_page"
    partial_completion = "partial_completion"
    captcha_issue = "captcha_issue"
    login_issue = "login_issue"
    other = "other"


class RunFeedbackRequest(BaseModel):
    """Request schema for submitting run feedback."""

    feedback_value: FeedbackValue = Field(
        ...,
        description="The feedback value - either 'thumbs_up' or 'thumbs_down'",
    )
    categories: list[FeedbackCategory] | None = Field(
        default=None,
        description="Categories for thumbs down feedback (optional for thumbs up)",
    )
    comment: str | None = Field(
        default=None,
        description="Optional free-text comment with additional feedback",
        max_length=2000,
    )


class RunFeedbackResponse(BaseModel):
    """Response schema for run feedback."""

    model_config = ConfigDict(from_attributes=True)

    feedback_id: str = Field(
        ...,
        description="Unique identifier for the feedback",
    )
    organization_id: str = Field(
        ...,
        description="Organization that owns this feedback",
    )
    workflow_run_id: str | None = Field(
        default=None,
        description="Associated workflow run ID (if feedback is for a workflow run)",
    )
    task_id: str | None = Field(
        default=None,
        description="Associated task ID (if feedback is for a task)",
    )
    feedback_value: int = Field(
        ...,
        description="The feedback value: 1 = thumbs up, -1 = thumbs down",
    )
    categories: list[str] | None = Field(
        default=None,
        description="Categories selected for thumbs down feedback",
    )
    comment: str | None = Field(
        default=None,
        description="Optional free-text comment",
    )
    created_by_user_id: str | None = Field(
        default=None,
        description="User ID who submitted the feedback",
    )
    created_at: datetime = Field(
        ...,
        description="When the feedback was created",
    )
    modified_at: datetime = Field(
        ...,
        description="When the feedback was last modified",
    )

    @property
    def feedback_value_enum(self) -> FeedbackValue:
        """Convert numeric feedback value to enum."""
        return FeedbackValue.thumbs_up if self.feedback_value == 1 else FeedbackValue.thumbs_down
