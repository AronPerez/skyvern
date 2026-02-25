"""Mixin for script-related database operations.

Handles script, script file, script block, and workflow script management.
Accesses shared state via the AgentDB instance (self.Session(), self.debug_enabled).

Methods to be migrated here:
    - create_script
    - get_scripts
    - get_script
    - get_script_revision
    - create_script_file
    - create_script_block
    - update_script_block
    - get_script_files
    - get_script_file_by_id
    - get_script_file_by_path
    - update_script_file
    - get_script_block
    - get_script_block_by_label
    - get_script_blocks_by_script_revision_id
    - create_workflow_script
    - get_workflow_script
    - get_workflow_script_by_cache_key_value
    - get_workflow_cache_key_count
    - get_workflow_cache_key_values
    - delete_workflow_cache_key_value
    - delete_workflow_scripts_by_permanent_id
    - get_workflow_scripts_by_permanent_id
"""


class ScriptMixin:
    """Mixin for script-related database operations.

    Handles script, script file, script block, and workflow script management.
    """
