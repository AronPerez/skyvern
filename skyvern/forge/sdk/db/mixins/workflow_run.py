"""Mixin for workflow-run-related database operations.

Handles workflow run lifecycle, run parameters, run output parameters, and run blocks.
Accesses shared state via the AgentDB instance (self.Session(), self.debug_enabled).

Methods to be migrated here:
    - get_running_workflow_runs_info_globally
    - create_workflow_run
    - update_workflow_run
    - bulk_update_workflow_runs
    - clear_workflow_run_failure_reason
    - get_all_runs
    - get_workflow_run
    - get_last_queued_workflow_run
    - get_workflow_runs_by_ids
    - get_last_running_workflow_run
    - get_last_workflow_run_for_browser_session
    - _apply_search_key_filter
    - _apply_error_code_filter
    - get_workflow_runs
    - get_workflow_runs_count
    - get_workflow_runs_for_workflow_permanent_id
    - get_workflow_runs_by_parent_workflow_run_id
    - get_workflow_run_output_parameters
    - get_workflow_run_output_parameter_by_id
    - create_or_update_workflow_run_output_parameter
    - update_workflow_run_output_parameter
    - create_workflow_run_parameter
    - get_workflow_run_parameters
    - create_workflow_run_block
    - delete_workflow_run_blocks
    - update_workflow_run_block
    - get_workflow_run_block
    - get_workflow_run_block_by_task_id
    - get_workflow_run_blocks
"""


class WorkflowRunMixin:
    """Mixin for workflow-run-related database operations.

    Handles workflow run lifecycle, run parameters, run output parameters, and run blocks.
    """
