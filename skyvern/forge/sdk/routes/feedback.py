from typing import Annotated

from fastapi import Depends, Header, Path

from skyvern import analytics
from skyvern.forge.sdk.routes.routers import base_router
from skyvern.forge.sdk.schemas.feedback import RunFeedbackRequest, RunFeedbackResponse
from skyvern.forge.sdk.schemas.organizations import Organization
from skyvern.forge.sdk.services import org_auth_service
from skyvern.services import feedback_service


@base_router.post(
    "/runs/{run_id}/feedback",
    tags=["Agent", "Feedback"],
    response_model=RunFeedbackResponse,
    description="Submit feedback for a run (thumbs up/down with optional categories and comments)",
    summary="Submit run feedback",
    openapi_extra={
        "x-fern-sdk-method-name": "submit_run_feedback",
    },
    responses={
        200: {"description": "Feedback submitted successfully"},
        404: {"description": "Run not found"},
        409: {"description": "Feedback already exists for this run"},
    },
)
@base_router.post("/runs/{run_id}/feedback/", include_in_schema=False)
async def submit_run_feedback(
    request: RunFeedbackRequest,
    run_id: str = Path(..., description="The id of the task run or the workflow run."),
    current_org: Organization = Depends(org_auth_service.get_current_org),
    x_api_key: Annotated[str | None, Header()] = None,
) -> RunFeedbackResponse:
    analytics.capture("skyvern-oss-agent-submit-run-feedback")

    return await feedback_service.submit_run_feedback(
        run_id=run_id,
        request=request,
        organization_id=current_org.organization_id,
        user_id=None,  # User ID not available in current auth flow
    )


@base_router.get(
    "/runs/{run_id}/feedback",
    tags=["Agent", "Feedback"],
    response_model=RunFeedbackResponse | None,
    description="Get feedback for a run",
    summary="Get run feedback",
    openapi_extra={
        "x-fern-sdk-method-name": "get_run_feedback",
    },
    responses={
        200: {"description": "Feedback retrieved successfully (or null if no feedback exists)"},
    },
)
@base_router.get("/runs/{run_id}/feedback/", include_in_schema=False)
async def get_run_feedback(
    run_id: str = Path(..., description="The id of the task run or the workflow run."),
    current_org: Organization = Depends(org_auth_service.get_current_org),
) -> RunFeedbackResponse | None:
    analytics.capture("skyvern-oss-agent-get-run-feedback")

    return await feedback_service.get_run_feedback(
        run_id=run_id,
        organization_id=current_org.organization_id,
    )


@base_router.put(
    "/runs/{run_id}/feedback",
    tags=["Agent", "Feedback"],
    response_model=RunFeedbackResponse,
    description="Update feedback for a run",
    summary="Update run feedback",
    openapi_extra={
        "x-fern-sdk-method-name": "update_run_feedback",
    },
    responses={
        200: {"description": "Feedback updated successfully"},
        404: {"description": "Feedback not found for this run"},
    },
)
@base_router.put("/runs/{run_id}/feedback/", include_in_schema=False)
async def update_run_feedback(
    request: RunFeedbackRequest,
    run_id: str = Path(..., description="The id of the task run or the workflow run."),
    current_org: Organization = Depends(org_auth_service.get_current_org),
) -> RunFeedbackResponse:
    analytics.capture("skyvern-oss-agent-update-run-feedback")

    return await feedback_service.update_run_feedback(
        run_id=run_id,
        request=request,
        organization_id=current_org.organization_id,
    )
