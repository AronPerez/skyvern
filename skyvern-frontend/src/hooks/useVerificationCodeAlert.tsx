import { useEffect, useState, useMemo } from "react";
import { LockClosedIcon } from "@radix-ui/react-icons";
import { ExternalLinkIcon } from "@radix-ui/react-icons";
import { Link } from "react-router-dom";
import { toast } from "@/components/ui/use-toast";

const VERIFICATION_CODE_TIMEOUT_MINS = 15;

// Module-level set to track which notification tags have already fired,
// preventing re-notification when navigating to a workflow page that
// remounts the hook while isWaitingForCode is still true.
const notifiedTags = new Set<string>();

export function formatTimeRemaining(seconds: number): string {
  if (seconds <= 0) return "0:00";
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

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

export function useVerificationCodeAlert({
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
