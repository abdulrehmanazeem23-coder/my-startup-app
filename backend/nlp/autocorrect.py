"""
ShifaScribe Clinical Text Auto-Corrector Engine
Phonetically auto-corrects noisy Whisper speech transcripts, Urdu script transliterations,
and drug name misspellings (e.g. "penadol", "punadol", "پینڈال", "پیناڈول" -> "Panadol").
"""

import re
from typing import List
from thefuzz import process, fuzz

# Common Pakistani pharmaceuticals catalog for auto-correction
DRAP_CATALOG = [
    "Panadol", "Paracetamol", "Augmentin", "Brufen", "Ibuprofen", "Flagyl",
    "Metronidazole", "Disprin", "Aspirin", "Rigix", "Softin", "Arinac",
    "Ponstan", "Surbex", "Omeprazole", "Risek", "Gravinate", "Entamizole",
    "Zantac", "Cefspan", "Klaricid", "Azomax", "Basogabin", "Cipro", "Ciprofloxacin",
    "Secnidazole", "Gaviscon", "Calpol", "Arinate", "Famotidine", "Loratadine", "Cetirizine"
]

# Explicit Urdu Script & English Phonetic Misspelling Rules
CLINICAL_AUTOCORRECT_RULES = [
    # ── 1. Urdu Script & English Drug Name Phonetics ───────────────────
    (r"\b(penadol|punadol|panadoll|painadol|panadul|پینڈال|پینڈول|پیناڈول|پینا ڈول|پینادول)\b", "Panadol"),
    (r"\b(paracetmol|paracetamal|parasitamol|پیراسیٹامول|پراسیٹامول)\b", "Paracetamol"),
    (r"\b(brofen|bruffen|bruphen|بروفن|بروفین|ابروفن)\b", "Brufen"),
    (r"\b(ibuprofen|ibrufen)\b", "Ibuprofen"),
    (r"\b(augmenten|aggmentin|ogmentin|اگمنٹن|اگمنٹین)\b", "Augmentin"),
    (r"\b(ponsten|ponstaan|پونسٹان|پونسٹین|پونستان)\b", "Ponstan"),
    (r"\b(dispren|desprin|ڈسپرین)\b", "Disprin"),
    (r"\b(flygyl|flgyl|flagil|فلیجل|فلائیجل)\b", "Flagyl"),
    (r"\b(arinac|آرینیک|ارینیک)\b", "Arinac"),
    (r"\b(surbex|سوربیکس)\b", "Surbex"),
    (r"\b(risek|رائزک)\b", "Risek"),
    (r"\b(gravinate|گریوینیٹ)\b", "Gravinate"),

    # ── 2. Urdu Script Dosage Units & Strength Formats ──────────────────
    (r"(\d+)\s*(?:ملی\s*گرام|ملگرام|ملیگرام|ایم\s*جی)\b", r"\1mg"),
    (r"(\d+)\s*(?:گرام|گرامز)\b", r"\1g"),
    (r"(\d+)\s*(?:ملی\s*لیٹر|ایم\s*ایل)\b", r"\1ml"),

    # ── 3. Urdu Script Frequencies & Directives ──────────────────────────
    (r"\b(تیڈیل|ٹی\s*ڈی\s*ایس|ٹیڈیل|تین\s+دفعہ|تیڈیل\s+کی\s+دوزیج)\b", "TDS"),
    (r"\b(بی\s*آئی\s*ڈی|بی\s*ڈی|صبح\s+شام)\b", "BID"),
    (r"\b(او\s*ڈی|ایک\s+دفعہ|روزانہ)\b", "OD"),
    (r"\b(کیو\s*ایچ\s*ایس|راات\s*کو|رات\s*کو)\b", "QHS"),

    # ── 4. Urdu Script Symptoms & Complaints ────────────────────────────
    (r"\b(سویئر\s*ہیڈک|ہیڈک|ہیڈیک|سر\s*میں\s*درد|سردرد)\b", "headache"),
    (r"\b(فیور|بخار|تیز\s*بخار)\b", "fever"),
    (r"\b(فلو|نزلا|نزلہ|زکام)\b", "flu"),
    (r"\b(کھانسی|شدید\s*کھانسی)\b", "cough"),
    (r"\b(الٹی|ووماٹینگ|وومٹنگ)\b", "vomiting"),
]

def autocorrect_transcript(text: str) -> str:
    """
    Phonetically auto-corrects a raw transcribed speech string (English, Roman Urdu, or Urdu script).
    Fixes drug misspellings (penadol/punadol/پینڈال -> Panadol), converts Urdu dosage units,
    and standardizes clinical dictation for immediate form auto-filling.
    """
    if not text or not isinstance(text, str):
        return ""

    corrected = text

    # Step 1: Apply rule-based phonetic & Urdu script auto-corrections
    for pattern, replacement in CLINICAL_AUTOCORRECT_RULES:
        corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)

    # Step 2: Token-by-token fuzzy auto-correction against DRAP catalog for English typos
    tokens = corrected.split()
    corrected_tokens = []
    
    # Stopwords to exclude from fuzzy drug matching
    stopwords = {
        "with", "from", "that", "this", "have", "take", "give", "days", "weeks", "months",
        "patient", "severe", "headache", "fever", "cough", "pain", "likh", "dene", "karo",
        "din", "hafta", "mahina", "raat", "subah", "shaam", "khaney", "pehle", "baad",
        "کو", "ہے", "اور", "بھی", "اس", "میرے", "کا", "کی", "کے", "بعد", "مجھے", "دوبارہ"
    }

    for token in tokens:
        clean_word = re.sub(r"[^\w]", "", token)
        if len(clean_word) >= 4 and clean_word.lower() not in stopwords:
            match = process.extractOne(clean_word, DRAP_CATALOG, scorer=fuzz.WRatio)
            if match and match[1] >= 75:  # 75%+ Levenshtein similarity
                matched_drug = match[0]
                token = re.sub(re.escape(clean_word), matched_drug, token, flags=re.IGNORECASE)
        corrected_tokens.append(token)

    return " ".join(corrected_tokens)
