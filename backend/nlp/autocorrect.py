"""
ShifaScribe Clinical Text Auto-Corrector Engine
Phonetically auto-corrects noisy Whisper speech transcripts, Urdu script transliterations,
and drug name misspellings into clean English medical terms for downstream NLP extraction.
"""

import re
from typing import List
from thefuzz import process, fuzz

# Common Pakistani pharmaceuticals catalog for fuzzy auto-correction
DRAP_CATALOG = [
    "Panadol", "Paracetamol", "Augmentin", "Brufen", "Ibuprofen", "Flagyl",
    "Metronidazole", "Disprin", "Aspirin", "Rigix", "Softin", "Arinac",
    "Ponstan", "Surbex", "Omeprazole", "Risek", "Gravinate", "Entamizole",
    "Zantac", "Cefspan", "Klaricid", "Azomax", "Basogabin", "Cipro", "Ciprofloxacin",
    "Secnidazole", "Gaviscon", "Calpol", "Arinate", "Famotidine", "Loratadine", "Cetirizine",
    "Motilium", "Domperidone", "Buscopan", "Leflox", "Levofloxacin", "Tramal"
]

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 0: Pre-processing rules (run BEFORE main autocorrect)
# Clean up Whisper artifacts like trailing Urdu chars stuck to English words
# ═══════════════════════════════════════════════════════════════════════════
PRE_PROCESS_RULES = [
    # Strip trailing Urdu characters attached to English drug names
    # e.g. "Augmentinڈ" → "Augmentin", "Panadolک" → "Panadol"
    (r"\b(" + "|".join(DRAP_CATALOG) + r")[^\s\w]*[\u0600-\u06FF]+", r"\1"),
    # Separate joined Urdu number-word combos: "چاردنڑ" → "چار دن"
    (r"(چار|تین|دو|پانچ|سات|ایک|دس)(دن[ڑ]?)", r"\1 دن"),
    # "دورو ٹائم" → "دو ٹائم" (Whisper adds ر to دو)
    (r"دورو\s*(?=ٹائم|طائم|طایم|طاہم|ٹایم)", "دو "),
    # Normalize spaced units: 500 mg -> 500mg, 200 mg -> 200mg
    (r"(\d+)\s+(mg|g|ml|mcg)\b", r"\1\2"),
]

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 1: Main Autocorrect Rules
# Each rule is (regex_pattern, replacement). Applied in order via re.sub().
# ═══════════════════════════════════════════════════════════════════════════
CLINICAL_AUTOCORRECT_RULES = [
    # ── 1. Drug Name Phonetics (Urdu Script + English misspellings) ─────

    # Panadol: ALL known Whisper phonetic outputs
    # پلڈٹال, پنڈال, پنڈر, پینڈال, پینڈول, etc.
    (r"(?:پلڈٹال|پنڈال|پنڈر|پینڈال|پینڈول|پیناڈول|پینا\s*ڈول|پینادول|پینڈڈال|پنادول|پنڈول|پندال|پناڈول|پنڈٹال|پلنڈال|پینڈل|پلڈال|پنادل|پنڈل)", "Panadol"),
    (r"\b(penadol|punadol|panadoll|painadol|panadul|pandol|penodol|panadl|pnadol)\b", "Panadol"),

    # Paracetamol
    (r"(?:پیراسیٹامول|پراسیٹامول|پراسیٹمول|پیرسیٹامول)", "Paracetamol"),
    (r"\b(paracetmol|paracetamal|parasitamol|paracetamole)\b", "Paracetamol"),

    # Calpol
    (r"(?:کالپول|کیلپول)\b", "Calpol"),
    (r"\b(calpole|kalpol|calpal)\b", "Calpol"),

    # Augmentin: ALL known Whisper phonetic outputs
    # اگمانٹن, مائنٹن, اوڈ مائنٹن, etc.
    (r"(?:اوڈ\s*)?(?:مائنٹن|مائنٹین|اگمانٹن|اوگمینٹن|اوگمنٹن|اوگمنٹین|اگمنٹن|اگمنٹین|اگمینٹن|اگمینٹین|آگمنٹن|آگمینٹن|اگمنٹون|اوگمنٹون|اسکا\s*بم|اسکھابم|اسکابم|اوگمانٹن|آگمانٹن|مینٹن)", "Augmentin"),
    (r"\b(augmenten|augmentun|aggmentin|ogmentin|augmantin|agmentin|augmanti|agmantin|ogmantin)\b", "Augmentin"),

    # Brufen
    (r"(?:بروفن|بروفین|ابروفن|بروفان)", "Brufen"),
    (r"\b(brofen|bruffen|bruphen|broofen|brufin)\b", "Brufen"),

    # Ponstan
    (r"(?:پونسٹان|پونسٹین|پونستان|پانسٹان)", "Ponstan"),
    (r"\b(ponsten|ponstaan|ponston)\b", "Ponstan"),

    # Disprin
    (r"(?:ڈسپرین|ڈیسپرین|دسپرین)", "Disprin"),
    (r"\b(dispren|desprin|dispreen|disprin)\b", "Disprin"),

    # Flagyl
    (r"(?:فلیجل|فلائیجل|فلاجل|فلیجیل)", "Flagyl"),
    (r"\b(flygyl|flgyl|flagil|flajil|flegel)\b", "Flagyl"),

    # Cefspan / Cefixime
    (r"(?:سین|سینو|سائن|سیفیکزیم|سیفپین|سیفسیپان|سیفسپان|سیفسپن)", "Cefspan"),
    (r"\b(cefspan|cefixime|cefspan)\b", "Cefspan"),

    # Risek / Omeprazole
    (r"(?:رائزک|رائزیک|ریزک|رسیک)", "Risek"),
    (r"\b(rizek|raizek|raisek|riseck)\b", "Risek"),
    (r"(?:اومیپرازول|امیپرازول)", "Omeprazole"),

    # Arinac / Surbex / Gravinate
    (r"(?:آرینیک|ارینیک|آرینک|ارینک)", "Arinac"),
    (r"\b(arinak|arnac)\b", "Arinac"),
    (r"(?:سوربیکس|سربیکس)", "Surbex"),
    (r"(?:گریوینیٹ|گروینیٹ)", "Gravinate"),

    # Rigix / Softin
    (r"(?:رجکس|ریجکس|رگکس|سیٹریزین|سٹریزین)\b", "Rigix"),
    (r"\b(rigx|regix|cetrizine|setrizine)\b", "Rigix"),
    (r"(?:سوفٹن|سافٹن|لوراٹاڈین)\b", "Softin"),
    (r"\b(soften|loratadine)\b", "Softin"),

    # Gaviscon
    (r"(?:گیوسکان|گیویسکان|گاویسکان)\b", "Gaviscon"),
    (r"\b(gaviscon|gavison)\b", "Gaviscon"),

    # Klaricid / Azomax
    (r"(?:کلاریسیڈ|کلاریسڈ|کلیریکیڈ)\b", "Klaricid"),
    (r"\b(claricid|klaracid|claracid)\b", "Klaricid"),
    (r"(?:ایزوماکس|ازوماکس|ایزومیکس)\b", "Azomax"),
    (r"\b(azomax|azimax|azomx)\b", "Azomax"),

    # Entamizole
    (r"(?:انٹامیزول|اینٹامیزول|انٹامزول)\b", "Entamizole"),

    # ── 2. Dosage Units (Urdu Script → English) ─────────────────────────
    # مج / ملے گرام / ملکران / ملگرام are all common Whisper outputs for "mg"
    (r"(\d+)\s*(?:مج[ی]?|ملج|ملے\s*گرام|ملکران|ملک\s*گرام|ملی\s*گرام|ملگرام|ملیگرام|ملگرامز|ایم\s*جی|ایمجی)\b", r"\1mg"),
    (r"(\d+)\s*(?:گرام|گرامز)\b", r"\1g"),
    (r"(\d+)\s*(?:ملی\s*لیٹر|ایم\s*ایل)\b", r"\1ml"),

    # ── 3. Urdu Script Frequencies & Directives ─────────────────────────
    # NOTE: Negative lookahead (?!ہ|ا) prevents matching inside دوبارہ / دوبارا
    # طایم / طاہم / طائم / ٹائم / ٹایم are ALL Whisper variants of "time"
    (r"(?:تیڈیل|ٹی\s*ڈی\s*ایس|ٹیڈیل|تین\s+دفعہ|تین\s*(?:ٹائم|طائم|طایم|طاہم|ٹائمز|طائمز|ٹایم)|۳\s*(?:ٹائم|طائم|طایم|طاہم|ٹایم)|3\s*(?:طیم|طائم|طایم|طاہم|ٹایم)|تین\s*مرتبہ|تین\s+بار)", "TDS"),
    (r"(?:بی\s*آئی\s*ڈی|بی\s*ڈی|صبح\s+شام|صبح\s*و\s*شام|دو\s*(?:ٹائم|طائم|طایم|طاہم|ٹائمز|طائمز|ٹایم)|۲\s*(?:ٹائم|طائم|طایم|طاہم|ٹایم)|2\s*(?:طیم|طائم|طایم|طاہم|ٹایم)|دو\s*مرتبہ|دو\s+بار(?!ہ|ا))", "BID"),
    (r"(?:او\s*ڈی|ایک\s+دفعہ|ایک\s*(?:ٹائم|طائم|طایم|طاہم|ٹائمز|ٹایم)|1\s*(?:طیم|طائم|طایم|طاہم|ٹایم)|ایک\s*مرتبہ|ایک\s+بار|روزانہ)", "OD"),
    (r"(?:کیو\s*ایچ\s*ایس|راات\s*کو|رات\s*کو)", "QHS"),

    # ── 4. Duration & Phonetics ─────────────────────────────────────────
    (r"(\d+)\s*(?:دین|دنے)\b", r"\1 din"),
    (r"(?:ایک|یک)\s*(?:دین|دنے|دن)\b", "1 din"),
    (r"دو\s*(?:دین|دنے|دن)\b", "2 din"),
    (r"تین\s*(?:دین|دنے|دن)\b", "3 din"),
    (r"چار\s*(?:دین|دنے|دن)\b", "4 din"),
    (r"پانچ\s*(?:دین|دنے|دن)\b", "5 din"),
    (r"سات\s*(?:دین|دنے|دن)\b", "7 din"),
    (r"دس\s*(?:دین|دنے|دن)\b", "10 din"),
    # "اردن" / "ارڈن" = garbled "4 din" from Whisper
    (r"(?:اردن|ارڈن)\s*کے?\s*لیے", "4 din کے لیے"),

    # ── 5. Symptoms & Complaints (Urdu Script → English) ────────────────
    # حیڈے / حیڈے کیا / ہیڈک / ایڈیکور are all Whisper variants of "headache"
    (r"(?:حیڈے\s*(?:کیا)?|سویئر\s*ہیڈک|ہیڈک|ہیڈیک|سر\s*میں\s*درد|سردرد|سر\s+درد|ایڈیکور|ایڈیک|ھیڈیک)", "headache"),
    (r"(?:صورت|صور|شدید|سوئر|سویئر|انکس\s*ور)\b", "severe"),
    # فیبر is a Whisper variant of "fever"
    (r"(?:فیبر|فیور|بخار|تیز\s*بخار)", "fever"),
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

    # Phase 0: Pre-processing (clean Whisper artifacts)
    for pattern, replacement in PRE_PROCESS_RULES:
        corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)

    # Phase 1: Apply rule-based phonetic & Urdu script auto-corrections
    for pattern, replacement in CLINICAL_AUTOCORRECT_RULES:
        corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)

    # Phase 2: Token-by-token fuzzy auto-correction against DRAP catalog for English typos
    tokens = corrected.split()
    corrected_tokens = []
    
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
        "year", "your", "above", "should", "could", "their", "severe", "whose",
        # Medical/clinical context words
        "patient", "headache", "fever", "cough", "pain", "tablet",
        "capsule", "syrup", "injection", "prescribed", "daily", "weeks", "months",
        "times", "dose", "doses", "doctor", "clinical", "notes", "advice",
        "checkup", "recheckup", "visit", "follow", "given", "taken",
        # Roman Urdu
        "likh", "dene", "karo", "diya", "liye", "wala", "baad", "khane", "khana",
        "pehle", "subah", "shaam", "raat", "safed", "kali", "pani", "khoon",
        "pasina", "kamzori", "theek", "bura", "acha", "zyada", "thoda",
        "hafta", "hafte", "mahina", "mahine", "dafa", "baar", "ghante",
        "din", "dinon",
    }

    for token in tokens:
        clean_word = re.sub(r"[^\w]", "", token)
        if (len(clean_word) >= 5
                and clean_word.isascii()
                and clean_word.isalpha()
                and clean_word.lower() not in stopwords
                and clean_word not in DRAP_CATALOG):
            match = process.extractOne(clean_word, DRAP_CATALOG, scorer=fuzz.ratio)
            if match and match[1] >= 82:
                matched_drug = match[0]
                token = re.sub(re.escape(clean_word), matched_drug, token, flags=re.IGNORECASE)
        corrected_tokens.append(token)

    return " ".join(corrected_tokens)
