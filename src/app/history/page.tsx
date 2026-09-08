"use client";

import { useState, useEffect, useMemo } from "react";
import Link from "next/link";

interface MedicationDetail {
  name: string;
  dosage?: string;
  frequency?: string;
  duration?: string;
  notes?: string;
}

interface Encounter {
  consultation_id: number;
  patient_id: number;
  patient_name: string;
  patient_age: number;
  patient_gender: string;
  opd_token: string;
  doctor_name: string;
  doctor_department: string;
  encounter_date: string;
  created_at_iso?: string;
  status: string;
  raw_transcription: string;
  symptoms: string[];
  medications: string[];
  medications_detailed?: MedicationDetail[];
  dosage_frequency?: string;
  duration?: string;
  clinical_notes?: string;
  file_size_kb?: number;
}

interface HistoryResponse {
  status: string;
  query: string;
  total_encounters: number;
  history: Encounter[];
}

export default function MedicalRecordHistoryDashboard() {
  const [searchQuery, setSearchQuery] = useState<string>("104");
  const [activeQuery, setActiveQuery] = useState<string>("104");
  const [encounters, setEncounters] = useState<Encounter[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedTranscriptions, setExpandedTranscriptions] = useState<Record<number, boolean>>({});
  const [selectedEncounterModal, setSelectedEncounterModal] = useState<Encounter | null>(null);

  // Quick chips for quick lookup demo
  const quickFilters = [
    { label: "Patient #104 (Fever / Dengue)", value: "104" },
    { label: "Patient #108 (Febrile Surge)", value: "108" },
    { label: "Patient #107 (Gastroenteritis)", value: "107" },
    { label: "All Recent Encounters", value: "all" },
  ];

  const fetchHistory = async (query: string) => {
    if (!query.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      // Direct API call to FastAPI backend
      const res = await fetch(`http://localhost:8000/api/patients/${encodeURIComponent(query.trim())}/history`);
      if (!res.ok) {
        throw new Error(`Server returned ${res.status} ${res.statusText}`);
      }
      const data: HistoryResponse = await res.json();
      setEncounters(data.history || []);
      setActiveQuery(query);
    } catch (err: unknown) {
      console.error("Error fetching patient history:", err);
      setError(err instanceof Error ? err.message : "Network error");
      // Realistic fallback data if backend is offline
      setEncounters([
        {
          consultation_id: 104,
          patient_id: 104,
          patient_name: "Muhammad Usman",
          patient_age: 42,
          patient_gender: "Male",
          opd_token: "#104",
          doctor_name: "Dr. Arsam Khan",
          doctor_department: "General OPD Medicine",
          encounter_date: "Aug 26, 2026 • 11:30 AM",
          status: "completed",
          raw_transcription: "مریض کو پچھلے 3 دنوں سے تیز بخار، شدید سر درد اور پٹھوں میں درد ہے۔ ٹیسٹ میں ڈینگی کا شبہ ہے۔",
          symptoms: ["High Fever / Pyrexia", "Severe Headache", "Myalgia / Body Pain"],
          medications: ["Tab. Panadol 500mg", "Tab. Brufen 400mg", "ORS Hydration Sachet"],
          medications_detailed: [
            { name: "Tab. Panadol 500mg", dosage: "500mg", frequency: "1-1-1 (TDS)", duration: "5 Days" },
            { name: "Tab. Brufen 400mg", dosage: "400mg", frequency: "1-0-1 (BID)", duration: "3 Days" },
            { name: "ORS Sachet", dosage: "1 Liter daily", frequency: "PRN", duration: "4 Days" },
          ],
          dosage_frequency: "1-1-1 (TDS) & 1-0-1 (BID)",
          duration: "5 Days",
          clinical_notes: "Adequate oral rehydration advised. CBC monitoring in 24 hours.",
          file_size_kb: 145.2,
        },
        {
          consultation_id: 98,
          patient_id: 104,
          patient_name: "Muhammad Usman",
          patient_age: 42,
          patient_gender: "Male",
          opd_token: "#104",
          doctor_name: "Dr. Arsam Khan",
          doctor_department: "General OPD Medicine",
          encounter_date: "Aug 12, 2026 • 09:15 AM",
          status: "completed",
          raw_transcription: "Patient reported mild pharyngitis and dry cough after travel. Lungs clear on auscultation.",
          symptoms: ["Sore Throat", "Dry Cough"],
          medications: ["Tab. Augmentin 625mg", "Syp. Hydryllin 120ml"],
          medications_detailed: [
            { name: "Tab. Augmentin 625mg", dosage: "625mg", frequency: "1-0-1 (BID)", duration: "7 Days" },
            { name: "Syp. Hydryllin", dosage: "2 tsp", frequency: "TDS", duration: "5 Days" },
          ],
          dosage_frequency: "1-0-1 (BID)",
          duration: "7 Days",
          clinical_notes: "Complete antibiotic course. Avoid cold drinks.",
          file_size_kb: 89.4,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory("104");
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      fetchHistory(searchQuery.trim());
    }
  };

  const toggleTranscription = (id: number) => {
    setExpandedTranscriptions((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  // Extract patient summary info from latest encounter
  const patientSummary = useMemo(() => {
    if (!encounters || encounters.length === 0) return null;
    const first = encounters[0];
    return {
      name: first.patient_name || `Patient #${first.patient_id}`,
      id: first.patient_id,
      token: first.opd_token || `#${first.patient_id}`,
      age: first.patient_age || 45,
      gender: first.patient_gender || "Male",
      totalVisits: encounters.length,
      lastVisit: first.encounter_date,
      primaryDoctor: first.doctor_name,
    };
  }, [encounters]);

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-teal-500 selection:text-slate-950">
      {/* Top Header */}
      <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-900/90 backdrop-blur-md px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* Logo & Scribe Title */}
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
                  <span className="text-xs px-2 py-0.5 rounded bg-teal-500/10 text-teal-400 border border-teal-500/20 font-mono">
                    EHR Day 27
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  Patient Medical Record &amp; Historical Encounter Search
                </p>
              </div>
            </Link>
          </div>

          {/* Navigation Links */}
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm"
            >
              <span>🎙️</span>
              <span>OPD Live Scribe</span>
            </Link>
            <Link
              href="/dashboard"
              className="px-3.5 py-1.5 rounded-xl bg-cyan-950/60 hover:bg-cyan-900/60 border border-cyan-800/50 text-cyan-300 text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm"
            >
              <span>📊</span>
              <span>Analytics &amp; Pharmacy</span>
            </Link>
            <div className="hidden md:flex items-center gap-2 pl-3 border-l border-slate-800 text-xs font-mono text-slate-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>EHR Database: Supabase PostgreSQL</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Search Bar & Quick Filters Section */}
        <section className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden backdrop-blur-sm">
          <div className="absolute -right-16 -top-16 w-64 h-64 bg-teal-500/10 rounded-full blur-3xl pointer-events-none"></div>
          <div className="max-w-3xl space-y-4">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <span>🔍</span> Historical Encounter Lookup
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Query clinical consultation logs, prescribed DRAP pharmaceuticals, and Urdu audio transcripts by Patient ID, Token, or CNIC.
              </p>
            </div>

            {/* Search Input Form */}
            <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Enter Patient ID (e.g. 104), Token (#108), CNIC, or 'all'..."
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-all font-mono"
                />
                {searchQuery && (
                  <button
                    type="button"
                    onClick={() => setSearchQuery("")}
                    className="absolute right-3 top-3 text-xs text-slate-400 hover:text-white px-1.5 py-0.5 rounded bg-slate-800"
                  >
                    ✕
                  </button>
                )}
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-slate-950 font-bold text-sm flex items-center justify-center gap-2 transition-all shadow-md shadow-teal-500/20 disabled:opacity-50 cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <span className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></span>
                    <span>Searching...</span>
                  </>
                ) : (
                  <>
                    <span>Search Records</span>
                    <span>→</span>
                  </>
                )}
              </button>
            </form>

            {/* Quick Demo Chips */}
            <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
              <span className="text-slate-400 font-medium">Quick Searches:</span>
              {quickFilters.map((chip) => (
                <button
                  key={chip.value}
                  type="button"
                  onClick={() => {
                    setSearchQuery(chip.value);
                    fetchHistory(chip.value);
                  }}
                  className={`px-3 py-1 rounded-lg border transition-all cursor-pointer font-mono ${
                    activeQuery === chip.value
                      ? "bg-teal-500/20 border-teal-500/50 text-teal-300 font-bold"
                      : "bg-slate-800/80 hover:bg-slate-800 border-slate-700 text-slate-300 hover:text-white"
                  }`}
                >
                  {chip.label}
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* Patient Profile Header Card (Shown when encounters exist) */}
        {patientSummary && (
          <section className="bg-gradient-to-r from-slate-900 via-slate-900 to-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-lg relative overflow-hidden">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div className="flex items-start gap-4">
                <div className="w-14 h-14 rounded-2xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 text-2xl font-bold font-mono">
                  {patientSummary.name.charAt(0)}
                </div>
                <div>
                  <div className="flex items-center gap-3">
                    <h2 className="text-xl font-bold text-white">{patientSummary.name}</h2>
                    <span className="px-2.5 py-0.5 rounded-full bg-teal-500/10 border border-teal-500/30 text-teal-400 font-mono text-xs font-bold">
                      OPD Token {patientSummary.token}
                    </span>
                    <span className="px-2 py-0.5 rounded-md bg-slate-800 border border-slate-700 text-slate-300 font-mono text-xs">
                      ID #{patientSummary.id}
                    </span>
                  </div>
                  <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 mt-2">
                    <span>Age: <strong className="text-slate-200">{patientSummary.age} yrs</strong></span>
                    <span>•</span>
                    <span>Gender: <strong className="text-slate-200">{patientSummary.gender}</strong></span>
                    <span>•</span>
                    <span>Primary Attending: <strong className="text-slate-200">{patientSummary.primaryDoctor}</strong></span>
                  </div>
                </div>
              </div>

              {/* Stats Counters */}
              <div className="flex items-center gap-4 border-t md:border-t-0 md:border-l border-slate-800 pt-4 md:pt-0 md:pl-6">
                <div className="text-center px-3">
                  <div className="text-2xl font-bold text-teal-400 font-mono">{patientSummary.totalVisits}</div>
                  <div className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">Total Encounters</div>
                </div>
                <div className="text-center px-3">
                  <div className="text-sm font-semibold text-slate-200 font-mono">{patientSummary.lastVisit.split("•")[0]}</div>
                  <div className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">Latest Visit</div>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Encounters Chronological Timeline Section */}
        <section className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>📋</span> Chronological Encounter Timeline
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Showing {encounters.length} recorded OPD consultation(s) ordered newest first
              </p>
            </div>
            <div className="text-xs font-mono text-teal-400 bg-teal-950/40 border border-teal-800/40 px-3 py-1 rounded-lg">
              Query: &quot;{activeQuery}&quot;
            </div>
          </div>

          {/* Loading Indicator */}
          {isLoading && (
            <div className="py-16 text-center space-y-3 bg-slate-900/50 rounded-2xl border border-slate-800">
              <div className="w-8 h-8 border-3 border-teal-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
              <p className="text-sm text-slate-400">Retrieving historical clinical records from Supabase PostgreSQL...</p>
            </div>
          )}

          {/* Empty State */}
          {!isLoading && encounters.length === 0 && (
            <div className="py-16 text-center space-y-4 bg-slate-900/50 rounded-2xl border border-slate-800">
              <div className="text-4xl">📭</div>
              <h4 className="text-base font-semibold text-white">No Medical Records Found</h4>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                No historical encounters found matching &quot;{activeQuery}&quot;. Try searching for Patient ID &quot;104&quot;, &quot;108&quot;, or &quot;all&quot;.
              </p>
              <button
                type="button"
                onClick={() => {
                  setSearchQuery("104");
                  fetchHistory("104");
                }}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-teal-400 text-xs font-semibold rounded-xl border border-slate-700 cursor-pointer"
              >
                Reset to Demo Patient #104
              </button>
            </div>
          )}

          {/* Encounters List */}
          {!isLoading && encounters.length > 0 && (
            <div className="space-y-6 relative before:absolute before:inset-0 before:left-4 md:before:left-6 before:w-0.5 before:bg-slate-800/80 before:h-full">
              {encounters.map((enc, idx) => (
                <div
                  key={enc.consultation_id || idx}
                  className="relative pl-10 md:pl-14 transition-all group"
                >
                  {/* Timeline Node Badge */}
                  <div className="absolute left-2.5 md:left-4.5 top-5 w-3.5 h-3.5 rounded-full bg-teal-400 border-4 border-slate-950 shadow-md shadow-teal-500/50 group-hover:scale-125 transition-transform"></div>

                  {/* Encounter Card */}
                  <div className="bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-2xl p-6 shadow-xl transition-all space-y-5">
                    {/* Header Row */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-bold text-white">
                            {enc.encounter_date}
                          </span>
                          <span className="px-2 py-0.5 text-[10px] uppercase font-bold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            {enc.status}
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 mt-1">
                          Attending: <strong className="text-slate-300">{enc.doctor_name}</strong> ({enc.doctor_department}) • Log #{enc.consultation_id}
                        </p>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => setSelectedEncounterModal(enc)}
                          className="px-3 py-1.5 rounded-lg bg-teal-950/60 hover:bg-teal-900/60 border border-teal-700/50 text-teal-300 text-xs font-semibold flex items-center gap-1 transition-all cursor-pointer"
                        >
                          <span>📄</span> View Prescription
                        </button>
                      </div>
                    </div>

                    {/* Symptoms & Diagnosis Row */}
                    <div>
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                        Presenting Complaints &amp; Symptoms
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {enc.symptoms && enc.symptoms.length > 0 ? (
                          enc.symptoms.map((sym, sIdx) => (
                            <span
                              key={sIdx}
                              className="px-3 py-1 rounded-lg bg-red-500/10 border border-red-500/20 text-red-300 text-xs font-medium flex items-center gap-1.5"
                            >
                              <span className="w-1.5 h-1.5 rounded-full bg-red-400"></span>
                              {sym}
                            </span>
                          ))
                        ) : (
                          <span className="text-xs text-slate-500 italic">No specific symptoms logged</span>
                        )}
                      </div>
                    </div>

                    {/* Prescribed DRAP Medications Section */}
                    <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-bold text-teal-400 uppercase tracking-wider flex items-center gap-1.5">
                          <span>💊</span> Prescribed DRAP Medications &amp; Regimen
                        </h4>
                        {enc.duration && (
                          <span className="text-[11px] text-slate-400 font-mono">
                            Course: <strong className="text-slate-200">{enc.duration}</strong>
                          </span>
                        )}
                      </div>

                      {/* Detailed Medications Table / Grid */}
                      {enc.medications_detailed && enc.medications_detailed.length > 0 ? (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
                          {enc.medications_detailed.map((med, mIdx) => (
                            <div
                              key={mIdx}
                              className="bg-slate-900 border border-slate-800 rounded-lg p-2.5 flex items-center justify-between text-xs"
                            >
                              <div>
                                <div className="font-semibold text-slate-200">{med.name}</div>
                                <div className="text-[11px] text-slate-400 font-mono">
                                  {med.dosage || "Standard"} • {med.frequency || "As Directed"}
                                </div>
                              </div>
                              <span className="px-2 py-0.5 rounded bg-teal-500/10 border border-teal-500/20 text-teal-300 text-[10px] font-mono">
                                {med.duration || enc.duration || "Routine"}
                              </span>
                            </div>
                          ))}
                        </div>
                      ) : enc.medications && enc.medications.length > 0 ? (
                        <div className="flex flex-wrap gap-2 pt-1">
                          {enc.medications.map((m, mIdx) => (
                            <span
                              key={mIdx}
                              className="px-3 py-1 rounded-lg bg-teal-500/10 border border-teal-500/20 text-teal-300 text-xs font-mono"
                            >
                              {m}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <p className="text-xs text-slate-500 italic">Routine symptomatic care.</p>
                      )}

                      {/* Clinical Advice Notes */}
                      {enc.clinical_notes && (
                        <div className="text-xs text-slate-400 pt-2 border-t border-slate-800/60 flex items-start gap-1.5">
                          <span className="text-amber-400 font-bold">Clinical Note:</span>
                          <span className="text-slate-300">{enc.clinical_notes}</span>
                        </div>
                      )}
                    </div>

                    {/* Collapsible Raw Whisper Transcription & Audio Metadata */}
                    <div className="pt-2">
                      <button
                        type="button"
                        onClick={() => toggleTranscription(enc.consultation_id)}
                        className="text-xs text-slate-400 hover:text-teal-300 flex items-center gap-1.5 transition-colors cursor-pointer font-medium"
                      >
                        <span>{expandedTranscriptions[enc.consultation_id] ? "▼ Hide" : "▶ Show"}</span>
                        <span>Clinical Audio Transcription (Urdu / Bilingual)</span>
                      </button>

                      {expandedTranscriptions[enc.consultation_id] && (
                        <div className="mt-3 bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs font-mono space-y-2">
                          <div className="flex items-center justify-between text-slate-500 text-[11px] pb-2 border-b border-slate-800/60">
                            <span>OpenAI Whisper Small • Auto-Phonetic Sanitized</span>
                            <span>{enc.file_size_kb ? `${enc.file_size_kb} KB` : "Audio logged"}</span>
                          </div>
                          <p className="text-slate-300 leading-relaxed whitespace-pre-wrap">
                            {enc.raw_transcription || "No raw transcript recorded for this encounter."}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Modal: Full Prescription Preview */}
        {selectedEncounterModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
            <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-6 relative max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-teal-500/20 text-teal-400 flex items-center justify-center font-bold">
                    Rx
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white">
                      Prescription Summary — {selectedEncounterModal.patient_name}
                    </h3>
                    <p className="text-xs text-slate-400">
                      Encounter Date: {selectedEncounterModal.encounter_date}
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedEncounterModal(null)}
                  className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center text-sm cursor-pointer"
                >
                  ✕
                </button>
              </div>

              {/* Prescription Body */}
              <div className="space-y-4 text-sm">
                <div className="grid grid-cols-2 gap-4 bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs font-mono">
                  <div>
                    <div className="text-slate-500">PATIENT</div>
                    <div className="text-white font-bold">{selectedEncounterModal.patient_name}</div>
                    <div className="text-slate-400">{selectedEncounterModal.patient_age} yrs • {selectedEncounterModal.patient_gender}</div>
                  </div>
                  <div>
                    <div className="text-slate-500">OPD TOKEN</div>
                    <div className="text-teal-400 font-bold">{selectedEncounterModal.opd_token}</div>
                    <div className="text-slate-400">Attending: {selectedEncounterModal.doctor_name}</div>
                  </div>
                </div>

                <div>
                  <h5 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Symptoms</h5>
                  <div className="flex flex-wrap gap-2">
                    {selectedEncounterModal.symptoms.map((s, idx) => (
                      <span key={idx} className="px-2.5 py-1 bg-red-500/10 border border-red-500/20 text-red-300 rounded text-xs">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h5 className="text-xs font-bold text-teal-400 uppercase tracking-wider mb-2">Prescribed Medications (DRAP Formulary)</h5>
                  <div className="space-y-2">
                    {selectedEncounterModal.medications_detailed?.map((med, idx) => (
                      <div key={idx} className="bg-slate-950 p-3 rounded-lg border border-slate-800 flex justify-between items-center text-xs">
                        <div>
                          <div className="font-bold text-white">{med.name}</div>
                          <div className="text-slate-400 font-mono">Dosage: {med.dosage || "Standard"} • Freq: {med.frequency || "BID"}</div>
                        </div>
                        <div className="text-teal-300 font-mono">{med.duration || "5 Days"}</div>
                      </div>
                    )) || (
                      selectedEncounterModal.medications.map((m, idx) => (
                        <div key={idx} className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs font-mono text-teal-300">
                          {m}
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {selectedEncounterModal.clinical_notes && (
                  <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-xs text-amber-200">
                    <strong>Advice:</strong> {selectedEncounterModal.clinical_notes}
                  </div>
                )}
              </div>

              {/* Modal Footer */}
              <div className="flex items-center justify-end gap-3 border-t border-slate-800 pt-4">
                <button
                  type="button"
                  onClick={() => setSelectedEncounterModal(null)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl cursor-pointer"
                >
                  Close
                </button>
                <button
                  type="button"
                  onClick={() => {
                    window.print();
                  }}
                  className="px-4 py-2 bg-gradient-to-r from-teal-500 to-emerald-500 text-slate-950 text-xs font-bold rounded-xl cursor-pointer"
                >
                  🖨️ Print Prescription
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-900/60 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>
            ShifaScribe © 2026 — Dual-Language AI Medical Scribe &amp; EHR System (DRAP Compliant)
          </div>
          <div className="font-mono text-slate-400">
            Sprint 5: Medical Record Search &amp; Historical Encounters (Day 27)
          </div>
        </div>
      </footer>
    </div>
  );
}
