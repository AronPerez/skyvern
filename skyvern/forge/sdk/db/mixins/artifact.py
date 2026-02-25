"""Mixin for artifact-related database operations.

Handles artifact storage, retrieval, and bulk operations.
Accesses shared state via the AgentDB instance (self.Session(), self.debug_enabled).

Methods to be migrated here:
    - create_artifact
    - bulk_create_artifacts
    - get_artifacts_for_task_v2
    - get_artifacts_for_task_step
    - get_artifacts_for_run
    - get_artifact_by_id
    - get_artifacts_by_ids
    - get_artifacts_by_entity_id
    - get_artifact_by_entity_id
    - get_artifact
    - get_artifact_for_run
    - get_latest_artifact
    - get_latest_n_artifacts
"""


class ArtifactMixin:
    """Mixin for artifact-related database operations.

    Handles artifact storage, retrieval, and bulk operations.
    """
