import { useState, useEffect, useMemo } from "react";
import { VerificationCodeBanner } from "@/components/VerificationCodeBanner";
import { statusIsFinalized } from "@/routes/tasks/types";
import { useWorkflowRunWithWorkflowQuery } from "../hooks/useWorkflowRunWithWorkflowQuery";
import { useQueryClient } from "@tanstack/react-query";
import { twoFaManualFallbackTimeoutSecs } from "@/util/env";

function WorkflowRunVerificationCodeForm() {
  const queryClient = useQueryClient();
  const { data: workflowRun } = useWorkflowRunWithWorkflowQuery();

  const isRunFinalized = workflowRun ? statusIsFinalized(workflowRun) : false;
  const isWaitingForCode =
    !isRunFinalized && (workflowRun?.waiting_for_verification_code ?? false);

  const totpVerificationUrl =
    workflowRun?.totp_verification_url ??
    workflowRun?.workflow?.totp_verification_url ??
    null;
  const isAutomatedFlow = Boolean(totpVerificationUrl) && isWaitingForCode;

  const pollingStartedAt =
    workflowRun?.verification_code_polling_started_at ?? null;
  const [showManualFallback, setShowManualFallback] = useState(false);

  useEffect(() => {
    if (!isAutomatedFlow || !pollingStartedAt) {
      setShowManualFallback(false);
      return;
    }
    let ts = pollingStartedAt;
    if (!ts.endsWith("Z") && !ts.includes("+") && !ts.includes("-", 10)) {
      ts += "Z";
    }
    const startMs = new Date(ts).getTime();
    const check = () =>
      setShowManualFallback(
        (Date.now() - startMs) / 1000 >= twoFaManualFallbackTimeoutSecs,
      );
    check();
    const id = setInterval(check, 1000);
    return () => clearInterval(id);
  }, [isAutomatedFlow, pollingStartedAt]);

  const urlDomain = useMemo(() => {
    if (!totpVerificationUrl) return null;
    try {
      return new URL(totpVerificationUrl).hostname;
    } catch {
      return totpVerificationUrl;
    }
  }, [totpVerificationUrl]);

  const navigateUrl =
    workflowRun?.workflow?.workflow_permanent_id && workflowRun?.workflow_run_id
      ? `/workflows/${workflowRun.workflow.workflow_permanent_id}/${workflowRun.workflow_run_id}`
      : undefined;

  return (
    <VerificationCodeBanner
      isWaitingForCode={isWaitingForCode}
      pollingStartedAt={pollingStartedAt}
      label={`Workflow "${workflowRun?.workflow?.title ?? "Run"}"`}
      notificationTag={`2fa-required-${workflowRun?.workflow_run_id}`}
      navigateUrl={navigateUrl}
      defaultIdentifier={workflowRun?.verification_code_identifier ?? null}
      defaultWorkflowRunId={workflowRun?.workflow_run_id}
      defaultWorkflowId={workflowRun?.workflow?.workflow_permanent_id}
      onCodeSent={() =>
        queryClient.invalidateQueries({ queryKey: ["workflowRun"] })
      }
      descriptionNode={
        isAutomatedFlow ? (
          showManualFallback ? (
            <>
              2FA code not yet available from {urlDomain}. Enter a code
              manually?
            </>
          ) : (
            <>Requesting from {urlDomain}...</>
          )
        ) : undefined
      }
      showSpinner={isAutomatedFlow && !showManualFallback}
      showManualEntry={!isAutomatedFlow || showManualFallback}
    />
  );
}

export { WorkflowRunVerificationCodeForm };
