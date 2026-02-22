import { useEffect, useState, useMemo } from "react";
import { ReloadIcon, LockClosedIcon } from "@radix-ui/react-icons";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { PushTotpCodeForm } from "@/components/PushTotpCodeForm";
import { twoFaManualFallbackTimeoutSecs } from "@/util/env";

type TwoFARequestingBannerProps = {
  workflowRunId: string;
  workflowId?: string | null;
  taskId?: string | null;
  totpVerificationUrl: string | null;
  totpIdentifier: string | null;
  waitingForVerificationCode: boolean;
  verificationCodeIdentifier: string | null;
  verificationCodePollingStartedAt: string | null;
};

function TwoFARequestingBanner({
  workflowRunId,
  workflowId,
  taskId,
  totpVerificationUrl,
  totpIdentifier,
  waitingForVerificationCode,
  verificationCodeIdentifier,
  verificationCodePollingStartedAt,
}: TwoFARequestingBannerProps) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  // Calculate elapsed time since polling started
  useEffect(() => {
    if (!waitingForVerificationCode || !verificationCodePollingStartedAt) {
      setElapsedSeconds(0);
      return;
    }

    const startTime = new Date(verificationCodePollingStartedAt).getTime();

    const updateElapsed = () => {
      const now = Date.now();
      const elapsed = Math.floor((now - startTime) / 1000);
      setElapsedSeconds(Math.max(0, elapsed));
    };

    // Initial calculation
    updateElapsed();

    // Update every second
    const interval = setInterval(updateElapsed, 1000);
    return () => clearInterval(interval);
  }, [waitingForVerificationCode, verificationCodePollingStartedAt]);

  const showManualFallback = elapsedSeconds >= twoFaManualFallbackTimeoutSecs;
  const isAutomatedFlow = Boolean(totpVerificationUrl);

  // Extract domain from totp_verification_url for display
  const urlDomain = useMemo(() => {
    if (!totpVerificationUrl) return null;
    try {
      const url = new URL(totpVerificationUrl);
      return url.hostname;
    } catch {
      return totpVerificationUrl;
    }
  }, [totpVerificationUrl]);

  // Identifier to display (prefer verification_code_identifier, fallback to totp_identifier)
  const displayIdentifier =
    verificationCodeIdentifier || totpIdentifier || null;

  // Don't render if not waiting for verification code
  if (!waitingForVerificationCode) {
    return null;
  }

  return (
    <Alert
      variant="warning"
      className="flex items-center justify-between gap-4 border-amber-600 bg-amber-950/50"
    >
      <div className="flex items-center gap-3">
        <LockClosedIcon className="h-5 w-5 text-amber-400" />
        <div>
          <AlertTitle className="mb-0 text-amber-200">
            {isAutomatedFlow && !showManualFallback
              ? "Requesting 2FA Code"
              : "2FA Code Required"}
          </AlertTitle>
          <AlertDescription className="text-amber-300/80">
            {isAutomatedFlow && !showManualFallback ? (
              <span className="flex items-center gap-2">
                <ReloadIcon className="h-3 w-3 animate-spin" />
                Requesting from {urlDomain}...
              </span>
            ) : isAutomatedFlow && showManualFallback ? (
              <span>
                2FA code not yet available from {urlDomain}. Enter a code
                manually?
              </span>
            ) : (
              <span>
                {displayIdentifier
                  ? `Waiting for code sent to ${displayIdentifier}`
                  : "Waiting for verification code"}
              </span>
            )}
          </AlertDescription>
        </div>
      </div>

      {/* Show manual input option if: not automated, or timeout reached */}
      {(!isAutomatedFlow || showManualFallback) && (
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm" className="shrink-0">
              Enter Code
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Enter 2FA Code</DialogTitle>
            </DialogHeader>
            <PushTotpCodeForm
              defaultIdentifier={displayIdentifier}
              defaultWorkflowRunId={workflowRunId}
              defaultWorkflowId={workflowId}
              defaultTaskId={taskId}
              onSuccess={() => setDialogOpen(false)}
            />
          </DialogContent>
        </Dialog>
      )}
    </Alert>
  );
}

export { TwoFARequestingBanner };
