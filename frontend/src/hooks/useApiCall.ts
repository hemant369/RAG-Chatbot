import { useState, useCallback } from "react";

export type ApiStatus = "idle" | "loading" | "success" | "error";

interface UseApiCallOptions {
  onSuccess?: (data: any) => void;
  onError?: (error: any) => void;
  resetDelay?: number; // Auto-reset status after X ms (default: 3000)
}

export function useApiCall<T = any>(options: UseApiCallOptions = {}) {
  const { onSuccess, onError, resetDelay = 3000 } = options;

  const [status, setStatus] = useState<ApiStatus>("idle");
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(
    async (apiFunction: () => Promise<T>) => {
      setStatus("loading");
      setError(null);

      try {
        const result = await apiFunction();
        setData(result);
        setStatus("success");
        onSuccess?.(result);

        // Auto-reset status after delay
        if (resetDelay > 0) {
          setTimeout(() => {
            setStatus("idle");
          }, resetDelay);
        }

        return result;
      } catch (err: any) {
        const errorMessage = err?.response?.data?.detail || err?.message || "An error occurred";
        setError(errorMessage);
        setStatus("error");
        onError?.(err);

        // Auto-reset error after delay
        if (resetDelay > 0) {
          setTimeout(() => {
            setStatus("idle");
            setError(null);
          }, resetDelay);
        }

        throw err;
      }
    },
    [onSuccess, onError, resetDelay]
  );

  const reset = useCallback(() => {
    setStatus("idle");
    setError(null);
    setData(null);
  }, []);

  return {
    status,
    data,
    error,
    isLoading: status === "loading",
    isSuccess: status === "success",
    isError: status === "error",
    isIdle: status === "idle",
    execute,
    reset,
  };
}
