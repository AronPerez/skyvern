"""Mixin for workflow-related database operations.

Handles Workflow CRUD, templates, parameters, output parameters, and copilot chat.
Accesses shared state via the AgentDB instance (self.Session(), self.debug_enabled).

Methods to be migrated here:
    - create_workflow
    - soft_delete_workflow_by_id
    - get_workflow
    - get_workflow_by_permanent_id
    - get_workflow_for_workflow_run
    - get_workflow_versions_by_permanent_id
    - get_workflows_by_permanent_ids
    - get_workflows_by_organization_id
    - update_workflow
    - soft_delete_workflow_by_permanent_id
    - add_workflow_template
    - remove_workflow_template
    - get_org_template_permanent_ids
    - is_workflow_template
    - get_workflows_depending_on
    - create_workflow_parameter
    - create_aws_secret_parameter
    - create_output_parameter
    - _convert_parameter_to_model
    - save_workflow_definition_parameters
    - get_workflow_output_parameters
    - get_workflow_output_parameters_by_ids
    - get_workflow_parameters
    - get_workflow_parameter
    - create_workflow_copilot_chat
    - update_workflow_copilot_chat
    - create_workflow_copilot_chat_message
    - get_workflow_copilot_chat_messages
    - get_workflow_copilot_chat_by_id
    - get_latest_workflow_copilot_chat
"""


class WorkflowMixin:
    """Mixin for workflow-related database operations.

    Handles Workflow CRUD, templates, parameters, output parameters, and copilot chat.
    """
