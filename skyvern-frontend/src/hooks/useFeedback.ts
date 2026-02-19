import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getClient } from "@/api/AxiosClient";
import { useCredentialGetter } from "@/hooks/useCredentialGetter";
import type { RunFeedbackRequest, RunFeedbackResponse } from "@/api/types";

export function useFeedbackQuery(runId: string | null | undefined) {
  const credentialGetter = useCredentialGetter();

  return useQuery<RunFeedbackResponse | null>({
    queryKey: ["runFeedback", runId],
    queryFn: async () => {
      if (!runId) return null;
      const client = await getClient(credentialGetter);
      const response = await client.get<RunFeedbackResponse | null>(
        `/runs/${runId}/feedback`,
      );
      return response.data;
    },
    enabled: !!runId,
  });
}

export function useSubmitFeedbackMutation(runId: string | null | undefined) {
  const credentialGetter = useCredentialGetter();
  const queryClient = useQueryClient();

  return useMutation<RunFeedbackResponse, Error, RunFeedbackRequest>({
    mutationFn: async (request) => {
      if (!runId) throw new Error("Run ID is required");
      const client = await getClient(credentialGetter);
      const response = await client.post<RunFeedbackResponse>(
        `/runs/${runId}/feedback`,
        request,
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["runFeedback", runId] });
    },
  });
}

export function useUpdateFeedbackMutation(runId: string | null | undefined) {
  const credentialGetter = useCredentialGetter();
  const queryClient = useQueryClient();

  return useMutation<RunFeedbackResponse, Error, RunFeedbackRequest>({
    mutationFn: async (request) => {
      if (!runId) throw new Error("Run ID is required");
      const client = await getClient(credentialGetter);
      const response = await client.put<RunFeedbackResponse>(
        `/runs/${runId}/feedback`,
        request,
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["runFeedback", runId] });
    },
  });
}
