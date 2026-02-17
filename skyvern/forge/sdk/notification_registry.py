"""In-process pub/sub registry for pushing real-time notifications to WebSocket clients.

Each organization can have multiple subscribers (WebSocket connections).
Events are published to all subscribers for the given organization.
"""

import asyncio
from collections import defaultdict

import structlog

LOG = structlog.get_logger()


class NotificationRegistry:
    """Fan-out pub/sub: publish a message to all subscribers for an organization."""

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


notification_registry = NotificationRegistry()
