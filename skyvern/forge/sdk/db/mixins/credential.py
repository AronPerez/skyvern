"""Mixin for credential-related database operations.

Handles credential CRUD and Bitwarden collection management.
Accesses shared state via the AgentDB instance (self.Session(), self.debug_enabled).

Methods to be migrated here:
    - create_credential
    - get_credential
    - get_credentials
    - update_credential
    - update_credential_vault_data
    - delete_credential
    - create_organization_bitwarden_collection
    - get_organization_bitwarden_collection
"""


class CredentialMixin:
    """Mixin for credential-related database operations.

    Handles credential CRUD and Bitwarden collection management.
    """
