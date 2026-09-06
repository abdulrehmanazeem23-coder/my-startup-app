"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import {
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Cell,
  PieChart,
  Pie,
} from "recharts";

// ─────────────────────────────────────────────────────────────────────────────
// MOCK DATA ARRAYS (Day 23 Administrative Surveillance & Drug Allocation)
// ─────────────────────────────────────────────────────────────────────────────

interface SymptomFrequencyItem {
  symptom: string;
  count: number;
  category: "Vector-Borne" | "Gastrointestinal" | "Respiratory" | "General";
  urgency: "High" | "Medium" | "Low";
  growth: string;
}

const SYMPTOM_DATA: SymptomFrequencyItem[] = [
  { symptom: "High Fever / Pyrexia", count: 480, category: "General", urgency: "Medium", growth: "+8.4%" },
  { symptom: "Severe Headache / Migraine", count: 395, category: "General", urgency: "Low", growth: "+3.1%" },
  { symptom: "Dengue Rash & Thrombocytopenia", count: 342, category: "Vector-Borne", urgency: "High", growth: "+38.5%" },
  { symptom: "Watery Diarrhea / Dehydration", count: 285, category: "Gastrointestinal", urgency: "High", growth: "+21.2%" },
  { symptom: "Chest Congestion / Productive Cough", count: 240, category: "Respiratory", urgency: "Medium", growth: "-4.0%" },
  { symptom: "Body Aches / Severe Myalgia", count: 215, category: "General", urgency: "Low", growth: "+1.8%" },
  { symptom: "Abdominal Cramping & Gastritis", count: 180, category: "Gastrointestinal", urgency: "Medium", growth: "+5.6%" },
  { symptom: "Typhoid Malaise & Rigors", count: 125, category: "Vector-Borne", urgency: "High", growth: "+14.0%" },
  { symptom: "Shortness of Breath / Wheezing", count: 98, category: "Respiratory", urgency: "High", growth: "-1.5%" },
  { symptom: "Sore Throat & Pharyngitis", count: 92, category: "Respiratory", urgency: "Low", growth: "-6.2%" },
];

const DAILY_EPIDEMIC_TRENDS = [
  { day: "Day 17", dengue: 22, diarrhea: 28, respiratory: 36, fever: 54 },
  { day: "Day 18", dengue: 29, diarrhea: 31, respiratory: 34, fever: 58 },
  { day: "Day 19", dengue: 38, diarrhea: 35, respiratory: 32, fever: 64 },
  { day: "Day 20", dengue: 46, diarrhea: 40, respiratory: 35, fever: 69 },
  { day: "Day 21", dengue: 58, diarrhea: 46, respiratory: 31, fever: 76 },
  { day: "Day 22", dengue: 71, diarrhea: 51, respiratory: 37, fever: 84 },
  { day: "Day 23", dengue: 78, diarrhea: 54, respiratory: 35, fever: 89 },
];

interface MedicationAllocationItem {
  name: string;
  generic: string;
  volume: number;
  category: "Analgesic" | "Antibiotic" | "PPI / GI" | "Antihistamine" | "Anti-inflammatory";
  stockLevel: number;
  depletionRate: string;
}

const MEDICATION_ALLOCATION_DATA: MedicationAllocationItem[] = [
  { name: "Tab. Panadol 500mg", generic: "Paracetamol", volume: 1240, category: "Analgesic", stockLevel: 88, depletionRate: "Very High" },
  { name: "Tab. Augmentin 625mg", generic: "Co-Amoxiclav", volume: 890, category: "Antibiotic", stockLevel: 64, depletionRate: "High" },
  { name: "Cap. Risek 40mg", generic: "Omeprazole", volume: 760, category: "PPI / GI", stockLevel: 72, depletionRate: "High" },
  { name: "Tab. Flagyl 400mg", generic: "Metronidazole", volume: 620, category: "Antibiotic", stockLevel: 55, depletionRate: "Medium" },
  { name: "Tab. Brufen 400mg", generic: "Ibuprofen", volume: 510, category: "Anti-inflammatory", stockLevel: 80, depletionRate: "Medium" },
  { name: "Syp. Amoxil 250mg/5ml", generic: "Amoxicillin", volume: 430, category: "Antibiotic", stockLevel: 42, depletionRate: "High" },
  { name: "Tab. Cefspan 400mg", generic: "Cefixime", volume: 380, category: "Antibiotic", stockLevel: 49, depletionRate: "Medium" },
  { name: "Tab. Rigix 10mg", generic: "Cetirizine", volume: 310, category: "Antihistamine", stockLevel: 91, depletionRate: "Low" },
  { name: "Syp. Gaviscon", generic: "Sodium Alginate", volume: 290, category: "PPI / GI", stockLevel: 76, depletionRate: "Medium" },
  { name: "Tab. Ponstan 500mg", generic: "Mefenamic Acid", volume: 250, category: "Analgesic", stockLevel: 83, depletionRate: "Low" },
];

const MED_CATEGORY_SHARE = [
  { name: "Antibiotics", value: 2320, color: "#06b6d4" },
  { name: "Analgesics & Antipyretics", value: 1490, color: "#10b981" },
  { name: "PPI & Gastrointestinal", value: 1050, color: "#8b5cf6" },
  { name: "Anti-inflammatory (NSAID)", value: 510, color: "#f59e0b" },
  { name: "Antihistamines & Allergy", value: 310, color: "#ec4899" },
];

const RECENT_LIVE_SURVEILLANCE_FEED = [
  { token: "#108", region: "Rawalpindi Outpost B", symptoms: "Dengue rash, High fever, Retro-orbital headache", rx: "Tab. Panadol 500mg (TDS), ORS Hydration", flag: "Dengue Positive", time: "3 mins ago" },
  { token: "#107", region: "Islamabad Sector G-9", symptoms: "Watery diarrhea, Abdominal cramps, Vomiting", rx: "Tab. Flagyl 400mg (BID), Cap. Risek 40mg (OD)", flag: "Gastroenteritis", time: "8 mins ago" },
  { token: "#106", region: "Rawalpindi Central OPD", symptoms: "Severe migraine, Neck stiffness, Fever", rx: "Tab. Panadol 500mg (BID), Tab. Brufen 400mg", flag: "Routine Febrile", time: "14 mins ago" },
  { token: "#105", region: "Lahore Model Town OPD", symptoms: "Productive cough, Wheezing, Dyspnea", rx: "Tab. Augmentin 625mg (TDS), Syp. Hydryllin", flag: "Respiratory URI", time: "22 mins ago" },
  { token: "#104", region: "Islamabad OPD Block B", symptoms: "Fever for 2 days, Severe headache", rx: "Tab. Panadol 200mg (BID), Tab. Augmentin 500mg", flag: "Routine Scribe", time: "31 mins ago" },
];

// ─────────────────────────────────────────────────────────────────────────────
// COMPONENT
// ─────────────────────────────────────────────────────────────────────────────

export default function AdminAnalyticsDashboard() {
  const [selectedRegion, setSelectedRegion] = useState<string>("all");
  const [selectedTimeRange, setSelectedTimeRange] = useState<string>("7d");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");

  // Filtered Symptoms
  const filteredSymptoms = useMemo(() => {
    if (selectedCategory === "all") return SYMPTOM_DATA;
    return SYMPTOM_DATA.filter((s) => s.category === selectedCategory);
  }, [selectedCategory]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans flex flex-col">
      {/* Top Administrative Navigation Header */}
      <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-900/90 backdrop-blur-xl px-6 py-4">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* Brand & Admin Badge */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 via-teal-500 to-emerald-400 flex items-center justify-center text-slate-950 font-bold text-xl shadow-lg shadow-cyan-500/20">
              📊
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold tracking-tight text-white">
                  ShifaScribe Surveillance &amp; Analytics
                </h1>
                <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 font-mono font-medium">
                  Admin Dashboard • Sprint 4
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Hospital OPD Disease Surveillance, DRAP Drug Allocation &amp; Epidemic Intelligence
              </p>
            </div>
          </div>

          {/* Header Action Buttons & Navigation */}
          <div className="flex items-center gap-3 self-end md:self-auto">
            <Link
              href="/"
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-teal-300 border border-slate-700 hover:border-teal-500/50 flex items-center gap-2 transition-all cursor-pointer shadow-sm"
            >
              <svg className="w-4 h-4 text-teal-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              <span>🩺 Doctor Consultation Screen</span>
            </Link>

            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-950/60 border border-emerald-800/40 text-xs text-emerald-400 font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>Surveillance Grid Active</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Administrative Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 lg:p-8 flex flex-col gap-6">
        {/* Executive KPI Summary Cards */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* KPI 1 */}
          <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-5 shadow-lg backdrop-blur-sm relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/5 rounded-full blur-2xl pointer-events-none" />
            <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
              <span className="font-semibold uppercase tracking-wider">Total Consultations</span>
              <span className="text-emerald-400 font-bold bg-emerald-950/50 px-2 py-0.5 rounded border border-emerald-800/40">
                +14.2%
              </span>
            </div>
            <div className="text-2xl md:text-3xl font-extrabold text-white font-mono">1,842</div>
            <p className="text-[11px] text-slate-400 mt-1">
              AI Urdu voice scribed across 14 OPD outposts
            </p>
          </div>

          {/* KPI 2: Vector Warning */}
          <div className="bg-slate-900/70 border border-amber-900/40 rounded-2xl p-5 shadow-lg backdrop-blur-sm relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/5 rounded-full blur-2xl pointer-events-none" />
            <div className="flex items-center justify-between text-xs text-amber-400 mb-2">
              <span className="font-semibold uppercase tracking-wider flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
                Dengue Cluster Alert
              </span>
              <span className="text-red-400 font-bold bg-red-950/50 px-2 py-0.5 rounded border border-red-800/40">
                +38.5% Surge
              </span>
            </div>
            <div className="text-2xl md:text-3xl font-extrabold text-amber-300 font-mono">342 Cases</div>
            <p className="text-[11px] text-slate-400 mt-1">
              Concentrated in Rawalpindi &amp; Islamabad Sector G-9
            </p>
          </div>

          {/* KPI 3: Watery Diarrhea */}
          <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-5 shadow-lg backdrop-blur-sm relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-teal-500/5 rounded-full blur-2xl pointer-events-none" />
            <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
              <span className="font-semibold uppercase tracking-wider">Watery Diarrhea / GE</span>
              <span className="text-amber-400 font-bold bg-amber-950/50 px-2 py-0.5 rounded border border-amber-800/40">
                +21.2%
              </span>
            </div>
            <div className="text-2xl md:text-3xl font-extrabold text-teal-300 font-mono">285 Cases</div>
            <p className="text-[11px] text-slate-400 mt-1">
              Monitored for seasonal monsoon gastroenteritis
            </p>
          </div>

          {/* KPI 4: DRAP Drug Units Dispensed */}
          <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-5 shadow-lg backdrop-blur-sm relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/5 rounded-full blur-2xl pointer-events-none" />
            <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
              <span className="font-semibold uppercase tracking-wider">DRAP Meds Allocated</span>
              <span className="text-cyan-400 font-bold bg-cyan-950/50 px-2 py-0.5 rounded border border-cyan-800/40">
                5,680 Units
              </span>
            </div>
            <div className="text-2xl md:text-3xl font-extrabold text-purple-300 font-mono">98.4% Match</div>
            <p className="text-[11px] text-slate-400 mt-1">
              Validated against 200+ DRAP pharmaceutical catalog
            </p>
          </div>
        </section>

        {/* Global Filter Bar */}
        <section className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4 shadow-md">
          <div className="flex flex-wrap items-center gap-3 text-xs">
            {/* Region Filter */}
            <div className="flex items-center gap-2">
              <span className="text-slate-400 font-medium">Outpost Region:</span>
              <select
                value={selectedRegion}
                onChange={(e) => setSelectedRegion(e.target.value)}
                aria-label="Filter Outpost Region"
                className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500/60"
              >
                <option value="all">All Outposts (Islamabad &amp; Rawalpindi)</option>
                <option value="isb">Islamabad Capital Territory (Block B &amp; G-9)</option>
                <option value="rwp">Rawalpindi Division (Central &amp; Outpost B)</option>
                <option value="lhr">Lahore Metropolitan OPD Units</option>
              </select>
            </div>

            {/* Category Filter */}
            <div className="flex items-center gap-2">
              <span className="text-slate-400 font-medium">Condition Category:</span>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                aria-label="Filter Condition Category"
                className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500/60"
              >
                <option value="all">All Syndromes</option>
                <option value="Vector-Borne">Vector-Borne (Dengue &amp; Typhoid)</option>
                <option value="Gastrointestinal">Gastrointestinal &amp; Diarrhea</option>
                <option value="Respiratory">Respiratory &amp; Chest</option>
                <option value="General">General Febrile &amp; Pain</option>
              </select>
            </div>
          </div>

          {/* Time Range Selector */}
          <div className="flex items-center gap-1 bg-slate-950 border border-slate-800 rounded-lg p-1 text-xs">
            {["7d", "14d", "30d", "sprint4"].map((range) => (
              <button
                key={range}
                type="button"
                onClick={() => setSelectedTimeRange(range)}
                className={`px-3 py-1 rounded-md font-medium transition-colors cursor-pointer ${
                  selectedTimeRange === range
                    ? "bg-cyan-600 text-slate-950 font-bold shadow"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {range === "7d"
                  ? "Last 7 Days"
                  : range === "14d"
                  ? "14 Days"
                  : range === "30d"
                  ? "30 Days"
                  : "Sprint 4"}
              </button>
            ))}
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════════
            PRIMARY VISUALIZATION 1: REGIONAL SYMPTOM HEATMAP & FREQUENCY
            ═══════════════════════════════════════════════════════════════ */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Symptom Bar Chart (2 cols) */}
          <div className="lg:col-span-2 bg-slate-900/70 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col justify-between">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-cyan-400" />
                  Regional Symptom Keyword Frequency &amp; Cluster Heatmap
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Extracted in real-time from Whisper AI Urdu transcripts across regional consultations
                </p>
              </div>
              <span className="text-xs font-mono px-2.5 py-1 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                {filteredSymptoms.length} Clusters
              </span>
            </div>

            <div className="mt-4 h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={filteredSymptoms}
                  layout="vertical"
                  margin={{ top: 10, right: 30, left: 40, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                  <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
                  <YAxis
                    dataKey="symptom"
                    type="category"
                    stroke="#94a3b8"
                    width={150}
                    tick={{ fontSize: 11, fill: "#cbd5e1" }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      borderColor: "#334155",
                      borderRadius: "12px",
                      fontSize: "12px",
                      color: "#f8fafc",
                    }}
                    formatter={(value: any, _name: any, item: any) => [
                      `${value} Cases (${item.payload.growth} this week)`,
                      `Cluster: ${item.payload.category}`,
                    ]}
                  />
                  <Bar dataKey="count" radius={[0, 8, 8, 0]}>
                    {filteredSymptoms.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={
                          entry.urgency === "High"
                            ? "#f43f5e"
                            : entry.category === "Vector-Borne"
                            ? "#f59e0b"
                            : entry.category === "Gastrointestinal"
                            ? "#06b6d4"
                            : "#10b981"
                        }
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-2">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500" /> High Urgency / Surge
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> Vector-Borne
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-cyan-500" /> Gastrointestinal
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> General OPD
                </span>
              </div>
              <span className="text-[11px] text-slate-500">Source: NLP Keyword Clustering Engine</span>
            </div>
          </div>

          {/* Daily Epidemic Velocity Area Chart (1 col) */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col justify-between">
            <div className="pb-3 border-b border-slate-800">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-pulse" />
                7-Day Epidemic Outbreak Velocity
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Daily trajectory of Vector vs Gastrointestinal syndromes
              </p>
            </div>

            <div className="mt-4 h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={DAILY_EPIDEMIC_TRENDS} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorDengue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.0} />
                    </linearGradient>
                    <linearGradient id="colorDiarrhea" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="day" stroke="#64748b" tick={{ fontSize: 10 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 10 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      borderColor: "#334155",
                      borderRadius: "8px",
                      fontSize: "11px",
                      color: "#f8fafc",
                    }}
                  />
                  <Area type="monotone" dataKey="dengue" name="Dengue Rash" stroke="#f43f5e" fillOpacity={1} fill="url(#colorDengue)" strokeWidth={2} />
                  <Area type="monotone" dataKey="diarrhea" name="Diarrhea / GE" stroke="#06b6d4" fillOpacity={1} fill="url(#colorDiarrhea)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="p-3 bg-rose-950/30 border border-rose-900/40 rounded-xl text-xs text-rose-300 mt-2">
              <span className="font-bold">⚠️ Epidemiological Notice:</span> Dengue trajectory indicates exponential growth (+38% week-over-week). Larvicidal spraying alert dispatched to Municipal Health authorities.
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════════
            PRIMARY VISUALIZATION 2: MEDICATION ALLOCATION & VOLUME TRACKER
            ═══════════════════════════════════════════════════════════════ */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Medication Volume Allocation Chart (2 cols) */}
          <div className="lg:col-span-2 bg-slate-900/70 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col justify-between">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-teal-400" />
                  Medication Allocation &amp; Prescription Volume Tracker
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Aggregated prescription volumes for top 10 DRAP medications across all OPD dispensaries
                </p>
              </div>
              <span className="text-xs font-mono px-2.5 py-1 rounded bg-teal-950 text-teal-300 border border-teal-800">
                DRAP Validated ✓
              </span>
            </div>

            <div className="mt-4 h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={MEDICATION_ALLOCATION_DATA}
                  margin={{ top: 15, right: 20, left: 0, bottom: 25 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis
                    dataKey="name"
                    stroke="#94a3b8"
                    angle={-25}
                    textAnchor="end"
                    interval={0}
                    height={60}
                    tick={{ fontSize: 10, fill: "#cbd5e1" }}
                  />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      borderColor: "#334155",
                      borderRadius: "12px",
                      fontSize: "12px",
                      color: "#f8fafc",
                    }}
                    formatter={(value: any, _name: any, item: any) => [
                      `${value} Units Prescribed`,
                      `Generic: ${item.payload.generic} • Stock: ${item.payload.stockLevel}% (${item.payload.depletionRate} Depletion)`,
                    ]}
                  />
                  <Bar dataKey="volume" radius={[8, 8, 0, 0]}>
                    {MEDICATION_ALLOCATION_DATA.map((entry, index) => (
                      <Cell
                        key={`med-${index}`}
                        fill={
                          entry.category === "Antibiotic"
                            ? "#06b6d4"
                            : entry.category === "Analgesic"
                            ? "#10b981"
                            : entry.category === "PPI / GI"
                            ? "#8b5cf6"
                            : "#f59e0b"
                        }
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-2">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-cyan-500" /> Antibiotics (Amoxil, Augmentin, Cefspan)
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Analgesics (Panadol, Ponstan)
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-purple-500" /> GI &amp; PPI (Risek, Gaviscon)
                </span>
              </div>
              <span className="text-[11px] text-slate-500">Live DRAP Inventory Aggregator</span>
            </div>
          </div>

          {/* Therapeutic Category Share Pie Chart (1 col) */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col justify-between">
            <div className="pb-3 border-b border-slate-800">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-purple-400" />
                Therapeutic Class Distribution
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Proportion of drug volume prescribed by medical specialty
              </p>
            </div>

            <div className="mt-2 h-56 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={MED_CATEGORY_SHARE}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {MED_CATEGORY_SHARE.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      borderColor: "#334155",
                      borderRadius: "8px",
                      fontSize: "11px",
                      color: "#f8fafc",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Legend list */}
            <div className="space-y-1.5 text-xs">
              {MED_CATEGORY_SHARE.map((cat, idx) => (
                <div key={idx} className="flex items-center justify-between text-slate-300">
                  <span className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: cat.color }} />
                    {cat.name}
                  </span>
                  <span className="font-mono text-slate-400">{cat.value} units</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════════
            SECONDARY SECTION: LIVE ANONYMIZED SURVEILLANCE FEED TABLE
            ═══════════════════════════════════════════════════════════════ */}
        <section className="bg-slate-900/70 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
                Live Anonymized Scribe Surveillance Stream
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Real-time feed of auto-extracted symptoms and DRAP medications from active OPD consult rooms
              </p>
            </div>
            <span className="text-xs px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
              Live Stream Active
            </span>
          </div>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
                  <th className="py-2.5 px-3">Token #</th>
                  <th className="py-2.5 px-3">Clinic Outpost</th>
                  <th className="py-2.5 px-3">Auto-Extracted Symptoms</th>
                  <th className="py-2.5 px-3">Matched DRAP Prescription</th>
                  <th className="py-2.5 px-3">Syndromic Tag</th>
                  <th className="py-2.5 px-3 text-right">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {RECENT_LIVE_SURVEILLANCE_FEED.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-3 font-mono font-bold text-cyan-400">{row.token}</td>
                    <td className="py-3 px-3 text-slate-300 font-medium">{row.region}</td>
                    <td className="py-3 px-3 text-slate-200">{row.symptoms}</td>
                    <td className="py-3 px-3 font-mono text-emerald-300">{row.rx}</td>
                    <td className="py-3 px-3">
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-[11px] font-medium border ${
                          row.flag.includes("Dengue")
                            ? "bg-rose-950/60 text-rose-300 border-rose-800/50"
                            : row.flag.includes("Gastro")
                            ? "bg-cyan-950/60 text-cyan-300 border-cyan-800/50"
                            : "bg-slate-800 text-slate-300 border-slate-700"
                        }`}
                      >
                        {row.flag}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right text-slate-500 font-mono">{row.time}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>

      {/* Admin Dashboard Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-900/40 py-4 px-6 text-center text-xs text-slate-500">
        ShifaScribe Administrative Surveillance Dashboard • Day 23: Regional Symptom Heatmap &amp; Medication Allocation Tracker • Sprint 4
      </footer>
    </div>
  );
}
