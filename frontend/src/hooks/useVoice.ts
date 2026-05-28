"use client";

import { useCallback, useEffect, useRef, useState } from "react";

type VoiceState = "idle" | "recording" | "processing" | "playing";

interface UseVoiceOptions {
  onTranscript?: (text: string) => void;
  onAudioChunk?: (chunk: ArrayBuffer) => void;
  sendAudioChunk?: (data: string) => void;
  sendInterrupt?: () => void;
  energyThreshold?: number;
}

interface UseVoiceReturn {
  voiceState: VoiceState;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  playAudio: (chunks: ArrayBuffer[]) => void;
  cancelPlayback: () => void;
  isSupported: boolean;
}

export function useVoice({
  onTranscript,
  sendAudioChunk,
  sendInterrupt,
  energyThreshold = 0.02,
}: UseVoiceOptions = {}): UseVoiceReturn {
  const [voiceState, setVoiceState] = useState<VoiceState>("idle");
  const [isSupported, setIsSupported] = useState(false);

  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioContext = useRef<AudioContext | null>(null);
  const analyser = useRef<AnalyserNode | null>(null);
  const sourceNode = useRef<AudioBufferSourceNode | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  // Check browser support
  useEffect(() => {
    setIsSupported(
      typeof window !== "undefined" &&
        !!navigator.mediaDevices?.getUserMedia &&
        !!window.MediaRecorder
    );
  }, []);

  const getAudioContext = useCallback(() => {
    if (!audioContext.current) {
      audioContext.current = new AudioContext();
    }
    return audioContext.current;
  }, []);

  const startRecording = useCallback(async () => {
    if (!isSupported) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,
        },
      });
      streamRef.current = stream;

      const recorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
          ? "audio/webm;codecs=opus"
          : "audio/webm",
      });

      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
          // Stream chunks to WebSocket
          if (sendAudioChunk) {
            const reader = new FileReader();
            reader.onloadend = () => {
              const base64 = (reader.result as string).split(",")[1];
              sendAudioChunk(base64);
            };
            reader.readAsDataURL(e.data);
          }
        }
      };

      recorder.onstop = () => {
        setVoiceState("processing");

        // Assemble full audio blob
        const fullBlob = new Blob(chunksRef.current, { type: "audio/webm" });
        const reader = new FileReader();
        reader.onloadend = () => {
          onTranscript?.(reader.result as string);
        };
        reader.readAsDataURL(fullBlob);
      };

      recorder.start(250); // Capture in 250ms chunks
      mediaRecorder.current = recorder;
      setVoiceState("recording");
    } catch (err) {
      console.error("[Voice] Failed to start recording:", err);
      setVoiceState("idle");
    }
  }, [isSupported, sendAudioChunk, onTranscript]);

  const stopRecording = useCallback(() => {
    if (mediaRecorder.current?.state === "recording") {
      mediaRecorder.current.stop();
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
  }, []);

  const playAudio = useCallback(
    (chunks: ArrayBuffer[]) => {
      const ctx = getAudioContext();
      setVoiceState("playing");

      // Concatenate chunks
      const totalLength = chunks.reduce((acc, c) => acc + c.byteLength, 0);
      const combined = new Uint8Array(totalLength);
      let offset = 0;
      for (const chunk of chunks) {
        combined.set(new Uint8Array(chunk), offset);
        offset += chunk.byteLength;
      }

      ctx.decodeAudioData(combined.buffer, (buffer) => {
        const source = ctx.createBufferSource();
        source.buffer = buffer;
        source.connect(ctx.destination);
        source.onended = () => setVoiceState("idle");
        source.start();
        sourceNode.current = source;
      });
    },
    [getAudioContext]
  );

  const cancelPlayback = useCallback(() => {
    if (sourceNode.current) {
      try {
        sourceNode.current.stop();
      } catch {
        // Already stopped
      }
      sourceNode.current = null;
    }
    setVoiceState("idle");
    sendInterrupt?.();
  }, [sendInterrupt]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopRecording();
      cancelPlayback();
      audioContext.current?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return {
    voiceState,
    startRecording,
    stopRecording,
    playAudio,
    cancelPlayback,
    isSupported,
  };
}
