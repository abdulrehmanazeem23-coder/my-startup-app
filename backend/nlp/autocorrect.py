"""
ShifaScribe Clinical Text Auto-Corrector Engine
Phonetically auto-corrects noisy Whisper speech transcripts, Urdu script transliterations,
and drug name misspellings (e.g. "penadol", "punadol", "پینڈڈال", "پنڈال", "اگمانٹن" -> "Panadol" / "Augmentin").
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

# ═══════════════════════════════════════════════════════════════════════════
# Explicit Urdu Script & English Phonetic Misspelling Rules
# Each rule is (regex_pattern, replacement). Applied in order via re.sub().
# ═══════════════════════════════════════════════════════════════════════════
CLINICAL_AUTOCORRECT_RULES = [
    # ── 1. Drug Name Phonetics (Urdu Script + English misspellings) ─────
    # Panadol: all known Whisper phonetic outputs
    (r"(?:پنڈال|پینڈال|پینڈول|پیناڈول|پینا\s*ڈول|پینادول|پینڈڈال|پنادول|پنڈول|پندال|پناڈول)", "Panadol"),
    (r"\b(penadol|punadol|panadoll|painadol|panadul|pandol|penodol)\b", "Panadol"),

    # Paracetamol
    (r"(?:پیراسیٹامول|پراسیٹامول|پراسیٹمول|پیرسیٹامول)", "Paracetamol"),
    (r"\b(paracetmol|paracetamal|parasitamol|paracetamole)\b", "Paracetamol"),

    # Augmentin: all known Whisper phonetic outputs
    (r"(?:اگمانٹن|اوگمینٹن|اوگمنٹن|اوگمنٹین|اگمنٹن|اگمنٹین|اگمینٹن|اگمینٹین|آگمنٹن|آگمینٹن|اسکا\s*بم|اسکھابم|اسکابم)", "Augmentin"),
    (r"\b(augmenten|augmentun|aggmentin|ogmentin|augmantin|agmentin|augmanti)\b", "Augmentin"),

    # Brufen
    (r"(?:بروفن|بروفین|ابروفن|بروفان)", "Brufen"),
    (r"\b(brofen|bruffen|bruphen|broofen)\b", "Brufen"),

    # Ponstan
    (r"(?:پونسٹان|پونسٹین|پونستان|پانسٹان)", "Ponstan"),
    (r"\b(ponsten|ponstaan|ponsten)\b", "Ponstan"),

    # Disprin
    (r"(?:ڈسپرین|ڈیسپرین|دسپرین)", "Disprin"),
    (r"\b(dispren|desprin|dispreen)\b", "Disprin"),

    # Flagyl
    (r"(?:فلیجل|فلائیجل|فلاجل|فلیجیل)", "Flagyl"),
    (r"\b(flygyl|flgyl|flagil|flajil)\b", "Flagyl"),

    # Cefspan
    (r"(?:سین|سینو|سائن|سیفیکزیم|سیفپین|سیفسیپان|سیفسپان|سیفسپن)", "Cefspan"),

    # Risek
    (r"(?:رائزک|رائزیک|ریزک|رسیک)", "Risek"),

    # Arinac
    (r"(?:آرینیک|ارینیک|آرینک|ارینک)", "Arinac"),

    # Surbex / Gravinate
    (r"(?:سوربیکس|سربیکس)", "Surbex"),
    (r"(?:گریوینیٹ|گروینیٹ)", "Gravinate"),

    # ── 2. Dosage Units (Urdu Script → English) ─────────────────────────
    # CRITICAL: مج / مجی are common Whisper outputs for "mg"
    (r"(\d+)\s*(?:مج|مجی|ملج|ملک\s*گرام|ملی\s*گرام|ملگرام|ملیگرام|ملگرامز|ایم\s*جی|ایمجی)\b", r"\1mg"),
    (r"(\d+)\s*(?:گرام|گرامز)\b", r"\1g"),
    (r"(\d+)\s*(?:ملی\s*لیٹر|ایم\s*ایل)\b", r"\1ml"),

    # ── 3. Urdu Script Frequencies & Directives ─────────────────────────
    # NOTE: دو\s+بار (with required space) to avoid matching inside دوبارہ (dobara/recheckup)
    (r"(?:تیڈیل|ٹی\s*ڈی\s*ایس|ٹیڈیل|تین\s+دفعہ|تین\s*ٹائم|تین\s*ٹائمز|تین\s*طائم|تین\s*طائمز|۳\s*ٹائم|۳\s*طائم|3\s*طیم|۳\s*طیم|تین\s*مرتبہ|تین\s+بار)", "TDS"),
    (r"(?:بی\s*آئی\s*ڈی|بی\s*ڈی|صبح\s+شام|صبح\s*و\s*شام|دو\s*ٹائم|دو\s*ٹائمز|دو\s*طائم|دو\s*طائمز|۲\s*ٹائم|۲\s*طائم|2\s*طیم|۲\s*طیم|دو\s*مرتبہ|دو\s+بار(?!ہ))", "BID"),
    (r"(?:او\s*ڈی|ایک\s+دفعہ|ایک\s*ٹائم|ایک\s*ٹائمز|1\s*طیم|۱\s*طیم|ایک\s*مرتبہ|ایک\s+بار|روزانہ)", "OD"),
    (r"(?:کیو\s*ایچ\s*ایس|راات\s*کو|رات\s*کو)", "QHS"),

    # ── 4. Duration & Phonetics ─────────────────────────────────────────
    (r"(\d+)\s*(?:دین|دنے)\b", r"\1 din"),
    (r"(?:ایک|یک)\s*(?:دین|دنے)\b", "1 din"),
    (r"دو\s*(?:دین|دنے)\b", "2 din"),
    (r"تین\s*(?:دین|دنے)\b", "3 din"),
    (r"چار\s*(?:دین|دنے)\b", "4 din"),
    (r"پانچ\s*(?:دین|دنے)\b", "5 din"),
    (r"سات\s*(?:دین|دنے)\b", "7 din"),

    # ── 5. Symptoms & Complaints (Urdu Script → English) ────────────────
    (r"(?:سویئر\s*ہیڈک|ہیڈک|ہیڈیک|سر\s*میں\s*درد|سردرد|سر\s+درد|ایڈیکور|ایڈیک|ھیڈیک)", "headache"),
    (r"(?:صورت|شدید|سوئر|سویئر)", "severe"),
    (r"(?:فیور|بخار|تیز\s*بخار)", "fever"),
    (r"(?:فلو|نزلا|نزلہ|زکام|سوئر\s+فلو)", "flu"),
    (r"(?:کھانسی|شدید\s*کھانسی)", "cough"),
    (r"(?:الٹی|ووماٹینگ|وومٹنگ)", "vomiting"),
    (r"(?:دست|پتلے\s*دست)", "diarrhea"),
    (r"(?:چکر|سر\s*چکر|سر\s*چکرانا)", "dizziness"),

    # ── 6. Word-Number Spacing (after7 → after 7, for5 → for 5) ────────
    (r"\b(after|for|in|within|before)(\d+)\b", r"\1 \2"),
]


def autocorrect_transcript(text: str) -> str:
    """
    Phonetically auto-corrects a raw transcribed speech string (English, Roman Urdu, or Urdu script).
    Fixes drug misspellings, converts Urdu dosage units, and standardizes clinical dictation.
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
    
    # Broad stoplist: common English words that should NEVER be fuzzy-matched to a drug name
    stopwords = {
        # Common English
        "about", "after", "again", "also", "back", "been", "before", "being", "below",
        "between", "call", "came", "come", "could", "days", "does", "done", "each",
        "even", "every", "first", "five", "from", "given", "give", "goes", "gone",
        "good", "have", "here", "high", "just", "keep", "know", "last", "like",
        "long", "look", "made", "make", "many", "more", "most", "much", "must",
        "need", "next", "once", "only", "other", "over", "part", "past", "same",
        "said", "says", "seem", "show", "side", "since", "some", "still", "such",
        "sure", "take", "tell", "than", "that", "them", "then", "there", "these",
        "they", "this", "those", "through", "time", "times", "told", "took", "turn",
        "under", "until", "upon", "very", "want", "well", "went", "were", "what",
        "when", "where", "which", "while", "whom", "will", "with", "work", "would",
        "year", "your", "above", "should", "could", "their",
        # Medical/clinical context words
        "patient", "severe", "headache", "fever", "cough", "pain", "tablet",
        "capsule", "syrup", "injection", "prescribed", "daily", "weeks", "months",
        "times", "dose", "doses", "doctor", "clinical", "notes", "advice",
        "checkup", "recheckup", "visit", "follow", "which", "given", "taken",
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
