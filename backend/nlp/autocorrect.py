"""
ShifaScribe Clinical Text Auto-Corrector Engine
Phonetically auto-corrects noisy Whisper speech transcripts, Urdu script transliterations,
and drug name misspellings (e.g. "penadol", "punadol", "پینڈڈال", "اگمینٹن", "سین" -> "Panadol" / "Cefspan").
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
    (r"\b(penadol|punadol|panadoll|painadol|panadul|پینڈال|پینڈول|پیناڈول|پینا ڈول|پینادول|پینڈڈال)\b", "Panadol"),
    (r"\b(paracetmol|paracetamal|parasitamol|پیراسیٹامول|پراسیٹامول)\b", "Paracetamol"),
    (r"\b(brofen|bruffen|bruphen|بروفن|بروفین|ابروفن)\b", "Brufen"),
    (r"\b(ibuprofen|ibrufen)\b", "Ibuprofen"),
    (r"\b(augmenten|augmentun|aggmentin|ogmentin|اوگمینٹن|اوگمنٹن|اوگمنٹین|اگمنٹن|اگمنٹین|اگمینٹن|اگمینٹین|اسکا\s*بم|اسکھابم|اسکابم)\b", "Augmentin"),
    (r"\b(after|for|in|within|before)(\d+)\b", r"\1 \2"),
    (r"\b(ponsten|ponstaan|پونسٹان|پونسٹین|پونستان)\b", "Ponstan"),
    (r"\b(dispren|desprin|ڈسپرین)\b", "Disprin"),
    (r"\b(flygyl|flgyl|flagil|فلیجل|فلائیجل)\b", "Flagyl"),
    (r"\b(arinac|آرینیک|ارینیک)\b", "Arinac"),
    (r"\b(surbex|سوربیکس)\b", "Surbex"),
    (r"\b(risek|رائزک)\b", "Risek"),
    (r"\b(gravinate|گریوینیٹ)\b", "Gravinate"),
    (r"\b(سین|سینو|سائن|سیفیکزیم|سیفپین|سیفسیپان|سیفسپان)\b", "Cefspan"),

    # ── 2. Urdu Script Dosage Units & Strength Formats ──────────────────
    (r"(\d+)\s*(?:ملک\s*گرام|ملی\s*گرام|ملگرام|ملیگرام|ملگرامز|ایم\s*جی|ایمجی)\b", r"\1mg"),
    (r"(\d+)\s*(?:گرام|گرامز)\b", r"\1g"),
    (r"(\d+)\s*(?:ملی\s*لیٹر|ایم\s*ایل)\b", r"\1ml"),

    # ── 3. Urdu Script Frequencies & Directives ──────────────────────────
    (r"\b(تیڈیل|ٹی\s*ڈی\s*ایس|ٹیڈیل|تین\s+دفعہ|تین\s*ٹائم|تین\s*ٹائمز|تین\s*طائم|تین\s*طائمز|۳\s*ٹائم|۳\s*طائم|3\s*طیم|۳\s*طیم|تیڈیل\s+کی\s+دوزیج|ڈیل|ڈیڈیل)\b", "TDS"),
    (r"\b(بی\s*آئی\s*ڈی|بی\s*ڈی|صبح\s+شام|دو\s*ٹائم|دو\s*ٹائمز|دو\s*طائم|دو\s*طائمز|۲\s*ٹائم|۲\s*طائم|2\s*طیم|۲\s*طیم)\b", "BID"),
    (r"\b(او\s*ڈی|ایک\s+دفعہ|ایک\s*ٹائم|ایک\s*ٹائمز|1\s*طیم|۱\s*طیم|روزانہ)\b", "OD"),
    (r"\b(کیو\s*ایچ\s*ایس|راات\s*کو|رات\s*کو)\b", "QHS"),

    # ── 4. Urdu Script Duration & Phonetics ──────────────────────────────
    (r"(\d+)\s*دین\b", r"\1 din"),
    (r"(ایک|یک)\s*دین\b", "1 din"),
    (r"دو\s*دین\b", "2 din"),
    (r"تین\s*دین\b", "3 din"),
    (r"چار\s*دین\b", "4 din"),
    (r"پانچ\s*دین\b", "5 din"),
    (r"سات\s*دین\b", "7 din"),

    # ── 5. Urdu Script Symptoms & Complaints ────────────────────────────
    (r"\b(سویئر\s*ہیڈک|ہیڈک|ہیڈیک|سر\s*میں\s*درد|سردرد|سر\s+درد)\b", "headache"),
    (r"\b(فیور|بخار|تیز\s*بخار)\b", "fever"),
    (r"\b(فلو|نزلا|نزلہ|زکام|سوئر\s+فلو)\b", "flu"),
    (r"\b(کھانسی|شدید\s*کھانسی)\b", "cough"),
    (r"\b(الٹی|ووماٹینگ|وومٹنگ)\b", "vomiting"),
    (r"\b(دست|پتلے\s*دست)\b", "diarrhea"),
    (r"\b(چکر|سر\s*چکر)\b", "dizziness"),
]

def autocorrect_transcript(text: str) -> str:
    """
    Phonetically auto-corrects a raw transcribed speech string (English, Roman Urdu, or Urdu script).
    Fixes drug misspellings (penadol/punadol/پینڈڈال/اگمینٹن -> Panadol/Augmentin), converts Urdu dosage units (200 ملگرام -> 200mg),
    and standardizes clinical dictation for immediate form auto-filling.
    """
    if not text or not isinstance(text, str):
        return ""

    corrected = text

    # Step 1: Apply rule-based phonetic & Urdu script auto-corrections
    for pattern, replacement in CLINICAL_AUTOCORRECT_RULES:
        corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)

    # Step 2: Token-by-token fuzzy auto-correction against DRAP catalog for English typos
    # ONLY for words that look like they could be drug names (5+ chars, Latin-only, not common English)
    tokens = corrected.split()
    corrected_tokens = []
    
    # Broad stoplist: common English words, Urdu/Roman-Urdu words that should NEVER be fuzzy-matched to a drug name
    stopwords = {
        # Common English
        "about", "after", "also", "back", "been", "before", "being", "call", "came",
        "come", "could", "days", "does", "done", "each", "even", "every", "five",
        "from", "give", "goes", "gone", "good", "have", "here", "high", "just",
        "keep", "know", "last", "like", "long", "look", "made", "make", "many",
        "more", "most", "much", "must", "need", "next", "once", "only", "over",
        "part", "past", "same", "said", "says", "seem", "show", "side", "some",
        "such", "sure", "take", "tell", "than", "that", "them", "then", "they",
        "this", "time", "told", "took", "turn", "upon", "very", "want", "well",
        "went", "were", "what", "when", "whom", "will", "with", "work", "year",
        "your", "should", "would", "could", "their", "there", "these", "those",
        "which", "while", "where", "other", "after", "again", "still", "first",
        "since", "under", "until", "about", "above", "below", "between", "through",
        # Medical/clinical context words
        "patient", "severe", "headache", "fever", "cough", "pain", "tablet",
        "capsule", "syrup", "injection", "prescribed", "daily", "weeks", "months",
        "times", "dose", "doses", "doctor", "clinical", "notes", "advice",
        "checkup", "recheckup", "visit", "follow",
        # Roman Urdu
        "likh", "dene", "karo", "diya", "liye", "wala", "baad", "khane", "khana",
        "pehle", "subah", "shaam", "raat", "safed", "kali", "pani", "khoon",
        "pasina", "kamzori", "theek", "bura", "acha", "zyada", "thoda",
        "hafta", "hafte", "mahina", "mahine", "dafa", "baar", "ghante",
        "din", "dinon",
        # Urdu script words that might get garbled by split()
        "کو", "ہے", "اور", "بھی", "اس", "میرے", "کا", "کی", "کے", "بعد",
        "مجھے", "دوبارہ", "ایک", "دوز", "لکھ", "دیئے", "انہوں", "نے",
        "میں", "کھانی", "لیے", "ساتھ", "پھر", "پاس", "آنا", "جس", "وجہ",
        "علیکم", "پیشنٹ", "آئے", "ہیں", "محمد", "تارک", "دنوں", "سوئر",
        "سے", "کافی",
    }

    for token in tokens:
        clean_word = re.sub(r"[^\w]", "", token)
        # Only attempt fuzzy match if:
        # 1. Word is 5+ characters (drug names are typically 5+ chars)
        # 2. Word is purely Latin alphabet (not Urdu script, not numbers)
        # 3. Word is not in the stopword list
        # 4. Word is not already a known correct drug name
        if (len(clean_word) >= 5
                and clean_word.isascii()
                and clean_word.isalpha()
                and clean_word.lower() not in stopwords
                and clean_word not in DRAP_CATALOG):
            match = process.extractOne(clean_word, DRAP_CATALOG, scorer=fuzz.ratio)
            if match and match[1] >= 82:  # Stricter threshold + stricter scorer
                matched_drug = match[0]
                token = re.sub(re.escape(clean_word), matched_drug, token, flags=re.IGNORECASE)
        corrected_tokens.append(token)

    return " ".join(corrected_tokens)
