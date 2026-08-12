"use client";

import { useState } from "react";
import ConsultationRecorder, {
  RecordingState,
  TranscriptionStatus,
} from "@/components/ConsultationRecorder";

export default function DoctorConsultScreen() {
  const [currentRecordingState, setCurrentRecordingState] =
    useState<RecordingState>("idle");
  const [transcriptionStatus, setTranscriptionStatus] =
    useState<TranscriptionStatus>("idle");
  const [transcriptionText, setTranscriptionText] = useState<string>("");

  const handleTranscriptionUpdate = (
    status: TranscriptionStatus,
    text: string
  ) => {
    setTranscriptionStatus(status);
    setTranscriptionText(text);
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100">
      {/* Top Header / App Bar */}
      <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-900/90 backdrop-blur-md px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* Brand Logo & Name */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 to-emerald-400 flex items-center justify-center text-slate-950 font-bold text-xl shadow-lg shadow-teal-500/20">
              ش
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold tracking-tight text-white">
                  ShifaScribe
                </h1>
                <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
                  v0.2-Day9
                </span>
              </div>
              <p className="text-xs text-slate-400">
                AI Urdu Voice-to-Text Medical Scribe System
              </p>
            </div>
          </div>

          {/* OPD Clinic & Doctor Badges */}
          <div className="hidden md:flex items-center gap-4">
            <div className="px-3.5 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs">
              <span className="text-slate-400 block text-[10px]">Clinic Location</span>
              <span className="font-semibold text-slate-200">OPD Block B • Room #4</span>
            </div>
            <div className="px-3.5 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs">
              <span className="text-slate-400 block text-[10px]">Consultant Doctor</span>
              <span className="font-semibold text-slate-200">
                Dr. Arsam Khan (General Physician)
              </span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-950/60 border border-emerald-800/40 text-xs text-emerald-400 font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Urdu Speech AI Engine Online
            </div>
          </div>
        </div>
      </header>

      {/* Main Doctor Workspace Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 lg:p-8 flex flex-col gap-6">
        {/* Patient Quick Context Card */}
        <section className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 md:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-lg">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-teal-400 font-bold text-lg font-mono">
              #104
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h2 className="text-lg font-semibold text-white">
                  Muhammad Tariq
                </h2>
                <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  45 yrs • Male
                </span>
                <span className="text-xs px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  OPD Routine
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Chief Complaint:{" "}
                <span className="text-slate-300">
                  Chest tightness &amp; persistent cough for 3 days
                </span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 self-end md:self-auto">
            <span className="text-xs text-slate-400">Token Status:</span>
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Active Consultation
            </span>
          </div>
        </section>

        {/* Center Panel: Recorder Component with integrated Transcription UI */}
        <section className="my-4 flex flex-col items-center justify-center">
          <ConsultationRecorder
            onStateChange={setCurrentRecordingState}
            onTranscriptionUpdate={handleTranscriptionUpdate}
          />
        </section>

        {/* Bottom EHR Transcription & Structure Preview Grid */}
        <section className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-2">
          {/* Live Urdu Audio Transcript Panel */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between shadow-lg">
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-teal-400" />
                  Urdu Voice Transcription Stream
                </h3>
                <span
                  className={`text-xs font-mono px-2 py-0.5 rounded border ${
                    transcriptionStatus === "completed"
                      ? "text-emerald-400 bg-emerald-950/60 border-emerald-800/50"
                      : transcriptionStatus === "processing_ai" ||
                        transcriptionStatus === "uploading"
                      ? "text-amber-400 bg-amber-950/60 border-amber-800/50"
                      : transcriptionStatus === "failed"
                      ? "text-red-400 bg-red-950/60 border-red-800/50"
                      : "text-slate-500 bg-slate-900 border-slate-800"
                  }`}
                >
                  {transcriptionStatus === "idle"
                    ? "Awaiting Input"
                    : transcriptionStatus === "uploading"
                    ? "Uploading..."
                    : transcriptionStatus === "processing_ai"
                    ? "AI Processing..."
                    : transcriptionStatus === "completed"
                    ? "Completed ✓"
                    : "Failed ✗"}
                </span>
              </div>

              <div className="mt-4 min-h-[140px] flex flex-col justify-center">
                {transcriptionStatus === "idle" && (
                  <p className="text-sm text-slate-500 italic text-center">
                    Click &ldquo;Start Consultation&rdquo; above to record and
                    auto-transcribe the patient conversation.
                  </p>
                )}
                {(transcriptionStatus === "uploading" ||
                  transcriptionStatus === "processing_ai") && (
                  <div className="flex flex-col items-center justify-center py-6 gap-3">
                    <div className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
                    <p className="text-xs text-amber-400 font-medium text-center">
                      {transcriptionStatus === "uploading"
                        ? "Uploading audio to Whisper AI pipeline..."
                        : "Whisper AI is processing Urdu speech..."}
                    </p>
                  </div>
                )}
                {transcriptionStatus === "completed" && (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-xs text-emerald-400 font-medium">
                      <span className="w-2 h-2 rounded-full bg-emerald-500" />
                      Transcription Received
                    </div>
                    <div className="p-3 bg-slate-950/80 rounded-xl border border-emerald-800/40 text-sm text-slate-100 dir-auto text-right font-sans leading-relaxed min-h-[80px]">
                      {transcriptionText || "(Empty transcript)"}
                    </div>
                  </div>
                )}
                {transcriptionStatus === "failed" && (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-xs text-red-400 font-medium">
                      <span className="w-2 h-2 rounded-full bg-red-500" />
                      Transcription Error
                    </div>
                    <p className="text-xs text-red-300 p-3 bg-red-950/40 rounded-xl border border-red-900/40">
                      {transcriptionText}
                    </p>
                  </div>
                )}
              </div>
            </div>

            <div className="pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-500">
              <span>Source: Built-in Microphones</span>
              <span>Sampling: 16kHz PCM</span>
            </div>
          </div>

          {/* Structured Clinical EHR Note Preview Card */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between shadow-lg">
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
                  Structured Medical EHR Output
                </h3>
                <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                  {transcriptionStatus === "completed" ? "Ready" : "Preview"}
                </span>
              </div>

              <div className="mt-4 space-y-3 min-h-[140px] text-xs">
                {transcriptionStatus === "completed" && transcriptionText ? (
                  <>
                    <div className="p-2.5 bg-slate-950/50 rounded-lg border border-teal-800/40">
                      <span className="font-semibold text-teal-400 block mb-0.5">
                        Raw AI Transcript (Urdu):
                      </span>
                      <span className="text-slate-300 dir-auto block text-right">
                        {transcriptionText}
                      </span>
                    </div>
                    <div className="p-2.5 bg-slate-950/50 rounded-lg border border-slate-800/60">
                      <span className="font-semibold text-teal-400 block mb-0.5">
                        Provisional Assessment:
                      </span>
                      <span className="text-slate-300">
                        Pending NLP ICD-10 extraction (Day 10)
                      </span>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="p-2.5 bg-slate-950/50 rounded-lg border border-slate-800/60">
                      <span className="font-semibold text-teal-400 block mb-0.5">
                        Symptoms (علامات):
                      </span>
                      <span className="text-slate-300">
                        Chest Tightness (سینے میں جکڑن), Cough (کھانسی) x 3 days
                      </span>
                    </div>
                    <div className="p-2.5 bg-slate-950/50 rounded-lg border border-slate-800/60">
                      <span className="font-semibold text-teal-400 block mb-0.5">
                        Provisional Assessment:
                      </span>
                      <span className="text-slate-300">
                        Upper Respiratory Tract Infection / Bronchitis evaluation
                      </span>
                    </div>
                  </>
                )}
              </div>
            </div>

            <div className="pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-500">
              <span>Schema: ICD-10 Standard</span>
              <span
                className={
                  transcriptionStatus === "completed"
                    ? "text-emerald-400 font-medium"
                    : "text-slate-500"
                }
              >
                {transcriptionStatus === "completed"
                  ? "Ready for EHR Sync"
                  : "Awaiting Transcription"}
              </span>
            </div>
          </div>
        </section>
      </main>

      {/* Doctor Consult Screen Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-900/40 py-3 px-6 text-center text-xs text-slate-500">
        ShifaScribe OPD Scribe System • Day 9: Frontend ↔ Whisper AI Pipeline Connected • Sprint 2
      </footer>
    </div>
  );
}
