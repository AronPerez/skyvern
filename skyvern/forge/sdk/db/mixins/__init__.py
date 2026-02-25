"""Database mixins for AgentDB.

Each mixin groups related database operations by domain.
Mixins access shared state via the AgentDB instance:
  - self.Session()       -- async context manager for DB sessions
  - self.debug_enabled   -- controls debug info in model conversions

Usage pattern inside a mixin method::

    async def get_thing(self, thing_id: str) -> Thing | None:
        async with self.Session() as session:
            result = await session.execute(select(ThingModel).where(...))
            row = result.scalars().first()
            return convert_to_thing(row) if row else None
"""

from skyvern.forge.sdk.db.mixins.artifact import ArtifactMixin
from skyvern.forge.sdk.db.mixins.browser_session import BrowserSessionMixin
from skyvern.forge.sdk.db.mixins.credential import CredentialMixin
from skyvern.forge.sdk.db.mixins.debug import DebugMixin
from skyvern.forge.sdk.db.mixins.folder import FolderMixin
from skyvern.forge.sdk.db.mixins.observer import ObserverMixin
from skyvern.forge.sdk.db.mixins.organization import OrganizationMixin
from skyvern.forge.sdk.db.mixins.otp import OTPMixin
from skyvern.forge.sdk.db.mixins.script import ScriptMixin
from skyvern.forge.sdk.db.mixins.task import TaskMixin
from skyvern.forge.sdk.db.mixins.workflow import WorkflowMixin
from skyvern.forge.sdk.db.mixins.workflow_run import WorkflowRunMixin

__all__ = [
    "ArtifactMixin",
    "BrowserSessionMixin",
    "CredentialMixin",
    "DebugMixin",
    "FolderMixin",
    "ObserverMixin",
    "OrganizationMixin",
    "OTPMixin",
    "ScriptMixin",
    "TaskMixin",
    "WorkflowMixin",
    "WorkflowRunMixin",
]
