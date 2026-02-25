"""Mixin for observer-related database operations.

Handles observer cruise tracking and observer thought/scenario fields.
Observer functionality is currently embedded in TaskV2, Thought, and Artifact
methods via fields like observer_cruise_id, observer_thought_id,
observer_thought_type, and observer_thought_scenario.
Accesses shared state via the AgentDB instance (self.Session(), self.debug_enabled).

Methods to be migrated here:
    (Observer-specific queries will be extracted from TaskV2/Thought/Artifact
    methods in future phases as the observer domain is decoupled.)
"""


class ObserverMixin:
    """Mixin for observer-related database operations.

    Handles observer cruise tracking and observer thought/scenario fields.
    """
