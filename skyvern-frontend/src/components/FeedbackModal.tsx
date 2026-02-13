import { useState, useEffect } from "react";
import { ReloadIcon } from "@radix-ui/react-icons";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { FeedbackCategory, FeedbackCategoryLabels } from "@/api/types";

type Props = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (categories: FeedbackCategory[], comment: string) => void;
  isPending: boolean;
  initialCategories?: FeedbackCategory[];
  initialComment?: string;
};

const allCategories = Object.values(FeedbackCategory);

function FeedbackModal({
  open,
  onOpenChange,
  onSubmit,
  isPending,
  initialCategories = [],
  initialComment = "",
}: Props) {
  const [selectedCategories, setSelectedCategories] =
    useState<FeedbackCategory[]>(initialCategories);
  const [comment, setComment] = useState(initialComment);

  // Reset form when modal opens with initial values
  useEffect(() => {
    if (open) {
      setSelectedCategories(initialCategories);
      setComment(initialComment);
    }
  }, [open, initialCategories, initialComment]);

  const handleCategoryToggle = (category: FeedbackCategory) => {
    setSelectedCategories((prev) =>
      prev.includes(category)
        ? prev.filter((c) => c !== category)
        : [...prev, category],
    );
  };

  const handleSubmit = () => {
    onSubmit(selectedCategories, comment);
  };

  const showCommentHint =
    selectedCategories.includes(FeedbackCategory.Other) && !comment.trim();

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>What went wrong?</DialogTitle>
          <DialogDescription>
            Help us improve by selecting the issues you encountered and
            providing additional details.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-3">
            <Label className="text-sm font-medium">
              Select all that apply (optional)
            </Label>
            <div className="space-y-2">
              {allCategories.map((category) => (
                <div key={category} className="flex items-center space-x-2">
                  <Checkbox
                    id={category}
                    checked={selectedCategories.includes(category)}
                    onCheckedChange={() => handleCategoryToggle(category)}
                  />
                  <label
                    htmlFor={category}
                    className="cursor-pointer text-sm leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                  >
                    {FeedbackCategoryLabels[category]}
                  </label>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="comment" className="text-sm font-medium">
              Additional details (optional)
            </Label>
            <Textarea
              id="comment"
              placeholder="Please describe the issue in more detail..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={4}
              className="resize-none"
            />
            {showCommentHint && (
              <p className="text-xs text-amber-500">
                Please describe what went wrong since you selected "Other"
              </p>
            )}
          </div>
        </div>

        <DialogFooter>
          <DialogClose asChild>
            <Button variant="secondary" disabled={isPending}>
              Cancel
            </Button>
          </DialogClose>
          <Button onClick={handleSubmit} disabled={isPending}>
            {isPending && <ReloadIcon className="mr-2 h-4 w-4 animate-spin" />}
            Submit Feedback
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export { FeedbackModal };
