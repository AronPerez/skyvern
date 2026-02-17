"""WebSocket endpoint for streaming global 2FA verification code notifications."""

import asyncio

import structlog
from fastapi import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from skyvern.forge import app
from skyvern.forge.sdk.notification.factory import NotificationRegistryFactory
from skyvern.forge.sdk.routes.routers import legacy_base_router
from skyvern.forge.sdk.services.org_auth_service import get_current_org

LOG = structlog.get_logger()
STREAMING_TIMEOUT = 300


@legacy_base_router.websocket("/stream/notifications")
async def notification_stream(
    websocket: WebSocket,
    apikey: str | None = None,
    token: str | None = None,
) -> None:
    try:
        await websocket.accept()
        if not token and not apikey:
            await websocket.send_text("No valid credential provided")
            return
    except ConnectionClosedOK:
        LOG.info("Notifications: ConnectionClosedOK error. Streaming won't start")
        return

    try:
        organization = await get_current_org(x_api_key=apikey, authorization=token)
        organization_id = organization.organization_id
    except Exception:
        LOG.exception("Notifications: Error while getting organization")
        try:
            await websocket.send_text("Invalid credential provided")
        except ConnectionClosedOK:
            LOG.info("Notifications: ConnectionClosedOK error while sending invalid credential message")
        return

    LOG.info("Notifications: Started streaming", organization_id=organization_id)
    registry = NotificationRegistryFactory.get_registry()
    queue = registry.subscribe(organization_id)

    try:
        # Send initial state: all currently active verification requests
        active_requests = await app.DATABASE.get_active_verification_requests(organization_id)
        for req in active_requests:
            await websocket.send_json(
                {
                    "type": "verification_code_required",
                    "task_id": req.get("task_id"),
                    "workflow_run_id": req.get("workflow_run_id"),
                    "identifier": req.get("verification_code_identifier"),
                    "polling_started_at": req.get("verification_code_polling_started_at"),
                }
            )

        # Stream real-time events
        while True:
            try:
                message = await asyncio.wait_for(queue.get(), timeout=STREAMING_TIMEOUT)
                await websocket.send_json(message)
            except TimeoutError:
                LOG.info(
                    "Notifications: No events for timeout period. Closing.",
                    organization_id=organization_id,
                )
                await websocket.send_json({"type": "timeout"})
                return

    except WebSocketDisconnect:
        LOG.info("Notifications: WebSocket disconnected", organization_id=organization_id)
    except ConnectionClosedOK:
        LOG.info("Notifications: ConnectionClosedOK", organization_id=organization_id)
    except ConnectionClosedError:
        LOG.warning(
            "Notifications: ConnectionClosedError (client likely disconnected)", organization_id=organization_id
        )
    except Exception:
        LOG.warning("Notifications: Error while streaming", organization_id=organization_id, exc_info=True)
    finally:
        registry.unsubscribe(organization_id, queue)
    LOG.info("Notifications: Connection closed", organization_id=organization_id)
