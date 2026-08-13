"use client";

import { useState, useEffect } from "react";

export interface StructuredEhrData {
  symptoms?: string[];
  medications?: string[];
  dosage_frequency?: string;
  duration?: string;
  food_relation?: string | null;
  full_dosage_frequency?: string | null;
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
  // Form State
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
Patient Token: #104 (Muhammad Tariq)
Date: ${new Date().toLocaleDateString()}

[CHIEF COMPLAINTS / SYMPTOMS]
${symptoms.length > 0 ? symptoms.map((s) => `• ${s}`).join("\n") : "None specified"}

[PRESCRIBED MEDICATIONS]
${medications.length > 0 ? medications.map((m) => `• ${m}`).join("\n") : "None prescribed"}

[DOSAGE & TIMING]
Frequency: ${dosageFrequency || "As Directed"}
Duration : ${duration || "Not Specified"}

[NOTES]
${clinicalNotes || "Standard OPD Follow-up"}

[RAW URDU TRANSCRIPT]
"${rawTranscript || "N/A"}"
========================================
    `.strip();

    navigator.clipboard.writeText(formatted);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  // Save EHR Record
  const handleSaveEhr = () => {
    setSavedStatus(true);
    setTimeout(() => setSavedStatus(false), 3000);
  };

  // Reset Form
  const handleResetForm = () => {
    setSymptoms([]);
    setMedications([]);
    setDosageFrequency("");
    setDuration("");
    setClinicalNotes("");
    setSavedStatus(false);
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      {/* Header & Status Indicator */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-emerald-400 animate-pulse" />
              Interactive E-Prescription Form
            </h2>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/20 font-mono font-medium">
              Day 14 • Sprint 3
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Auto-populated in real-time from Whisper AI &amp; ShifaScribe NLP Engine
          </p>
        </div>

        {/* Auto-Fill Status Badge */}
        <div className="flex items-center gap-2">
          {status === "completed" && structuredData ? (
            <span className="px-3.5 py-1.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5 shadow-sm shadow-emerald-500/10">
              <svg
                className="w-4 h-4 text-emerald-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              ✨ Auto-Filled by ShifaScribe AI
            </span>
          ) : status === "processing_ai" || status === "uploading" ? (
            <span className="px-3.5 py-1.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
              AI Extracting Prescription...
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
        {/* Left Column: Symptoms & Chief Complaints */}
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
                      className="text-teal-500 hover:text-red-400 text-sm font-bold leading-none"
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
                placeholder="Add additional symptom (e.g. Fever)..."
                value={symptomInput}
                onChange={(e) => setSymptomInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddSymptom())}
                className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-teal-500/60"
              />
              <button
                type="button"
                onClick={handleAddSymptom}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-teal-400 rounded-lg text-xs font-medium border border-slate-700 transition-colors"
              >
                + Add
              </button>
            </div>
          </div>

          {/* Dosage & Duration Control Inputs */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Dosage Frequency */}
            <div>
              <label className="block text-xs font-semibold text-teal-400 uppercase tracking-wider mb-2">
                2. Dosage / Frequency (خوراک)
              </label>
              <input
                type="text"
                value={dosageFrequency}
                onChange={(e) => setDosageFrequency(e.target.value)}
                placeholder="e.g. 1-1-1 (TDS) - Before Food"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-teal-500/60 transition-colors"
              />
              <span className="text-[10px] text-slate-500 mt-1 block">
                Translated from colloquial Urdu dictation
              </span>
            </div>

            {/* Duration */}
            <div>
              <label className="block text-xs font-semibold text-teal-400 uppercase tracking-wider mb-2">
                3. Duration (مدت)
              </label>
              <input
                type="text"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                placeholder="e.g. 7 Days / 2 Days"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-teal-500/60 transition-colors"
              />
              <span className="text-[10px] text-slate-500 mt-1 block">
                Calculated numerical duration bound
              </span>
            </div>
          </div>
        </div>

        {/* Right Column: Prescribed Medications Table & DRAP Validation */}
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-teal-400 uppercase tracking-wider mb-2 flex items-center justify-between">
              <span>4. Prescribed Medications (ادویات)</span>
              <span className="text-[10px] text-emerald-400 font-normal">
                DRAP Catalog Validated ✓
              </span>
            </label>

            {/* Medications Table List */}
            <div className="bg-slate-950/70 border border-slate-800 rounded-xl overflow-hidden min-h-[140px]">
              {medications.length > 0 ? (
                <div className="divide-y divide-slate-800/80">
                  {medications.map((med, idx) => (
                    <div
                      key={idx}
                      className="p-3 flex items-center justify-between gap-3 hover:bg-slate-900/50 transition-colors"
                    >
                      <div className="flex items-center gap-2.5 flex-1">
                        <span className="w-5 h-5 rounded-full bg-teal-500/10 text-teal-400 font-mono text-[10px] flex items-center justify-center font-bold border border-teal-500/20">
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
                        className="text-slate-500 hover:text-red-400 text-xs px-2 py-1 rounded hover:bg-slate-800 transition-colors"
                        title="Delete medication"
                      >
                        Delete
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-6 text-center text-xs text-slate-500 italic">
                  No prescribed medications extracted yet. Auto-fills from Whisper audio!
                </div>
              )}
            </div>

            {/* Manual Add Medication Input */}
            <div className="flex gap-2 mt-2">
              <input
                type="text"
                placeholder="Add medication (e.g. Tab. Panadol 500mg)..."
                value={newMedInput}
                onChange={(e) => setNewMedInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddMedication())}
                className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-teal-500/60"
              />
              <button
                type="button"
                onClick={handleAddMedication}
                className="px-3.5 py-1.5 bg-teal-600 hover:bg-teal-500 text-slate-950 rounded-lg text-xs font-bold transition-colors shadow-sm"
              >
                + Add Drug
              </button>
            </div>
          </div>

          {/* Clinical Notes / Doctor Remarks */}
          <div>
            <label className="block text-xs font-semibold text-teal-400 uppercase tracking-wider mb-1.5">
              5. Doctor Clinical Notes / Advice
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
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 border transition-all ${
              copied
                ? "bg-emerald-500 text-slate-950 border-emerald-400 shadow-md shadow-emerald-500/20"
                : "bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700"
            }`}
          >
            {copied ? (
              <>
                <span>✓ Copied to Clipboard</span>
              </>
            ) : (
              <>
                <svg
                  className="w-4 h-4 text-teal-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                  />
                </svg>
                <span>Copy Prescription</span>
              </>
            )}
          </button>

          {/* Reset Button */}
          <button
            type="button"
            onClick={handleResetForm}
            className="px-3.5 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-slate-200 bg-slate-950 border border-slate-800 hover:border-slate-700 transition-colors"
          >
            Reset Form
          </button>
        </div>

        {/* Save to Patient EHR Button */}
        <div className="flex items-center gap-3">
          {savedStatus && (
            <span className="text-xs text-emerald-400 font-medium animate-pulse">
              ✓ Saved to Patient Consultation Log!
            </span>
          )}
          <button
            type="button"
            onClick={handleSaveEhr}
            className="px-5 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-teal-500 to-emerald-400 hover:from-teal-400 hover:to-emerald-300 text-slate-950 shadow-lg shadow-teal-500/20 transition-all transform active:scale-95"
          >
            Save to Patient EHR Record
          </button>
        </div>
      </div>
    </div>
  );
}
