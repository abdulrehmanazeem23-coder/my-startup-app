"use client";

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import ConsultationRecorder, {
  RecordingState,
  TranscriptionStatus,
} from "@/components/ConsultationRecorder";
import PrescriptionForm, { StructuredEhrData } from "@/components/PrescriptionForm";

function DoctorConsultScreenContent() {
  const searchParams = useSearchParams();

  // Active Patient State (Defaults to demo Patient #104 or query params)
  const paramPatientId = searchParams.get("patient_id") || "104";
  const paramName = searchParams.get("name") || "Muhammad Tariq";
  const paramToken = searchParams.get("token") || "#104";
  const paramAge = searchParams.get("age") || "45";
  const paramGender = searchParams.get("gender") || "Male";
  const paramComplaint = searchParams.get("complaint") || "Severe headache & fever for 2 days";

  const [patientId, setPatientId] = useState<string>(paramPatientId);
  const [patientName, setPatientName] = useState<string>(paramName);
  const [patientToken, setPatientToken] = useState<string>(paramToken);
  const [patientAge, setPatientAge] = useState<string>(paramAge);
  const [patientGender, setPatientGender] = useState<string>(paramGender);
  const [chiefComplaint, setChiefComplaint] = useState<string>(paramComplaint);

  const [currentRecordingState, setCurrentRecordingState] =
    useState<RecordingState>("idle");
  const [transcriptionStatus, setTranscriptionStatus] =
    useState<TranscriptionStatus>("idle");
  const [transcriptionText, setTranscriptionText] = useState<string>("");
  const [structuredEhr, setStructuredEhr] = useState<StructuredEhrData | null>(null);

  // When searchParams change, update patient profile and attempt fetch if needed
  useEffect(() => {
    const qPid = searchParams.get("patient_id");
    const qName = searchParams.get("name");
    const qToken = searchParams.get("token");
    const qAge = searchParams.get("age");
    const qGender = searchParams.get("gender");
    const qComplaint = searchParams.get("complaint");

    if (qPid) setPatientId(qPid);
    if (qName) setPatientName(qName);
    if (qToken) setPatientToken(qToken);
    if (qAge) setPatientAge(qAge);
    if (qGender) setPatientGender(qGender);
    if (qComplaint) setChiefComplaint(qComplaint);

    // If only patient_id was passed without full params, fetch profile from backend
    if (qPid && !qName) {
      const backendUrl = typeof window !== "undefined"
        ? `http://${window.location.hostname || "localhost"}:8000`
        : "http://localhost:8000";

      fetch(`${backendUrl}/api/patients/${qPid}`)
        .then((res) => (res.ok ? res.json() : null))
        .then((data) => {
          if (data && data.name) {
            setPatientName(data.name);
            setPatientAge(String(data.age || 40));
            setPatientGender(data.gender || "Male");
            setPatientToken(data.opd_token || `#${qPid}`);
          }
        })
        .catch((err) => console.error("Error fetching patient profile:", err));
    }
  }, [searchParams]);

  const handleTranscriptionUpdate = (
    status: TranscriptionStatus,
    text: string,
    structuredData?: StructuredEhrData | null
  ) => {
    setTranscriptionStatus(status);
    setTranscriptionText(text);
    if (structuredData) {
      setStructuredEhr(structuredData);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100 font-sans print:bg-white print:text-slate-900 print:min-h-0">
      {/* Top Header / App Bar (Hidden on Print) */}
      <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-900/90 backdrop-blur-md px-6 py-4 print:hidden">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* Brand Logo & Name */}
          <div className="flex items-center gap-3">
            <Link href="/" className="flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 to-emerald-400 flex items-center justify-center text-slate-950 font-bold text-xl shadow-lg shadow-teal-500/20 group-hover:scale-105 transition-transform">
                ش
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-xl font-bold tracking-tight text-white group-hover:text-teal-300 transition-colors">
                    ShifaScribe
                  </h1>
                  <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
                    v0.4-Day28
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  AI Urdu Voice-to-Text &amp; Auto-Prescription Scribe
                </p>
              </div>
            </Link>
          </div>

          {/* Header Action Buttons & Navigation */}
          <div className="flex items-center gap-3">
            <Link
              href="/intake"
              className="px-3.5 py-1.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold flex items-center gap-1.5 transition-all shadow-md shadow-emerald-500/20 cursor-pointer"
            >
              <span>🏥</span>
              <span>New Patient Intake</span>
            </Link>

            <Link
              href="/history"
              className="px-3.5 py-1.5 rounded-xl bg-teal-950/60 hover:bg-teal-900/60 border border-teal-800/50 text-teal-300 text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm hover:border-teal-500/60 cursor-pointer"
            >
              <span>📋</span>
              <span>Patient History</span>
            </Link>

            <Link
              href="/dashboard"
              className="px-3.5 py-1.5 rounded-xl bg-cyan-950/60 hover:bg-cyan-900/60 border border-cyan-800/50 text-cyan-300 text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm hover:border-cyan-500/60 cursor-pointer"
            >
              <span>📊</span>
              <span>Surveillance</span>
            </Link>

            <div className="hidden lg:flex items-center gap-3 pl-2 border-l border-slate-800">
              <div className="px-3 py-1 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs">
                <span className="text-slate-400 block text-[10px]">Consultant Doctor</span>
                <span className="font-semibold text-slate-200">
                  Dr. Arsam Khan (General OPD)
                </span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-800/40 text-xs text-emerald-400 font-medium">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                Supabase DB Live
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Doctor Workspace Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 lg:p-8 flex flex-col gap-6 print:p-0 print:m-0 print:max-w-none">
        {/* Patient Quick Context Card (Hidden on Print) */}
        <section className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 md:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-lg print:hidden relative overflow-hidden">
          <div className="flex items-center gap-4">
            <div className="min-w-[4.5rem] px-3.5 h-12 rounded-2xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 font-bold text-base font-mono whitespace-nowrap shadow-sm">
              {patientToken}
            </div>
            <div>
              <div className="flex items-center gap-3 flex-wrap">
                <h2 className="text-lg font-bold text-white">
                  {patientName}
                </h2>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-mono">
                  {patientAge} yrs • {patientGender}
                </span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/30 font-mono">
                  ID #{patientId}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1 flex items-center gap-1.5">
                <span className="text-slate-500 font-medium">Chief Complaint:</span>
                <span className="text-slate-200 font-medium">
                  {chiefComplaint}
                </span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 self-end md:self-auto">
            <Link
              href="/intake"
              className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-teal-300 text-xs font-semibold border border-slate-700 transition-all cursor-pointer"
            >
              🔄 Change Patient / Intake
            </Link>
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Active Consultation</span>
            </span>
          </div>
        </section>

        {/* Center Panel: Recorder Component with integrated Transcription UI (Hidden on Print) */}
        <section className="my-2 flex flex-col items-center justify-center print:hidden">
          <ConsultationRecorder
            patientId={patientId}
            onStateChange={setCurrentRecordingState}
            onTranscriptionUpdate={handleTranscriptionUpdate}
          />
        </section>

        {/* Prescription Form Component (Contains interactive UI and A4 Print View) */}
        <section className="mt-2 print:m-0 print:p-0">
          <PrescriptionForm
            patientId={patientId}
            patientName={patientName}
            patientAge={patientAge}
            patientGender={patientGender}
            patientToken={patientToken}
            structuredData={structuredEhr}
            rawTranscript={transcriptionText}
            status={transcriptionStatus}
          />
        </section>

        {/* Live Audio Transcript Preview & Debug Card (Hidden on Print) */}
        <section className="grid grid-cols-1 gap-6 print:hidden">
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between shadow-lg">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-teal-400" />
                Raw Whisper AI Audio Transcript (Urdu)
              </h3>
              <span
                className={`text-xs font-mono px-2.5 py-0.5 rounded border ${
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
                {transcriptionStatus === "completed"
                  ? "AI Transcription Ready"
                  : transcriptionStatus === "processing_ai"
                  ? "Whisper AI Processing..."
                  : transcriptionStatus === "uploading"
                  ? "Uploading Audio..."
                  : transcriptionStatus === "failed"
                  ? "Transcription Error"
                  : "Awaiting Audio"}
              </span>
            </div>

            <div className="mt-4 min-h-[70px] flex items-center">
              {transcriptionText ? (
                <p className="text-sm text-slate-300 font-urdu leading-relaxed text-right w-full dir-rtl">
                  {transcriptionText}
                </p>
              ) : (
                <p className="text-xs text-slate-500 italic">
                  No audio transcribed yet. Click &quot;Start Recording&quot; above to capture Urdu clinical dialogue.
                </p>
              )}
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-900/60 py-6 text-center text-xs text-slate-500 print:hidden mt-auto">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>
            ShifaScribe © 2026 — Dual-Language AI Medical Scribe (DRAP Compliant)
          </div>
          <div className="font-mono text-slate-400">
            Day 28: Patient Intake Interface &amp; Supabase Write-Back
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function DoctorConsultScreen() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400 text-sm">
        <div className="flex items-center gap-3">
          <div className="w-6 h-6 border-2 border-teal-400 border-t-transparent rounded-full animate-spin"></div>
          <span>Loading ShifaScribe Consultation Screen...</span>
        </div>
      </div>
    }>
      <DoctorConsultScreenContent />
    </Suspense>
  );
}
