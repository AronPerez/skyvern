import { useEffect, useState, useMemo, useRef } from "react";
import { toast } from "@/components/ui/use-toast";

const VERIFICATION_CODE_TIMEOUT_MINS = 15;

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
}: UseVerificationCodeAlertOptions): UseVerificationCodeAlertReturn {
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);
  const hasNotifiedRef = useRef(false);

  // Countdown timer — reset when waiting state changes
  useEffect(() => {
    if (!isWaitingForCode || !pollingStartedAt) {
      setTimeRemaining(null);
      hasNotifiedRef.current = false;
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
  }, [isWaitingForCode, pollingStartedAt]);

  // Browser notification + sound + in-app toast (fire once per waiting transition)
  useEffect(() => {
    if (!isWaitingForCode || hasNotifiedRef.current) return;
    hasNotifiedRef.current = true;

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

    // In-app toast (uses existing toast system, TOAST_LIMIT=1)
    toast({
      variant: "warning",
      title: "2FA Code Required",
      description: `${label} needs verification to continue.`,
    });
  }, [isWaitingForCode, label, notificationTag]);

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
