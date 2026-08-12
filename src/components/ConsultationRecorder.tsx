"use client";

import { useState, useEffect, useRef } from "react";

export type RecordingState = "idle" | "recording" | "processing";

interface ConsultationRecorderProps {
  onStateChange?: (state: RecordingState) => void;
}

export default function ConsultationRecorder({
  onStateChange,
}: ConsultationRecorderProps) {
  const [recordingState, setRecordingState] = useState<RecordingState>("idle");
  const [seconds, setSeconds] = useState(0);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [audioBlobSizeKB, setAudioBlobSizeKB] = useState<string | null>(null);
  const [audioMimeType, setAudioMimeType] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Audio capture refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  // Timer effect when recording
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (recordingState === "recording") {
      interval = setInterval(() => {
        setSeconds((prev) => prev + 1);
      }, 1000);
    } else {
      setSeconds(0);
    }
    return () => clearInterval(interval);
  }, [recordingState]);

  const updateState = (newState: RecordingState) => {
    setRecordingState(newState);
    if (onStateChange) {
      onStateChange(newState);
    }
  };

  // Start MediaRecorder & Compressed Microphone Capture (Day 3 Update)
  const startRecording = async () => {
    setErrorMessage(null);
    audioChunksRef.current = [];

    console.log("[ShifaScribe Compression] Requesting microphone access with 16kHz Mono constraints...");

    // Day 3 Audio Constraints: 16kHz Sample Rate, 1 Channel (Mono), Noise Suppression
    const audioConstraints: MediaStreamConstraints = {
      audio: {
        sampleRate: 16000,
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    };

    try {
      const stream = await navigator.mediaDevices.getUserMedia(audioConstraints);
      streamRef.current = stream;
      console.log("[ShifaScribe Compression] Microphone permission granted! Applied constraints: 16kHz sample rate, 1 (Mono) channel.");

      // Day 3 WebM MIME Type Detection & Fallback
      const preferredMimeTypes = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/ogg;codecs=opus",
        "audio/mp4",
      ];

      const selectedMimeType =
        preferredMimeTypes.find((type) => MediaRecorder.isTypeSupported(type)) || "";

      console.log(`[ShifaScribe Compression] Selected browser MIME type: ${selectedMimeType}`);

      const options = selectedMimeType ? { mimeType: selectedMimeType } : undefined;
      const mediaRecorder = new MediaRecorder(stream, options);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event: BlobEvent) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          const chunkKB = (event.data.size / 1024).toFixed(2);
          console.log(
            `[ShifaScribe Compression] Collected chunk #${audioChunksRef.current.length}: ${chunkKB} KB (${event.data.size} bytes)`
          );
        }
      };

      mediaRecorder.onstop = () => {
        console.log(
          `[ShifaScribe Compression] MediaRecorder stopped. Assembling ${audioChunksRef.current.length} chunks...`
        );
        const finalBlobType = selectedMimeType || "audio/webm";
        const blob = new Blob(audioChunksRef.current, { type: finalBlobType });
        const url = URL.createObjectURL(blob);

        const sizeInKB = (blob.size / 1024).toFixed(2);
        setAudioUrl(url);
        setAudioBlobSizeKB(sizeInKB);
        setAudioMimeType(blob.type || finalBlobType);

        // Day 4 Verification Console Log
        console.log(
          `[ShifaScribe Compression Success] Final Compressed Blob Generated:\n` +
          `  • Size: ${sizeInKB} KB (${blob.size} bytes)\n` +
          `  • MIME Type: ${blob.type || finalBlobType}\n` +
          `  • Object URL: ${url}`
        );

        // Stop all stream tracks to release microphone hardware
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((track) => {
            track.stop();
            console.log(`[ShifaScribe Compression] Released audio track: ${track.label}`);
          });
          streamRef.current = null;
        }

        setTimeout(() => {
          updateState("idle");
        }, 1200);
      };

      // Start recording with 1000ms chunk interval
      mediaRecorder.start(1000);
      console.log(
        `[ShifaScribe Compression] MediaRecorder active (Timeslice: 1000ms, MIME: ${selectedMimeType || "default"}).`
      );

      updateState("recording");
    } catch (err: any) {
      console.error("[ShifaScribe Compression] Error accessing microphone:", err);
      setErrorMessage(
        err.name === "NotAllowedError" || err.name === "PermissionDeniedError"
          ? "Microphone access denied. Please allow microphone permissions in your browser bar."
          : `Failed to initialize microphone: ${err.message || err}`
      );
      updateState("idle");
    }
  };

  // Stop MediaRecorder
  const stopRecording = () => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      console.log("[ShifaScribe Compression] Stopping MediaRecorder...");
      updateState("processing");
      mediaRecorderRef.current.stop();
    }
  };

  const handleMainButtonClick = () => {
    if (recordingState === "idle") {
      startRecording();
    } else if (recordingState === "recording") {
      stopRecording();
    }
  };

  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const remainingSecs = secs % 60;
    return `${mins.toString().padStart(2, "0")}:${remainingSecs
      .toString()
      .padStart(2, "0")}`;
  };

  return (
    <div className="w-full max-w-xl mx-auto flex flex-col items-center justify-center p-8 bg-slate-900/80 rounded-3xl border border-slate-800 shadow-2xl backdrop-blur-xl transition-all duration-300">
      {/* Header Badge */}
      <div className="flex items-center justify-between w-full mb-6 px-2">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-emerald-500 animate-ping" />
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            ShifaScribe Mic (16kHz Mono • WebM)
          </span>
        </div>
        <div className="flex items-center gap-2">
          {recordingState === "idle" && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-950/80 text-emerald-400 border border-emerald-800/50">
              ● Ready (Compressed)
            </span>
          )}
          {recordingState === "recording" && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-950/90 text-red-400 border border-red-800/60 animate-pulse">
              ● Live 16kHz Stream
            </span>
          )}
          {recordingState === "processing" && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-amber-950/90 text-amber-400 border border-amber-800/60">
              ● WebM Compression
            </span>
          )}
        </div>
      </div>

      {/* Error Alert Banner */}
      {errorMessage && (
        <div className="w-full mb-6 p-3.5 bg-red-950/80 border border-red-800/60 rounded-xl text-red-200 text-xs flex items-center gap-3">
          <span className="text-base">⚠️</span>
          <p>{errorMessage}</p>
        </div>
      )}

      {/* Main Record Button */}
      <div className="relative flex items-center justify-center my-4 group">
        <button
          id="consultation-record-btn"
          onClick={handleMainButtonClick}
          disabled={recordingState === "processing"}
          aria-label="Consultation Recording Button"
          className={`relative z-10 w-48 h-48 rounded-full flex flex-col items-center justify-center transition-all duration-300 transform active:scale-95 focus:outline-none focus:ring-4 ${
            recordingState === "idle"
              ? "bg-gradient-to-tr from-teal-600 via-emerald-600 to-emerald-500 text-white shadow-lg shadow-emerald-900/40 hover:scale-105 hover:shadow-emerald-700/60 border-4 border-emerald-400/30 focus:ring-emerald-500/40"
              : recordingState === "recording"
              ? "bg-gradient-to-tr from-red-600 via-rose-600 to-red-500 text-white shadow-2xl shadow-red-900/60 animate-pulse-ring border-4 border-red-400 focus:ring-red-500/50"
              : "bg-gradient-to-tr from-amber-600 via-orange-600 to-amber-700 text-white shadow-xl shadow-amber-900/40 cursor-wait border-4 border-amber-400/40 focus:ring-amber-500/40"
          }`}
        >
          {recordingState === "idle" && (
            <div className="flex flex-col items-center justify-center text-center p-2">
              <svg
                className="w-16 h-16 mb-2 drop-shadow-md"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                />
              </svg>
              <span className="text-sm font-bold uppercase">Start Consultation</span>
              <span className="text-[11px] font-medium text-emerald-100/90 dir-rtl">
                شروع کریں
              </span>
            </div>
          )}

          {recordingState === "recording" && (
            <div className="flex flex-col items-center justify-center text-center p-2">
              <div className="flex items-center gap-1.5 h-8 mb-2">
                <div className="w-1.5 bg-white rounded-full waveform-bar-1" />
                <div className="w-1.5 bg-white rounded-full waveform-bar-2" />
                <div className="w-1.5 bg-white rounded-full waveform-bar-3" />
                <div className="w-1.5 bg-white rounded-full waveform-bar-4" />
                <div className="w-1.5 bg-white rounded-full waveform-bar-5" />
              </div>
              <span className="text-2xl font-extrabold font-mono">{formatTime(seconds)}</span>
              <span className="text-xs font-semibold uppercase text-red-100 mt-1">
                Stop & Compress
              </span>
            </div>
          )}

          {recordingState === "processing" && (
            <div className="flex flex-col items-center justify-center text-center p-2">
              <svg className="w-12 h-12 mb-2 animate-spin text-amber-100" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span className="text-xs font-bold uppercase text-amber-100">Compressing Audio</span>
            </div>
          )}
        </button>
      </div>

      {/* Local HTML5 Audio Voice Playback Player Card */}
      {audioUrl && (
        <div className="w-full mt-6 p-4 bg-slate-950/90 border border-teal-500/40 rounded-2xl flex flex-col gap-3 shadow-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-teal-400 animate-pulse" />
              <span className="text-xs font-bold text-teal-300 uppercase tracking-wider">
                Compressed Audio Playback (Day 3 Verified)
              </span>
            </div>
            <div className="flex items-center gap-2 font-mono text-[11px]">
              {audioBlobSizeKB && (
                <span className="text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/60 font-bold">
                  {audioBlobSizeKB} KB
                </span>
              )}
              {audioMimeType && (
                <span className="text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                  {audioMimeType}
                </span>
              )}
            </div>
          </div>

          <audio
            id="captured-audio-player"
            controls
            src={audioUrl}
            className="w-full rounded-lg accent-teal-500 h-10"
          />

          <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
            <span>Constraints: 16kHz • Mono Channel</span>
            <span className="text-teal-400 font-medium">Bandwidth Optimized</span>
          </div>
        </div>
      )}
    </div>
  );
}
