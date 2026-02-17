import { VerificationCodeBanner } from "@/components/VerificationCodeBanner";
import {
  useNotificationStream,
  type VerificationRequest,
} from "@/hooks/useNotificationStream";
import { useQueryClient } from "@tanstack/react-query";

function bannerLabel(req: VerificationRequest): string {
  if (req.task_id) return `Task "${req.task_id}"`;
  if (req.workflow_run_id) return `Workflow run "${req.workflow_run_id}"`;
  return "Run";
}

function GlobalVerificationCodeBanners() {
  const requests = useNotificationStream();
  const queryClient = useQueryClient();

  if (requests.length === 0) return null;

  return (
    <>
      {requests.map((req) => {
        const key = req.task_id ?? req.workflow_run_id ?? "";
        return (
          <VerificationCodeBanner
            key={key}
            isWaitingForCode={true}
            pollingStartedAt={req.polling_started_at ?? null}
            label={bannerLabel(req)}
            notificationTag={`global-2fa-${key}`}
            defaultIdentifier={req.identifier ?? null}
            defaultTaskId={req.task_id ?? null}
            defaultWorkflowRunId={req.workflow_run_id ?? null}
            onCodeSent={() => {
              if (req.task_id) {
                queryClient.invalidateQueries({ queryKey: ["task"] });
              }
              if (req.workflow_run_id) {
                queryClient.invalidateQueries({
                  queryKey: ["workflowRun"],
                });
              }
            }}
          />
        );
      })}
    </>
  );
}

export { GlobalVerificationCodeBanners };
