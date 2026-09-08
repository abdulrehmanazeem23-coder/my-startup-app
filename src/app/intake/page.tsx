"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface QuickPreset {
  name: string;
  age: number;
  gender: string;
  complaint: string;
}

const QUICK_PRESETS: QuickPreset[] = [
  { name: "Muhammad Tariq", age: 45, gender: "Male", complaint: "Severe headache & high fever for 2 days" },
  { name: "Fatima Zahra", age: 34, gender: "Female", complaint: "Productive cough, chest congestion, wheezing" },
  { name: "Zainab Bibi", age: 29, gender: "Female", complaint: "Watery diarrhea, vomiting, severe dehydration" },
  { name: "Ahmed Raza", age: 52, gender: "Male", complaint: "Generalized body aches, joint stiffness, malaise" },
];

export default function PatientIntakePage() {
  const router = useRouter();

  const [name, setName] = useState("");
  const [age, setAge] = useState<number | string>(42);
  const [gender, setGender] = useState("Male");
  const [opdToken, setOpdToken] = useState("");
  const [complaint, setComplaint] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successData, setSuccessData] = useState<any | null>(null);

  const handleApplyPreset = (preset: QuickPreset) => {
    setName(preset.name);
    setAge(preset.age);
    setGender(preset.gender);
    setComplaint(preset.complaint);
    setErrorMessage(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setErrorMessage("Please enter patient full name.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      const backendUrl = typeof window !== "undefined"
        ? `http://${window.location.hostname || "localhost"}:8000`
        : "http://localhost:8000";

      const res = await fetch(`${backendUrl}/api/patients/new`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: jsonBody(),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `Server returned status ${res.status}`);
      }

      const data = await res.json();
      setSuccessData(data);

      // Brief pause to show success animation then redirect to consultation screen
      setTimeout(() => {
        router.push(`/?patient_id=${data.patient_id}&name=${encodeURIComponent(data.name)}&token=${encodeURIComponent(data.opd_token)}&age=${data.age}&gender=${encodeURIComponent(data.gender)}&complaint=${encodeURIComponent(complaint || "OPD Routine Consultation")}`);
      }, 700);
    } catch (err: any) {
      console.error("Intake Error:", err);
      setErrorMessage(err.message || "Failed to register patient intake");
      setIsSubmitting(false);
    }
  };

  const jsonBody = () => {
    return JSON.stringify({
      name: name.trim(),
      age: Number(age) || 40,
      gender: gender || "Male",
      opd_token: opdToken.trim() || undefined,
    });
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-teal-500 selection:text-slate-950 flex flex-col">
      {/* Top Header */}
      <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-900/90 backdrop-blur-md px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 to-emerald-400 flex items-center justify-center text-slate-950 font-bold text-xl shadow-lg shadow-teal-500/20 group-hover:scale-105 transition-transform">
              ش
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold tracking-tight text-white group-hover:text-teal-300 transition-colors">
                  ShifaScribe
                </h1>
                <span className="text-xs px-2 py-0.5 rounded bg-teal-500/10 text-teal-400 border border-teal-500/20 font-mono">
                  Intake Day 28
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Patient Reception &amp; OPD Consultation Intake
              </p>
            </div>
          </Link>

          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm"
            >
              <span>🎙️</span>
              <span>OPD Live Scribe</span>
            </Link>
            <Link
              href="/history"
              className="px-3.5 py-1.5 rounded-xl bg-teal-950/60 hover:bg-teal-900/60 border border-teal-800/50 text-teal-300 text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm"
            >
              <span>📋</span>
              <span>Patient History</span>
            </Link>
            <Link
              href="/dashboard"
              className="px-3.5 py-1.5 rounded-xl bg-cyan-950/60 hover:bg-cyan-900/60 border border-cyan-800/50 text-cyan-300 text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm"
            >
              <span>📊</span>
              <span>Surveillance</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 py-10 space-y-8">
        {/* Title Card */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/10 border border-teal-500/30 text-teal-400 text-xs font-semibold font-mono">
            <span>🏥</span> New Patient Registration
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            OPD Patient Intake Interface
          </h2>
          <p className="text-sm text-slate-400 max-w-lg mx-auto">
            Register the patient to generate a secure OPD token, store the record in Supabase PostgreSQL, and launch the AI voice scribe consultation.
          </p>
        </div>

        {/* Quick Presets */}
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 shadow-md space-y-2.5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <span>⚡</span> Fast Intake Demo Presets
            </span>
            <span className="text-[11px] text-teal-400 font-mono">Click to auto-fill</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
            {QUICK_PRESETS.map((preset, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleApplyPreset(preset)}
                className="bg-slate-950/80 hover:bg-slate-800/80 border border-slate-800 hover:border-teal-500/50 rounded-xl p-2.5 text-left transition-all cursor-pointer group"
              >
                <div className="font-semibold text-xs text-white group-hover:text-teal-300 transition-colors">
                  {preset.name}
                </div>
                <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                  {preset.age} yrs • {preset.gender}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Main Intake Form Card */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl backdrop-blur-xl relative overflow-hidden">
          <div className="absolute -right-20 -top-20 w-64 h-64 bg-teal-500/10 rounded-full blur-3xl pointer-events-none"></div>

          <form onSubmit={handleSubmit} className="space-y-6 relative">
            {errorMessage && (
              <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center gap-2">
                <span>⚠️</span>
                <span>{errorMessage}</span>
              </div>
            )}

            {successData && (
              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
                <span>✓</span>
                <span>
                  Intake registered successfully! Token <strong>{successData.opd_token}</strong> (ID #{successData.patient_id}). Redirecting to Scribe...
                </span>
              </div>
            )}

            {/* Input Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              {/* Patient Full Name */}
              <div className="sm:col-span-2 space-y-1.5">
                <label className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center justify-between">
                  <span>Patient Full Name <span className="text-teal-400">*</span></span>
                  <span className="text-[11px] text-slate-500 font-normal">e.g. Muhammad Tariq</span>
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Enter full patient name..."
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-all font-medium"
                />
              </div>

              {/* Patient Age */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  Patient Age (Years)
                </label>
                <input
                  type="number"
                  min="1"
                  max="120"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  placeholder="e.g. 45"
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-all font-mono"
                />
              </div>

              {/* Patient Gender */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  Gender
                </label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-all cursor-pointer font-medium"
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other / Pediatric</option>
                </select>
              </div>

              {/* OPD Token (Optional / Auto) */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center justify-between">
                  <span>Custom OPD Token</span>
                  <span className="text-[11px] text-slate-500 font-normal">Leave blank for auto</span>
                </label>
                <input
                  type="text"
                  value={opdToken}
                  onChange={(e) => setOpdToken(e.target.value)}
                  placeholder="Auto-assigned (e.g. #105)"
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-all font-mono"
                />
              </div>

              {/* Attending Doctor */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  Attending Consultant
                </label>
                <div className="w-full bg-slate-950/60 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-300 font-medium flex items-center justify-between">
                  <span>Dr. Arsam Khan</span>
                  <span className="text-[11px] font-mono text-teal-400 bg-teal-950/60 px-2 py-0.5 rounded border border-teal-800/40">Room #4</span>
                </div>
              </div>

              {/* Initial Chief Complaint / Notes */}
              <div className="sm:col-span-2 space-y-1.5">
                <label className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center justify-between">
                  <span>Initial Chief Complaint / Triage Note</span>
                  <span className="text-[11px] text-slate-500 font-normal">Optional</span>
                </label>
                <textarea
                  rows={2}
                  value={complaint}
                  onChange={(e) => setComplaint(e.target.value)}
                  placeholder="e.g. High grade fever, rigors, body pain for 3 days..."
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-all resize-none"
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="pt-4 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-slate-800">
              <div className="text-xs text-slate-400 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Live Supabase PostgreSQL Write-Back Ready</span>
              </div>

              <div className="flex items-center gap-3 w-full sm:w-auto">
                <button
                  type="button"
                  onClick={() => {
                    setName("");
                    setComplaint("");
                    setOpdToken("");
                  }}
                  className="px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-all cursor-pointer"
                >
                  Clear
                </button>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex-1 sm:flex-none px-8 py-3 rounded-xl bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-slate-950 font-bold text-sm flex items-center justify-center gap-2 transition-all shadow-lg shadow-teal-500/20 disabled:opacity-50 cursor-pointer"
                >
                  {isSubmitting ? (
                    <>
                      <span className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></span>
                      <span>Creating Patient Record...</span>
                    </>
                  ) : (
                    <>
                      <span>Start Consultation</span>
                      <span>🎙️ →</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-900/60 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>
            ShifaScribe © 2026 — Patient Intake &amp; Real-time AI Scribe
          </div>
          <div className="font-mono text-slate-400">
            Day 28: Patient Intake &amp; Database Write-Back
          </div>
        </div>
      </footer>
    </div>
  );
}
