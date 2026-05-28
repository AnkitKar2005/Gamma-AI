"use client";

import { useCallback, useEffect, useRef } from "react";
import type { WSMessage, WSMessageType } from "@/types";

interface UseStreamOptions {
  /** Called for each token chunk during streaming */
  onToken: (content: string, messageId: string) => void;
  /** Called when streaming completes */
  onDone: (messageId: string) => void;
  /** Called when an error occurs */
  onError: (error: string) => void;
}

/**
 * Hook that handles streaming chat_token / chat_done / error
 * WebSocket messages and dispatches to callbacks.
 *
 * Returns a message handler suitable for useWebSocket's onMessage.
 */
export function useStream({ onToken, onDone, onError }: UseStreamOptions) {
  const onTokenRef = useRef(onToken);
  const onDoneRef = useRef(onDone);
  const onErrorRef = useRef(onError);

  useEffect(() => {
    onTokenRef.current = onToken;
    onDoneRef.current = onDone;
    onErrorRef.current = onError;
  }, [onToken, onDone, onError]);

  const handleMessage = useCallback(
    (type: WSMessageType, payload: Record<string, unknown>, _message: WSMessage) => {
      switch (type) {
        case "chat_token": {
          const content = (payload.content as string) ?? "";
          const messageId = (payload.message_id as string) ?? "";
          onTokenRef.current(content, messageId);
          break;
        }

        case "chat_done": {
          const messageId = (payload.message_id as string) ?? "";
          onDoneRef.current(messageId);
          break;
        }

        case "error": {
          const error = (payload.error as string) ?? "Unknown error";
          onErrorRef.current(error);
          break;
        }

        // Other message types are handled elsewhere
        default:
          break;
      }
    },
    []
  );

  return { handleMessage };
}
