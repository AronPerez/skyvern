import { useState, useEffect, useMemo } from "react";
import {
  LockClosedIcon,
  ClockIcon,
  ExternalLinkIcon,
} from "@radix-ui/react-icons";
import { Link } from "react-router-dom";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { PushTotpCodeForm } from "@/components/PushTotpCodeForm";
import { toast } from "@/components/ui/use-toast";
import { formatTimeRemaining } from "@/util/timeFormat";

const VERIFICATION_CODE_TIMEOUT_MINS = 15;

// Module-level set to track which notification tags have already fired,
// preventing re-notification when navigating to a workflow page that
// remounts the hook while isWaitingForCode is still true.
const notifiedTags = new Set<string>();

type UseVerificationCodeAlertOptions = {
  isWaitingForCode: boolean;
  pollingStartedAt: string | null | undefined;
  label: string;
  notificationTag: string;
  navigateUrl?: string;
};

type UseVerificationCodeAlertReturn = {
  timeRemaining: number | null;
  isTimeCritical: boolean;
  isTimedOut: boolean;
};

function useVerificationCodeAlert({
  isWaitingForCode,
  pollingStartedAt,
  label,
  notificationTag,
  navigateUrl,
}: UseVerificationCodeAlertOptions): UseVerificationCodeAlertReturn {
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);

  // Countdown timer — reset when waiting state changes
  useEffect(() => {
    if (!isWaitingForCode || !pollingStartedAt) {
      setTimeRemaining(null);
      notifiedTags.delete(notificationTag);
      return;
    }

    const startTime = new Date(pollingStartedAt).getTime();
    const timeoutMs = VERIFICATION_CODE_TIMEOUT_MINS * 60 * 1000;

    const updateTimer = () => {
      const now = Date.now();
      const elapsed = now - startTime;
      const remaining = Math.max(0, Math.ceil((timeoutMs - elapsed) / 1000));
      setTimeRemaining(remaining);
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);
    return () => clearInterval(interval);
  }, [isWaitingForCode, pollingStartedAt, notificationTag]);

  // Browser notification + sound + in-app toast (fire once per waiting transition)
  useEffect(() => {
    if (!isWaitingForCode || notifiedTags.has(notificationTag)) return;
    notifiedTags.add(notificationTag);

    // OS-level browser notification
    if (typeof Notification !== "undefined") {
      if (Notification.permission === "default") {
        Notification.requestPermission();
      }
      if (Notification.permission === "granted") {
        try {
          const notification = new Notification("2FA Code Required", {
            body: `${label} needs a verification code to continue.`,
            icon: "/favicon.png",
            tag: notificationTag,
            requireInteraction: true,
          });
          notification.onclick = () => {
            window.focus();
            notification.close();
          };
        } catch (e) {
          console.error("Failed to create notification:", e);
        }
      }
    }

    // Sound alert
    try {
      const audio = new Audio("/dragon-cry.mp3");
      audio.play().catch((e) => console.error("Failed to play sound:", e));
    } catch (e) {
      console.error("Failed to create audio:", e);
    }

    // In-app toast — Figma Option C style (dark bg, amber outline, lock icon, nav link)
    toast({
      variant: "default",
      className: "border-warning/50",
      title: (
        <div className="flex items-start gap-2">
          <LockClosedIcon className="mt-0.5 h-4 w-4 flex-shrink-0 text-warning" />
          <span>2FA Code Required</span>
        </div>
      ),
      description: (
        <div className="space-y-2">
          <p className="text-muted-foreground">
            {label} needs verification to continue.
          </p>
          {navigateUrl && (
            <Link
              to={navigateUrl}
              className="inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300"
            >
              Go to workflow
              <ExternalLinkIcon className="h-3 w-3" />
            </Link>
          )}
        </div>
      ),
    });
  }, [isWaitingForCode, label, notificationTag, navigateUrl]);

  const isTimeCritical = useMemo(
    () => timeRemaining !== null && timeRemaining <= 60,
    [timeRemaining],
  );
  const isTimedOut = useMemo(
    () => timeRemaining !== null && timeRemaining <= 0,
    [timeRemaining],
  );

  return { timeRemaining, isTimeCritical, isTimedOut };
}

type VerificationCodeBannerProps = {
  isWaitingForCode: boolean;
  pollingStartedAt: string | null | undefined;
  label: string;
  notificationTag: string;
  navigateUrl?: string;
  defaultIdentifier: string | null | undefined;
  defaultWorkflowRunId?: string | null;
  defaultWorkflowId?: string | null;
  defaultTaskId?: string | null;
  onCodeSent?: () => void;
};

function VerificationCodeBanner({
  isWaitingForCode,
  pollingStartedAt,
  label,
  notificationTag,
  navigateUrl,
  defaultIdentifier,
  defaultWorkflowRunId,
  defaultWorkflowId,
  defaultTaskId,
  onCodeSent,
}: VerificationCodeBannerProps) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const { timeRemaining, isTimeCritical, isTimedOut } =
    useVerificationCodeAlert({
      isWaitingForCode,
      pollingStartedAt,
      label,
      notificationTag,
      navigateUrl,
    });

  if (!isWaitingForCode) return null;

  const handleSuccess = () => {
    setDialogOpen(false);
    onCodeSent?.();
  };

  return (
    <>
      {/* Slim persistent banner — Figma Option C */}
      <div className="flex items-center justify-between border-b border-amber-500/30 bg-amber-500/10 px-4 py-2.5">
        <div className="flex min-w-0 flex-1 items-center gap-2">
          <LockClosedIcon className="h-3.5 w-3.5 flex-shrink-0 text-amber-400" />
          <p className="truncate text-xs text-slate-200">
            <span className="text-slate-100">{label}</span> needs 2FA
          </p>
          {timeRemaining !== null && (
            <span
              className={`ml-2 flex items-center gap-1 text-xs font-medium ${
                isTimeCritical ? "text-red-300" : "text-slate-400"
              }`}
            >
              <ClockIcon className="h-3 w-3" />
              {formatTimeRemaining(timeRemaining)}
            </span>
          )}
        </div>
        <div className="flex flex-shrink-0 items-center gap-2">
          {isTimedOut && (
            <span className="text-xs text-red-300">Timed out</span>
          )}
          <button
            type="button"
            onClick={() => setDialogOpen(true)}
            className="rounded bg-amber-500/20 px-2 py-1 text-xs font-medium text-amber-400 transition-colors hover:bg-amber-500/30"
          >
            Enter Code
          </button>
        </div>
      </div>

      {/* Dialog with PushTotpCodeForm */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Enter 2FA Verification Code</DialogTitle>
            <DialogDescription>
              Enter the code you received (6-digit code or magic link URL) to
              continue.
            </DialogDescription>
          </DialogHeader>
          <PushTotpCodeForm
            defaultIdentifier={defaultIdentifier}
            defaultWorkflowRunId={defaultWorkflowRunId}
            defaultWorkflowId={defaultWorkflowId}
            defaultTaskId={defaultTaskId}
            showAdvancedFields={false}
            onSuccess={handleSuccess}
          />
        </DialogContent>
      </Dialog>
    </>
  );
}

export { VerificationCodeBanner };
