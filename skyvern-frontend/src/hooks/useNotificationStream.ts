import { useEffect, useRef, useState } from "react";
import { useCredentialGetter } from "@/hooks/useCredentialGetter";
import { getRuntimeApiKey, wssBaseUrl } from "@/util/env";

type VerificationRequest = {
  type: "verification_code";
  task_id?: string;
  workflow_run_id?: string;
  identifier?: string | null;
  polling_started_at?: string | null;
};

type NotificationEvent = VerificationRequest;

type NotificationMessage = {
  type: string;
  task_id?: string;
  workflow_run_id?: string;
  identifier?: string | null;
  polling_started_at?: string | null;
};

function requestKey(msg: {
  task_id?: string;
  workflow_run_id?: string;
}): string {
  return msg.task_id ?? msg.workflow_run_id ?? "";
}

function useNotificationStream(): {
  events: NotificationEvent[];
  verificationRequests: VerificationRequest[];
} {
  const [eventMap, setEventMap] = useState<Map<string, NotificationEvent>>(
    new Map(),
  );
  const credentialGetter = useCredentialGetter();
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const unmountedRef = useRef(false);

  useEffect(() => {
    unmountedRef.current = false;

    async function connect() {
      if (unmountedRef.current) return;

      let credential = "";
      if (credentialGetter) {
        const token = await credentialGetter();
        credential = `?token=Bearer ${token}`;
      } else {
        const apiKey = getRuntimeApiKey();
        credential = apiKey ? `?apikey=${apiKey}` : "";
      }

      if (!credential) return;

      const socket = new WebSocket(
        `${wssBaseUrl}/stream/notifications${credential}`,
      );
      socketRef.current = socket;

      socket.addEventListener("message", (event) => {
        try {
          const msg: NotificationMessage = JSON.parse(event.data);
          const key = requestKey(msg);
          if (!key) return;

          if (msg.type === "verification_code_required") {
            setEventMap((prev) => {
              const next = new Map(prev);
              next.set(key, {
                type: "verification_code",
                task_id: msg.task_id,
                workflow_run_id: msg.workflow_run_id,
                identifier: msg.identifier,
                polling_started_at: msg.polling_started_at,
              });
              return next;
            });
          } else if (msg.type === "verification_code_resolved") {
            setEventMap((prev) => {
              const next = new Map(prev);
              next.delete(key);
              return next;
            });
          }
        } catch {
          // ignore malformed messages
        }
      });

      socket.addEventListener("close", () => {
        socketRef.current = null;
        if (!unmountedRef.current) {
          reconnectTimerRef.current = setTimeout(connect, 3000);
        }
      });

      socket.addEventListener("error", () => {
        socket.close();
      });
    }

    connect();

    return () => {
      unmountedRef.current = true;
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [credentialGetter]);

  const events = Array.from(eventMap.values());
  const verificationRequests = events.filter(
    (e): e is VerificationRequest => e.type === "verification_code",
  );

  return { events, verificationRequests };
}

export { useNotificationStream };
export type { VerificationRequest, NotificationEvent };
