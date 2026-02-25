"""Mixin for organization-related database operations.

Handles Organization CRUD and auth token management.
Accesses shared state via the AgentDB instance (self.Session(), self.debug_enabled).

Methods to be migrated here:
    - get_all_organizations
    - get_organization
    - get_organization_by_domain
    - create_organization
    - update_organization
    - get_valid_org_auth_token (overloads)
    - get_valid_org_auth_tokens
    - validate_org_auth_token
    - create_org_auth_token
    - invalidate_org_auth_tokens
"""


class OrganizationMixin:
    """Mixin for organization-related database operations.

    Handles Organization CRUD and auth token management.
    """
