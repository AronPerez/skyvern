import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ThumbsDownIcon } from "@/components/icons/ThumbsDownIcon";
import { ThumbsUpIcon } from "@/components/icons/ThumbsUpIcon";
import { toast } from "@/components/ui/use-toast";
import { FeedbackValue, FeedbackCategory } from "@/api/types";
import {
  useFeedbackQuery,
  useSubmitFeedbackMutation,
  useUpdateFeedbackMutation,
} from "@/hooks/useFeedback";
import { FeedbackModal } from "@/components/FeedbackModal";
import { cn } from "@/util/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

type Props = {
  runId: string | null | undefined;
  disabled?: boolean;
};

function FeedbackButtons({ runId, disabled = false }: Props) {
  const [modalOpen, setModalOpen] = useState(false);

  const { data: existingFeedback, isLoading } = useFeedbackQuery(runId);
  const submitMutation = useSubmitFeedbackMutation(runId);
  const updateMutation = useUpdateFeedbackMutation(runId);

  const isPending = submitMutation.isPending || updateMutation.isPending;
  const isDisabled = disabled || isLoading || isPending;

  const currentValue = existingFeedback?.feedback_value;
  const isThumbsUp = currentValue === 1;
  const isThumbsDown = currentValue === -1;

  const handleThumbsUp = async () => {
    if (isDisabled) return;

    try {
      if (existingFeedback) {
        await updateMutation.mutateAsync({
          feedback_value: FeedbackValue.ThumbsUp,
          categories: undefined,
          comment: undefined,
        });
      } else {
        await submitMutation.mutateAsync({
          feedback_value: FeedbackValue.ThumbsUp,
        });
      }
      toast({
        variant: "success",
        title: "Thank you for your feedback!",
        description: "Your positive feedback helps us improve Skyvern.",
      });
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to submit feedback",
      });
    }
  };

  const handleThumbsDown = () => {
    if (isDisabled) return;
    setModalOpen(true);
  };

  const handleModalSubmit = async (
    categories: FeedbackCategory[],
    comment: string,
  ) => {
    try {
      if (existingFeedback) {
        await updateMutation.mutateAsync({
          feedback_value: FeedbackValue.ThumbsDown,
          categories: categories.length > 0 ? categories : undefined,
          comment: comment || undefined,
        });
      } else {
        await submitMutation.mutateAsync({
          feedback_value: FeedbackValue.ThumbsDown,
          categories: categories.length > 0 ? categories : undefined,
          comment: comment || undefined,
        });
      }
      setModalOpen(false);
      toast({
        variant: "success",
        title: "Thank you for your feedback!",
        description: "We appreciate you helping us improve Skyvern.",
      });
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to submit feedback",
      });
    }
  };

  return (
    <>
      <TooltipProvider>
        <div className="flex items-center gap-1">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                disabled={isDisabled}
                onClick={handleThumbsUp}
                className={cn(
                  "h-8 w-8",
                  isThumbsUp &&
                    "bg-green-500/20 text-green-500 hover:bg-green-500/30 hover:text-green-400",
                )}
              >
                <ThumbsUpIcon className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>
                {isThumbsUp
                  ? "You rated this run positively"
                  : "Rate this run positively"}
              </p>
            </TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                disabled={isDisabled}
                onClick={handleThumbsDown}
                className={cn(
                  "h-8 w-8",
                  isThumbsDown &&
                    "bg-red-500/20 text-red-500 hover:bg-red-500/30 hover:text-red-400",
                )}
              >
                <ThumbsDownIcon className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              {isThumbsDown ? (
                <div className="max-w-xs">
                  <p className="font-medium">You rated this run negatively</p>
                  {existingFeedback?.categories &&
                    existingFeedback.categories.length > 0 && (
                      <p className="text-xs text-slate-400">
                        Issues: {existingFeedback.categories.join(", ")}
                      </p>
                    )}
                  {existingFeedback?.comment && (
                    <p className="truncate text-xs text-slate-400">
                      Comment: {existingFeedback.comment}
                    </p>
                  )}
                </div>
              ) : (
                <p>Report an issue with this run</p>
              )}
            </TooltipContent>
          </Tooltip>
        </div>
      </TooltipProvider>

      <FeedbackModal
        open={modalOpen}
        onOpenChange={setModalOpen}
        onSubmit={handleModalSubmit}
        isPending={isPending}
        initialCategories={
          existingFeedback?.categories as FeedbackCategory[] | undefined
        }
        initialComment={existingFeedback?.comment ?? undefined}
      />
    </>
  );
}

export { FeedbackButtons };
