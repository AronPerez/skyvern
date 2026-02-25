"""Mixin for folder-related database operations.

Handles folder organization for workflows.
Accesses shared state via the AgentDB instance (self.Session(), self.debug_enabled).

Methods to be migrated here:
    - create_folder
    - get_folders
    - get_folder
    - update_folder
    - get_workflow_permanent_ids_in_folder
    - soft_delete_folder
    - get_folder_workflow_count
    - get_folder_workflow_counts_batch
    - update_workflow_folder
"""


class FolderMixin:
    """Mixin for folder-related database operations.

    Handles folder organization for workflows.
    """
