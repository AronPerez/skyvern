"""Mixin for browser-session-related database operations.

Handles persistent browser sessions and browser profiles.
Accesses shared state via the AgentDB instance (self.Session(), self.debug_enabled).

Methods to be migrated here:
    - create_browser_profile
    - get_browser_profile
    - list_browser_profiles
    - delete_browser_profile
    - get_active_persistent_browser_sessions
    - get_persistent_browser_sessions_history
    - get_persistent_browser_session_by_runnable_id
    - get_persistent_browser_session
    - create_persistent_browser_session
    - update_persistent_browser_session
    - set_persistent_browser_session_browser_address
    - update_persistent_browser_session_compute_cost
    - mark_persistent_browser_session_deleted
    - occupy_persistent_browser_session
    - release_persistent_browser_session
    - close_persistent_browser_session
    - get_all_active_persistent_browser_sessions
"""


class BrowserSessionMixin:
    """Mixin for browser-session-related database operations.

    Handles persistent browser sessions and browser profiles.
    """
