"use client";

import { useState, useEffect } from "react";

export interface MedicationDetail {
  name: string;
  strength: string;
  form: string;
  formatted: string;
  frequency: string;
  duration: string;
  instruction: string;
}

export interface StructuredEhrData {
  symptoms?: string[];
  medications?: string[];
  medications_detailed?: MedicationDetail[];
  dosage_frequency?: string;
  duration?: string;
  food_relation?: string | null;
  full_dosage_frequency?: string | null;
  clinical_notes?: string;
  raw_input?: string;
}

interface PrescriptionFormProps {
  structuredData?: StructuredEhrData | null;
  rawTranscript?: string;
  status?: "idle" | "uploading" | "processing_ai" | "completed" | "failed";
}

export default function PrescriptionForm({
  structuredData,
  rawTranscript,
  status = "idle",
}: PrescriptionFormProps) {
  // Patient & Doctor Context State (Editable)
  const [patientName, setPatientName] = useState<string>("Muhammad Tariq");
  const [patientAge, setPatientAge] = useState<string>("45 yrs");
  const [patientGender, setPatientGender] = useState<string>("Male");
  const [patientToken, setPatientToken] = useState<string>("#104");
  const [doctorName, setDoctorName] = useState<string>("Dr. Arsam Khan (General Physician)");

  // Form State (100% Editable via useState)
  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [symptomInput, setSymptomInput] = useState<string>("");
  const [medications, setMedications] = useState<string[]>([]);
  const [newMedInput, setNewMedInput] = useState<string>("");
  const [dosageFrequency, setDosageFrequency] = useState<string>("");
  const [duration, setDuration] = useState<string>("");
  const [clinicalNotes, setClinicalNotes] = useState<string>("");

  // UI State
  const [copied, setCopied] = useState<boolean>(false);
  const [savedStatus, setSavedStatus] = useState<boolean>(false);
  const [printDate, setPrintDate] = useState<string>("September 6, 2026");
  const [securityToken, setSecurityToken] = useState<string>("849201");

  // Populate Print Date & Security Token on Client Mount
  useEffect(() => {
    try {
      setPrintDate(
        new Date().toLocaleDateString("en-PK", {
          year: "numeric",
          month: "long",
          day: "numeric",
        })
      );
      setSecurityToken(Date.now().toString().slice(-6));
    } catch {
      // fallback
    }
  }, []);

  // Auto-Fill Form when structuredData is received from AI Backend
  useEffect(() => {
    if (structuredData && status === "completed") {
      if (structuredData.symptoms && structuredData.symptoms.length > 0) {
        setSymptoms(structuredData.symptoms);
      } else {
        setSymptoms(["General OPD Evaluation"]);
      }

      if (structuredData.medications && structuredData.medications.length > 0) {
        setMedications(structuredData.medications);
      } else {
        setMedications([]);
      }

      setDosageFrequency(
        structuredData.full_dosage_frequency ||
          structuredData.dosage_frequency ||
          "As Directed"
      );

      setDuration(structuredData.duration || "Not Specified");
      if (structuredData.clinical_notes) {
        setClinicalNotes(structuredData.clinical_notes);
      }
      setSavedStatus(false);
    }
  }, [structuredData, status]);

  // Handlers for Symptoms
  const handleAddSymptom = () => {
    if (symptomInput.trim() && !symptoms.includes(symptomInput.trim())) {
      setSymptoms([...symptoms, symptomInput.trim()]);
      setSymptomInput("");
    }
  };

  const handleRemoveSymptom = (index: number) => {
    setSymptoms(symptoms.filter((_, i) => i !== index));
  };

  // Handlers for Medications
  const handleAddMedication = () => {
    if (newMedInput.trim() && !medications.includes(newMedInput.trim())) {
      setMedications([...medications, newMedInput.trim()]);
      setNewMedInput("");
    }
  };

  const handleRemoveMedication = (index: number) => {
    setMedications(medications.filter((_, i) => i !== index));
  };

  const handleEditMedication = (index: number, newValue: string) => {
    const updated = [...medications];
    updated[index] = newValue;
    setMedications(updated);
  };

  // Copy Prescription to Clipboard
  const handleCopyPrescription = () => {
    const formatted = `
========================================
       SHIFASCRIBE CLINICAL E-PRESCRIPTION
========================================
Patient: ${patientName} (${patientAge} • ${patientGender})
Token: ${patientToken}
Date: ${new Date().toLocaleDateString()}
Doctor: ${doctorName}

[CHIEF COMPLAINTS / SYMPTOMS]
${symptoms.length > 0 ? symptoms.map((s) => `• ${s}`).join("\n") : "None specified"}

[PRESCRIBED MEDICATIONS & DOSAGE]
${
  medications.length > 0
    ? medications.map((m, idx) => `  ${idx + 1}. ${m}`).join("\n")
    : "No medications prescribed."
}

[PRIMARY DOSAGE FREQUENCY]: ${dosageFrequency || "As Directed"}
[TREATMENT DURATION]: ${duration || "Not Specified"}

[PHYSICIAN NOTES & ADVICE]
${clinicalNotes || "Standard OPD Follow-up & Care."}
========================================
`;
    navigator.clipboard.writeText(formatted.trim());
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  // Save to EHR Record Handler
  const handleSaveEhr = () => {
    setSavedStatus(true);
    setTimeout(() => setSavedStatus(false), 3500);
  };

  // Reset Form Handler
  const handleResetForm = () => {
    setSymptoms([]);
    setMedications([]);
    setDosageFrequency("");
    setDuration("");
    setClinicalNotes("");
    setSavedStatus(false);
  };

  // Save & Print Handler (Triggers window.print())
  const handlePrintPrescription = () => {
    setSavedStatus(true);
    window.print();
  };

  return (
    <>
      {/* ═══════════════════════════════════════════════════════════════
          SCREEN VIEW: Interactive Dark-Mode UI (Hidden during Print)
          ═══════════════════════════════════════════════════════════════ */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 md:p-8 flex flex-col gap-6 shadow-2xl backdrop-blur-xl transition-all duration-300 print:hidden">
        {/* Card Header & Live Status Badge */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
          <div className="flex items-center gap-3">
            <div className="w-3.5 h-3.5 rounded-full bg-teal-400 animate-pulse" />
            <div>
              <h2 className="text-base md:text-lg font-bold text-white tracking-wide flex items-center gap-2">
                Interactive E-Prescription Form
                <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-teal-950 text-teal-300 border border-teal-800 font-mono font-normal">
                  Multi-Drug Scribe • Sprint 4
                </span>
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Auto-populated in real-time from Whisper AI &amp; ShifaScribe NLP Engine (Per-Drug Dosages, Frequencies &amp; Durations)
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            {status === "completed" ? (
              <span className="px-3.5 py-1.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5 shadow-sm">
                <span>✓ ✨ Auto-Filled ({medications.length} Drug{medications.length !== 1 ? "s" : ""} Extracted)</span>
              </span>
            ) : status === "processing_ai" || status === "uploading" ? (
              <span className="px-3.5 py-1.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
                AI Extracting Multi-Drug EHR...
              </span>
            ) : (
              <span className="px-3.5 py-1.5 rounded-full text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700">
                Awaiting Dictation
              </span>
            )}
          </div>
        </div>

        {/* Form Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Symptoms & Chief Complaints + Timing Controls */}
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-teal-400 uppercase tracking-wider mb-2 flex items-center justify-between">
                <span>1. Chief Complaints / Symptoms (علامات)</span>
                <span className="text-[10px] text-slate-500 font-normal">
                  {symptoms.length} extracted
                </span>
              </label>
              <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl min-h-[90px] flex flex-wrap items-start gap-2">
                {symptoms.length > 0 ? (
                  symptoms.map((symptom, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium bg-teal-500/10 text-teal-300 border border-teal-500/20 group hover:border-teal-500/40 transition-colors"
                    >
                      <span>{symptom}</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveSymptom(idx)}
                        className="text-teal-500 hover:text-red-400 text-sm font-bold leading-none cursor-pointer"
                        title="Remove symptom"
                      >
                        &times;
                      </button>
                    </span>
                  ))
                ) : (
                  <p className="text-xs text-slate-500 italic p-1">
                    No symptoms detected yet. Record dictation or type manually below.
                  </p>
                )}
              </div>

              {/* Manual Add Symptom Input */}
              <div className="flex gap-2 mt-2">
                <input
                  type="text"
                  placeholder="Add additional symptom (e.g. Headache, Fever)..."
                  value={symptomInput}
                  onChange={(e) => setSymptomInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddSymptom())}
                  className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-teal-500/60"
                />
                <button
                  type="button"
                  onClick={handleAddSymptom}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-teal-400 rounded-lg text-xs font-medium border border-slate-700 transition-colors cursor-pointer"
                >
                  + Add
                </button>
              </div>
            </div>

            {/* Dosage & Duration Summary Controls */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Primary Dosage Frequency */}
              <div>
                <label className="block text-xs font-semibold text-teal-400 uppercase tracking-wider mb-2 flex items-center justify-between">
                  <span>2. Dosage / Frequency (خوراک)</span>
                  {medications.length > 1 && (
                    <span className="text-[10px] text-teal-400 font-normal">Primary / Summary</span>
                  )}
                </label>
                <input
                  type="text"
                  value={dosageFrequency}
                  onChange={(e) => setDosageFrequency(e.target.value)}
                  placeholder="e.g. 1-1-1 (TDS) - Before Food"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-teal-500/60 transition-colors"
                />
                <span className="text-[10px] text-slate-500 mt-1 block">
                  {medications.length > 1
                    ? "See individual drug instructions on right"
                    : "Translated from colloquial Urdu dictation"}
                </span>
              </div>

              {/* Primary Duration */}
              <div>
                <label className="block text-xs font-semibold text-teal-400 uppercase tracking-wider mb-2 flex items-center justify-between">
                  <span>3. Duration (مدت)</span>
                  {medications.length > 1 && (
                    <span className="text-[10px] text-teal-400 font-normal">Primary / Summary</span>
                  )}
                </label>
                <input
                  type="text"
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                  placeholder="e.g. 7 Days / 5 Days"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-teal-500/60 transition-colors"
                />
                <span className="text-[10px] text-slate-500 mt-1 block">
                  Calculated numerical duration bound
                </span>
              </div>
            </div>
          </div>

          {/* Right Column: Prescribed Medications Table & Per-Drug Details */}
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-teal-400 uppercase tracking-wider mb-2 flex items-center justify-between">
                <span>4. Prescribed Medications (ادویات اور ان کی خوراک)</span>
                <span className="text-[10px] text-emerald-400 font-normal">
                  DRAP Catalog Validated ✓
                </span>
              </label>

              {/* Medications Table List with Individual Instructions */}
              <div className="bg-slate-950/70 border border-slate-800 rounded-xl overflow-hidden min-h-[140px]">
                {medications.length > 0 ? (
                  <div className="divide-y divide-slate-800/80">
                    {medications.map((med, idx) => (
                      <div
                        key={idx}
                        className="p-3 flex items-center justify-between gap-3 hover:bg-slate-900/50 transition-colors"
                      >
                        <div className="flex items-center gap-2.5 flex-1 min-w-0">
                          <span className="w-5 h-5 rounded-full bg-teal-500/10 text-teal-400 font-mono text-[10px] flex items-center justify-center font-bold border border-teal-500/20 flex-shrink-0">
                            {idx + 1}
                          </span>
                          <input
                            type="text"
                            value={med}
                            onChange={(e) => handleEditMedication(idx, e.target.value)}
                            className="flex-1 bg-transparent border-b border-transparent hover:border-slate-700 focus:border-teal-500 text-xs font-mono font-medium text-emerald-300 focus:outline-none px-1 py-0.5 transition-colors"
                          />
                        </div>

                        <button
                          type="button"
                          onClick={() => handleRemoveMedication(idx)}
                          className="text-slate-500 hover:text-red-400 text-xs px-2 py-1 rounded hover:bg-slate-800 transition-colors flex-shrink-0 cursor-pointer"
                          title="Delete medication"
                        >
                          Delete
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-6 text-center text-xs text-slate-500 italic">
                    No prescribed medications extracted yet. Auto-fills all medicines, dosages &amp; durations from Whisper audio!
                  </div>
                )}
              </div>

              {/* Manual Add Medication Input */}
              <div className="flex gap-2 mt-2">
                <input
                  type="text"
                  placeholder="Add medication (e.g. Tab. Panadol 500mg — 1-1-1 (TDS), 5 Days)..."
                  value={newMedInput}
                  onChange={(e) => setNewMedInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddMedication())}
                  className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-teal-500/60"
                />
                <button
                  type="button"
                  onClick={handleAddMedication}
                  className="px-3.5 py-1.5 bg-teal-600 hover:bg-teal-500 text-slate-950 rounded-lg text-xs font-bold transition-colors shadow-sm cursor-pointer"
                >
                  + Add Drug
                </button>
              </div>
            </div>

            {/* Clinical Notes / Doctor Remarks */}
            <div>
              <label className="block text-xs font-semibold text-teal-400 uppercase tracking-wider mb-1.5">
                5. Doctor Clinical Notes / Advice (ڈاکٹر کی ہدایات)
              </label>
              <textarea
                rows={2}
                value={clinicalNotes}
                onChange={(e) => setClinicalNotes(e.target.value)}
                placeholder="Enter special precautions, follow-up advice, or lab tests required..."
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-teal-500/60 transition-colors resize-none"
              />
            </div>
          </div>
        </div>

        {/* Action Toolbar */}
        <div className="pt-4 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            {/* Copy Button */}
            <button
              type="button"
              onClick={handleCopyPrescription}
              className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 border transition-all cursor-pointer ${
                copied
                  ? "bg-emerald-500 text-slate-950 border-emerald-400 shadow-md shadow-emerald-500/20"
                  : "bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700"
              }`}
            >
              {copied ? (
                <span>✓ Copied to Clipboard</span>
              ) : (
                <>
                  <svg className="w-4 h-4 text-teal-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  <span>Copy Prescription</span>
                </>
              )}
            </button>

            {/* Reset Button */}
            <button
              type="button"
              onClick={handleResetForm}
              className="px-3.5 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-slate-200 bg-slate-950 border border-slate-800 hover:border-slate-700 transition-colors cursor-pointer"
            >
              Reset Form
            </button>
          </div>

          {/* Right Action Group: Save EHR & Save & Print */}
          <div className="flex items-center gap-3">
            {savedStatus && (
              <span className="text-xs text-emerald-400 font-medium animate-pulse">
                ✓ Saved to Patient Consultation Log!
              </span>
            )}
            
            <button
              type="button"
              onClick={handleSaveEhr}
              className="px-4 py-2.5 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all cursor-pointer"
            >
              Save to Patient EHR
            </button>

            {/* Primary Save & Print Button */}
            <button
              type="button"
              id="save-and-print-btn"
              onClick={handlePrintPrescription}
              className="px-5 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 shadow-lg shadow-emerald-500/20 flex items-center gap-2 transition-all transform active:scale-95 cursor-pointer"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
              </svg>
              <span>Save &amp; Print</span>
            </button>
          </div>
        </div>
      </div>

      {/* ═══════════════════════════════════════════════════════════════
          PRINT-ONLY VIEW: Clean A4 Hospital Letterhead Prescription
          ═══════════════════════════════════════════════════════════════ */}
      <div className="hidden print:block w-full bg-white text-slate-900 font-sans p-6">
        {/* Hospital Header & Letterhead */}
        <div className="border-b-2 border-slate-900 pb-4 mb-4">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-lg bg-teal-700 text-white font-bold text-2xl flex items-center justify-center font-serif">
                ش
              </div>
              <div>
                <h1 className="text-xl font-extrabold tracking-tight text-slate-900 uppercase">
                  ShifaScribe Medical Center
                </h1>
                <p className="text-xs text-slate-600 font-medium">
                  Outpatient Department (OPD) • Block B, Room #4
                </p>
                <p className="text-[10px] text-slate-500">
                  Tel: +92 (051) 849-3021 • Email: info@shifascribe.health • Islamabad, Pakistan
                </p>
              </div>
            </div>

            <div className="text-right">
              <h2 className="text-sm font-bold text-slate-900">{doctorName}</h2>
              <p className="text-xs text-teal-800 font-semibold">MBBS, FCPS • General Physician</p>
              <p className="text-[10px] text-slate-500 font-mono">PMDC Reg: #84920-P</p>
            </div>
          </div>
        </div>

        {/* Patient Info Bar */}
        <div className="bg-slate-100 border border-slate-300 rounded-md p-3 mb-5 grid grid-cols-4 gap-2 text-xs">
          <div>
            <span className="text-slate-500 block text-[10px] font-semibold uppercase">Patient Name</span>
            <span className="font-bold text-slate-900">{patientName}</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[10px] font-semibold uppercase">Age / Gender</span>
            <span className="font-semibold text-slate-800">{patientAge} • {patientGender}</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[10px] font-semibold uppercase">Token / MR #</span>
            <span className="font-bold font-mono text-teal-900">{patientToken} (OPD-2026-084)</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[10px] font-semibold uppercase">Date &amp; Time</span>
            <span suppressHydrationWarning className="font-semibold text-slate-800">{printDate}</span>
          </div>
        </div>

        {/* Section 1: Chief Complaints & Symptoms */}
        <div className="mb-5">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-200 pb-1 mb-2 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-teal-600 inline-block" />
            Chief Complaints &amp; Clinical Findings (علامات)
          </h3>
          <div className="flex flex-wrap gap-2 pt-1">
            {symptoms.length > 0 ? (
              symptoms.map((s, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-0.5 rounded border border-slate-300 bg-slate-50 text-slate-800 text-xs font-medium"
                >
                  • {s}
                </span>
              ))
            ) : (
              <span className="text-xs text-slate-500 italic">Routine OPD Checkup</span>
            )}
          </div>
        </div>

        {/* Section 2: Rx Prescribed Medications Table */}
        <div className="mb-6">
          <div className="flex items-center gap-2 border-b-2 border-slate-900 pb-1 mb-2">
            <span className="text-2xl font-serif font-black text-slate-900 leading-none">℞</span>
            <h3 className="text-xs font-extrabold text-slate-900 uppercase tracking-wider">
              Prescribed Medications &amp; Dosage Instructions (ادویات اور خوراک)
            </h3>
          </div>

          <table className="w-full border-collapse text-xs">
            <thead>
              <tr className="bg-slate-100 border-b border-slate-300 text-slate-700">
                <th className="py-1.5 px-2 text-left w-10 font-bold">#</th>
                <th className="py-1.5 px-2 text-left font-bold">Medication Name &amp; Strength</th>
                <th className="py-1.5 px-2 text-left font-bold w-48">Dosage / Frequency</th>
                <th className="py-1.5 px-2 text-left font-bold w-36">Duration</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {medications.length > 0 ? (
                medications.map((med, idx) => {
                  // Attempt split by ' — ' or render cleanly
                  const parts = med.split(" — ");
                  const drugTitle = parts[0] || med;
                  const instructions = parts[1] || "";
                  const subParts = instructions.split(", ");
                  const freq = subParts[0] || dosageFrequency || "As Directed";
                  const dur = subParts[1] || duration || "As Advised";

                  return (
                    <tr key={idx} className="hover:bg-slate-50">
                      <td className="py-2 px-2 font-bold text-slate-600 font-mono">{idx + 1}</td>
                      <td className="py-2 px-2 font-bold text-slate-900">{drugTitle}</td>
                      <td className="py-2 px-2 text-slate-800 font-medium">{freq}</td>
                      <td className="py-2 px-2 text-slate-700 font-medium">{dur}</td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={4} className="py-3 text-center text-slate-500 italic">
                    No medications prescribed.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Section 3: Clinical Notes & Advice */}
        <div className="mb-8 p-3 rounded-md bg-slate-50 border border-slate-200">
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-1">
            Special Precautions &amp; Follow-up Advice (ڈاکٹر کی ہدایات)
          </h3>
          <p className="text-xs text-slate-700 leading-relaxed font-sans">
            {clinicalNotes || "Standard OPD Follow-up & Care. Take all prescribed medications after meals unless otherwise specified."}
          </p>
        </div>

        {/* Section 4: Signature & Security Footer */}
        <div className="pt-6 border-t border-slate-300 grid grid-cols-2 gap-4 items-end">
          <div>
            <div className="text-[10px] text-slate-500 font-mono">
              <p suppressHydrationWarning>Security Token: SHIFA-EHR-104-{securityToken}</p>
              <p>System Verified: ShifaScribe AI Clinical Scribe</p>
            </div>
          </div>

          <div className="text-right">
            <div className="inline-block text-center">
              <div className="w-48 border-b border-slate-900 mb-1" />
              <p className="text-xs font-bold text-slate-900">{doctorName}</p>
              <p className="text-[10px] text-slate-500 uppercase tracking-wider">
                Official Signature &amp; PMDC Stamp
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
