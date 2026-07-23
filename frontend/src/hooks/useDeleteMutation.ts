import { useMutation, useQueryClient } from "@tanstack/react-query";

export function useDeleteMutation<TId>(
  mutationFn: (id: TId) => Promise<void>,
  invalidateKey: unknown[],
  options?: {
    onSuccess?: () => void;
    onError?: (error: Error) => void;
  },
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: invalidateKey });
      options?.onSuccess?.();
    },
    onError: (err: Error) => {
      options?.onError?.(err);
    },
  });
}
