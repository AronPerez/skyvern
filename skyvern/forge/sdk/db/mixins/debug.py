"""Mixin for debug-session-related database operations.

Handles debug sessions and block runs.
Accesses shared state via the AgentDB instance (self.Session(), self.debug_enabled).

Methods to be migrated here:
    - get_debug_session
    - get_latest_block_run
    - get_latest_completed_block_run
    - create_block_run
    - get_latest_debug_session_for_user
    - get_debug_session_by_id
    - get_debug_session_by_browser_session_id
    - get_workflow_runs_by_debug_session_id
    - complete_debug_sessions
    - create_debug_session
"""


class DebugMixin:
    """Mixin for debug-session-related database operations.

    Handles debug sessions and block runs.
    """
