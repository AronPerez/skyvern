"""Mixin for task-related database operations.

Handles Task, Step, Action, TaskV2, Thought, and Run CRUD operations.
Accesses shared state via the AgentDB instance (self.Session(), self.debug_enabled).

Methods to be migrated here:
    - create_task
    - create_step
    - get_task
    - get_tasks_by_ids
    - get_step
    - get_task_steps
    - get_steps_by_task_ids
    - get_total_unique_step_order_count_by_task_ids
    - get_task_step_models
    - get_task_step_count
    - get_task_actions
    - get_task_actions_hydrated
    - get_tasks_actions
    - get_action_count_for_step
    - get_first_step
    - get_latest_step
    - update_step
    - clear_task_failure_reason
    - update_task
    - update_task_2fa_state
    - get_active_verification_requests
    - bulk_update_tasks
    - get_tasks
    - get_tasks_count
    - get_running_tasks_info_globally
    - get_latest_task_by_workflow_id
    - get_last_task_for_workflow_run
    - get_tasks_by_workflow_run_id
    - delete_task_artifacts
    - delete_task_steps
    - create_task_generation
    - create_ai_suggestion
    - get_task_generation_by_prompt_hash
    - create_action
    - update_action_screenshot_artifact_id
    - update_action_reasoning
    - retrieve_action_plan
    - get_previous_actions_for_task
    - delete_task_actions
    - get_task_v2
    - get_task_v2_by_workflow_run_id
    - create_task_v2
    - update_task_v2
    - delete_task_v2_artifacts
    - delete_thoughts
    - get_thought
    - get_thoughts
    - create_thought
    - update_thought
    - create_task_run
    - update_task_run
    - update_job_run_compute_cost
    - cache_task_run
    - get_cached_task_run
    - get_run
"""


class TaskMixin:
    """Mixin for task-related database operations.

    Handles Task, Step, Action, TaskV2, Thought, and Run CRUD.
    """
