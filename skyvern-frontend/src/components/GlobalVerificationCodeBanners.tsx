import { useVerificationCodeAlert } from "@/hooks/useVerificationCodeAlert";
import {
  useNotificationStream,
  type VerificationRequest,
} from "@/hooks/useNotificationStream";

function notificationLabel(req: VerificationRequest): string {
  if (req.task_id) return `Task "${req.task_id}"`;
  if (req.workflow_run_id) return `Workflow run "${req.workflow_run_id}"`;
  return "Run";
}

/**
 * Invisible component that fires toast / browser notification / sound
 * for a single active 2FA request. No banner UI — that lives on the
 * per-page detail components only.
 */
function GlobalNotificationItem({ req }: { req: VerificationRequest }) {
  const key = req.task_id ?? req.workflow_run_id ?? "";
  useVerificationCodeAlert({
    isWaitingForCode: true,
    pollingStartedAt: req.polling_started_at ?? null,
    label: notificationLabel(req),
    notificationTag: `2fa-required-${key}`,
  });
  return null;
}

function GlobalVerificationCodeBanners() {
  const requests = useNotificationStream();

  if (requests.length === 0) return null;

  return (
    <>
      {requests.map((req) => {
        const key = req.task_id ?? req.workflow_run_id ?? "";
        return <GlobalNotificationItem key={key} req={req} />;
      })}
    </>
  );
}

export { GlobalVerificationCodeBanners };
