"""Pluggable pub/sub registry for pushing real-time notifications to WebSocket clients.

OSS uses LocalNotificationRegistry (in-process asyncio queues).
Cloud deployments can substitute a distributed implementation
(e.g., Redis pub/sub) via NotificationRegistryFactory.set_registry().
"""

import asyncio
from abc import ABC, abstractmethod
from collections import defaultdict

import structlog

LOG = structlog.get_logger()


class BaseNotificationRegistry(ABC):
    """Abstract pub/sub registry scoped by organization.

    Implementations must fan-out: a single publish call delivers the
    message to every active subscriber for that organization.
    """

    @abstractmethod
    def subscribe(self, organization_id: str) -> asyncio.Queue[dict]: ...

    @abstractmethod
    def unsubscribe(self, organization_id: str, queue: asyncio.Queue[dict]) -> None: ...

    @abstractmethod
    def publish(self, organization_id: str, message: dict) -> None: ...


class LocalNotificationRegistry(BaseNotificationRegistry):
    """In-process fan-out pub/sub using asyncio queues. Single-pod only."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[asyncio.Queue[dict]]] = defaultdict(list)

    def subscribe(self, organization_id: str) -> asyncio.Queue[dict]:
        queue: asyncio.Queue[dict] = asyncio.Queue()
        self._subscribers[organization_id].append(queue)
        LOG.info("Notification subscriber added", organization_id=organization_id)
        return queue

    def unsubscribe(self, organization_id: str, queue: asyncio.Queue[dict]) -> None:
        queues = self._subscribers.get(organization_id)
        if queues:
            try:
                queues.remove(queue)
            except ValueError:
                pass
            if not queues:
                del self._subscribers[organization_id]
        LOG.info("Notification subscriber removed", organization_id=organization_id)

    def publish(self, organization_id: str, message: dict) -> None:
        queues = self._subscribers.get(organization_id, [])
        for queue in queues:
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                LOG.warning(
                    "Notification queue full, dropping message",
                    organization_id=organization_id,
                )


class NotificationRegistryFactory:
    __registry: BaseNotificationRegistry = LocalNotificationRegistry()

    @staticmethod
    def set_registry(registry: BaseNotificationRegistry) -> None:
        NotificationRegistryFactory.__registry = registry

    @staticmethod
    def get_registry() -> BaseNotificationRegistry:
        return NotificationRegistryFactory.__registry
