from fastapi import HTTPException, status

from skyvern.forge import app
from skyvern.forge.sdk.db.models import RunFeedbackModel
from skyvern.forge.sdk.schemas.feedback import FeedbackValue, RunFeedbackRequest, RunFeedbackResponse


def _feedback_value_to_int(feedback_value: FeedbackValue) -> int:
    """Convert FeedbackValue enum to integer for database storage."""
    return 1 if feedback_value == FeedbackValue.thumbs_up else -1


def _model_to_response(model: RunFeedbackModel) -> RunFeedbackResponse:
    """Convert RunFeedbackModel to RunFeedbackResponse."""
    return RunFeedbackResponse(
        feedback_id=model.feedback_id,
        organization_id=model.organization_id,
        workflow_run_id=model.workflow_run_id,
        task_id=model.task_id,
        feedback_value=model.feedback_value,
        categories=model.categories,
        comment=model.comment,
        created_by_user_id=model.created_by_user_id,
        created_at=model.created_at,
        modified_at=model.modified_at,
    )


async def submit_run_feedback(
    run_id: str,
    request: RunFeedbackRequest,
    organization_id: str,
    user_id: str | None = None,
) -> RunFeedbackResponse:
    """
    Submit feedback for a run.

    This function determines whether the run_id is a workflow_run_id or task_id
    and creates the appropriate feedback entry.
    """
    # Determine run type by checking if it's a workflow run or task
    workflow_run = await app.DATABASE.get_workflow_run(
        workflow_run_id=run_id,
        organization_id=organization_id,
    )

    task = None
    if not workflow_run:
        task = await app.DATABASE.get_task(run_id, organization_id=organization_id)

    if not workflow_run and not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run not found: {run_id}",
        )

    # Check if feedback already exists for this run
    existing_feedback = None
    if workflow_run:
        existing_feedback = await app.DATABASE.get_run_feedback_by_workflow_run_id(
            workflow_run_id=run_id,
            organization_id=organization_id,
        )
    else:
        existing_feedback = await app.DATABASE.get_run_feedback_by_task_id(
            task_id=run_id,
            organization_id=organization_id,
        )

    if existing_feedback:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Feedback already exists for this run. Use PUT to update.",
        )

    # Convert request to database format
    feedback_value_int = _feedback_value_to_int(request.feedback_value)
    categories = [cat.value for cat in request.categories] if request.categories else None

    # Create feedback
    feedback = await app.DATABASE.create_run_feedback(
        organization_id=organization_id,
        feedback_value=feedback_value_int,
        workflow_run_id=run_id if workflow_run else None,
        task_id=run_id if task else None,
        categories=categories,
        comment=request.comment,
        created_by_user_id=user_id,
    )

    return _model_to_response(feedback)


async def get_run_feedback(
    run_id: str,
    organization_id: str,
) -> RunFeedbackResponse | None:
    """
    Get feedback for a run.

    This function determines whether the run_id is a workflow_run_id or task_id
    and retrieves the appropriate feedback entry.
    """
    # Try to get feedback by workflow_run_id first
    feedback = await app.DATABASE.get_run_feedback_by_workflow_run_id(
        workflow_run_id=run_id,
        organization_id=organization_id,
    )

    # If not found, try to get by task_id
    if not feedback:
        feedback = await app.DATABASE.get_run_feedback_by_task_id(
            task_id=run_id,
            organization_id=organization_id,
        )

    if not feedback:
        return None

    return _model_to_response(feedback)


async def update_run_feedback(
    run_id: str,
    request: RunFeedbackRequest,
    organization_id: str,
) -> RunFeedbackResponse:
    """
    Update feedback for a run.

    This function finds the existing feedback and updates it.
    """
    # Get existing feedback
    existing_feedback = await app.DATABASE.get_run_feedback_by_workflow_run_id(
        workflow_run_id=run_id,
        organization_id=organization_id,
    )

    if not existing_feedback:
        existing_feedback = await app.DATABASE.get_run_feedback_by_task_id(
            task_id=run_id,
            organization_id=organization_id,
        )

    if not existing_feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback not found for run: {run_id}",
        )

    # Convert request to database format
    feedback_value_int = _feedback_value_to_int(request.feedback_value)
    categories = [cat.value for cat in request.categories] if request.categories else None

    # Update feedback
    updated_feedback = await app.DATABASE.update_run_feedback(
        feedback_id=existing_feedback.feedback_id,
        organization_id=organization_id,
        feedback_value=feedback_value_int,
        categories=categories,
        comment=request.comment,
    )

    if not updated_feedback:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update feedback",
        )

    return _model_to_response(updated_feedback)
