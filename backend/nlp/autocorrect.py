"""
ShifaScribe Clinical Text Auto-Corrector Engine
Phonetically auto-corrects noisy Whisper speech transcripts, Urdu script transliterations,
and drug name misspellings into clean English medical terms for downstream NLP extraction.
"""

import re
from typing import List
from thefuzz import process, fuzz
from .drap_validator import DRAP_CATALOG

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 0: Pre-processing rules (run BEFORE main autocorrect)
# Clean up Whisper artifacts like trailing Urdu chars stuck to English words
# ═══════════════════════════════════════════════════════════════════════════
PRE_PROCESS_RULES = [
    # Strip trailing Urdu characters attached to English drug names
    # e.g. "Augmentinڈ" → "Augmentin", "Panadolک" → "Panadol"
    (r"\b(" + "|".join(re.escape(d) for d in DRAP_CATALOG) + r")[^\s\w]*[\u0600-\u06FF]+", r"\1"),
    # Normalize 'mgr' typo from speech-to-text (e.g. '200mgr' -> '200mg', '500mgr' -> '500mg')
    (r"(\d+)\s*mgr\b", r"\1mg"),
    # Separate joined Urdu number-word combos: "چاردنڑ" → "چار دن"
    (r"(چار|تین|دو|پانچ|سات|ایک|دس|پندرہ|بیس|تیس)(دن[ڑ]?)", r"\1 دن"),
    # "دورو ٹائم" → "دو ٹائم" (Whisper adds ر to دو)
    (r"دورو\s*(?=ٹائم|طائم|طایم|طاہم|ٹایم|ٹی\s*ٹام|ٹی\s*تام)", "دو "),
    # Normalize spaced units: 500 mg -> 500mg, 200 mg -> 200mg
    (r"(\d+)\s+(mg|g|ml|mcg|iu)\b", r"\1\2"),
]

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 1: Main Autocorrect Rules
# Each rule is (regex_pattern, replacement). Applied in order via re.sub().
# ═══════════════════════════════════════════════════════════════════════════
CLINICAL_AUTOCORRECT_RULES = [
    # ── 1. Drug Name Phonetics (Urdu Script + English misspellings) ─────

    # Panadol: ALL known Whisper phonetic outputs
    (r"(?:پلڈٹال|پنڈال|پنڈر|پینڈال|پینڈول|پیناڈول|پینا\s*ڈول|پینادول|پینڈڈال|پنادول|پنڈول|پندال|پناڈول|پنڈٹال|پلنڈال|پینڈل|پلڈال|پنادل|پنڈل)", "Panadol"),
    (r"\b(penadol|punadol|panadoll|painadol|panadul|pandol|penodol|panadl|pnadol)\b", "Panadol"),

    # Paracetamol: ALL Whisper variants including پیرسیٹم, پراسیٹم, پیرسیٹامل
    (r"(?:پیراسیٹامول|پراسیٹامول|پراسیٹمول|پیرسیٹامول|پیرسیٹم|پراسیٹم|پیرسیٹامل|پراسیٹامل|پیرسٹامول|پیرسٹامل|پیرسیٹیم)", "Paracetamol"),
    (r"\b(paracetmol|paracetamal|parasitamol|paracetamole|paracetam|parasitam|paracitamol)\b", "Paracetamol"),

    # Calpol
    (r"(?:کالپول|کیلپول)\b", "Calpol"),
    (r"\b(calpole|kalpol|calpal)\b", "Calpol"),

    # Augmentin: ALL known Whisper phonetic outputs including اوپ مینٹل, اوپمینٹل, مائنٹن, اگمانٹن
    (r"(?:اوپ\s*مینٹل|اوپمینٹل|اوپ\s*مائنٹل|اوپمائنٹل|اوپ\s*مینٹن|اوپمینٹن|اوپ\s*منٹن|اوپمنٹن|اوپ\s*منٹل|اوپمنٹل|اوڈ\s*)?(?:مائنٹن|مائنٹین|اگمانٹن|اوگمینٹن|اوگمنٹن|اوگمنٹین|اگمنٹن|اگمنٹین|اگمینٹن|اگمینٹین|آگمنٹن|آگمینٹن|اگمنٹون|اوگمنٹون|اسکا\s*بم|اسکھابم|اسکابم|اوگمانٹن|آگمانٹن|مینٹن|مینٹل|اوگمینٹل|اوگمنٹل)", "Augmentin"),
    (r"\b(augmenten|augmentun|aggmentin|ogmentin|augmantin|agmentin|augmanti|agmantin|ogmantin|opmentin|opmintil|opmentil|augmentil)\b", "Augmentin"),

    # Brufen / Ibuprofen
    (r"(?:بروفن|بروفین|ابروفن|بروفان)", "Brufen"),
    (r"\b(brofen|bruffen|bruphen|broofen|brufin)\b", "Brufen"),

    # Ponstan
    (r"(?:پونسٹان|پونسٹین|پونستان|پانسٹان)", "Ponstan"),
    (r"\b(ponsten|ponstaan|ponston)\b", "Ponstan"),

    # Disprin / Aspirin
    (r"(?:ڈسپرین|ڈیسپرین|دسپرین)", "Disprin"),
    (r"\b(dispren|desprin|dispreen|disprin)\b", "Disprin"),
    (r"(?:ایسپرین|اسپرین)\b", "Aspirin"),

    # Flagyl / Metronidazole
    (r"(?:فلیجل|فلائیجل|فلاجل|فلیجیل)", "Flagyl"),
    (r"\b(flygyl|flgyl|flagil|flajil|flegel)\b", "Flagyl"),
    (r"(?:میٹرونیڈازول|میٹرونیدازول)\b", "Metronidazole"),

    # Entamizole
    (r"(?:انٹامیزول|اینٹامیزول|انٹامزول)\b", "Entamizole"),

    # Cefspan / Cefixime
    (r"(?:سین|سینو|سائن|سیفیکزیم|سیفپین|سیفسیپان|سیفسپان|سیفسپن)", "Cefspan"),
    (r"\b(cefspan|cefixime)\b", "Cefspan"),

    # Risek / Omeprazole / Losec / Nexum / Esomeprazole
    (r"(?:رائزک|رائزیک|ریزک|رسیک)", "Risek"),
    (r"\b(rizek|raizek|raisek|riseck)\b", "Risek"),
    (r"(?:اومیپرازول|امیپرازول)", "Omeprazole"),
    (r"(?:نیکسم|نیکسم|ایسومپرازول|ایزوم)", "Nexum"),
    (r"(?:لوزیک|لوزک)", "Losec"),

    # Arinac / Surbex / Gravinate / Motilium / Buscopan
    (r"(?:آرینیک|ارینیک|آرینک|ارینک)", "Arinac"),
    (r"\b(arinak|arnac)\b", "Arinac"),
    (r"(?:سوربیکس|سربیکس|سوربیکس\s*زیڈ)", "Surbex-Z"),
    (r"(?:گریوینیٹ|گروینیٹ|گریونیٹ)", "Gravinate"),
    (r"(?:موٹیلیم|موٹیلم|ڈومپیریڈون)", "Motilium"),
    (r"(?:بسکوپان|بسکوپین|ہائیوسین)", "Buscopan"),
    (r"(?:کلوفیک|کولو\s*فیک|ڈسپاتالین|ڈسپتالین)", "Colofac"),

    # Rigix / Softin / T-Day / Telfast / Kestine
    (r"(?:رجکس|ریجکس|رگکس|سیٹریزین|سٹریزین)\b", "Rigix"),
    (r"\b(rigx|regix|cetrizine|setrizine)\b", "Rigix"),
    (r"(?:سوفٹن|سافٹن|لوراٹاڈین)\b", "Softin"),
    (r"\b(soften|loratadine)\b", "Softin"),
    (r"(?:ٹیلفاسٹ|ٹیل\s*فاسٹ|فیکسو\s*فیناڈین|ٹی\s*ڈے|ٹیڈے)", "Telfast"),
    (r"(?:کیسٹین|کیسٹن)", "Kestine"),
    (r"(?:ایول|ایویل)\b", "Avil"),

    # Gaviscon / Mucaine / Somogel
    (r"(?:گیوسکان|گیویسکان|گاویسکان)\b", "Gaviscon"),
    (r"\b(gaviscon|gavison)\b", "Gaviscon"),
    (r"(?:میوکین|میوکائن)", "Mucaine"),
    (r"(?:سوموجیل|سوموجل)", "Somogel"),

    # Klaricid / Azomax / Zithromax / Cipro / Leflox / Moxiget / Velosef / Septran
    (r"(?:کلاریسیڈ|کلاریسڈ|کلیریکیڈ)\b", "Klaricid"),
    (r"\b(claricid|klaracid|claracid)\b", "Klaricid"),
    (r"(?:ایزوماکس|ازوماکس|ایزومیکس|زتھروماکس|زتھرومیکس)\b", "Azomax"),
    (r"\b(azomax|azimax|azomx|zithromax)\b", "Azomax"),
    (r"(?:سپرو|سفرو|سپروفلوکساسین|سپروکسن)", "Cipro"),
    (r"\b(cipro|ciproxin)\b", "Cipro"),
    (r"(?:لی\s*فلوکس|لیفلوکس|لیوفلوکساسین)", "Leflox"),
    (r"(?:موکسی\s*گیٹ|موکسیگیٹ|موکسیفلوکساسین)", "Moxiget"),
    (r"(?:ویلوسیف|ویلوسف|سیفراڈین)", "Velosef"),
    (r"(?:سیپٹران|سپٹران)", "Septran"),
    (r"(?:اموکسل|اموکسل|اموکسیسلین)", "Amoxil"),

    # Voltral / Diclofenac / Caflam / Synflex / Nuberol / Muscoril / Celebrex / Tramal
    (r"(?:وولٹرال|ولٹرال|والٹرال|ڈائیکلوفینک|ڈیکلوفینک)", "Voltral"),
    (r"(?:کیفلام|کافلام|کفلام)", "Caflam"),
    (r"(?:سنفلیکس|سنفلکس|نیپروکسن)", "Synflex"),
    (r"(?:نیوبرول|نوبرول)\s*(?:فورٹ)?", "Nuberol Forte"),
    (r"(?:مسکوریل|مسکورل)", "Muscoril"),
    (r"(?:سیلیبریکس|سیلیبرکس)", "Celebrex"),
    (r"(?:ٹرامال|ٹرامادول)", "Tramal"),
    (r"(?:گیبیکا|گابیکا|پریگابالین)", "Gabica"),
    (r"(?:لیریکا|لاریکا)", "Lyrica"),

    # Cardiovascular / Antihypertensive
    (r"(?:کونکور|کانکور|بائسوپرولول)", "Concor"),
    (r"(?:ٹینورمین|ٹینورمن|اٹینولول)", "Tenormin"),
    (r"(?:نورواسک|نورواسک|ایملوڈیپین)", "Norvasc"),
    (r"(?:کیپوٹن|کیپوٹین|کیپٹوپرل)", "Capoten"),
    (r"(?:کوزار|ایزی\s*ڈے|ایزیڈے|لوسارٹن)", "Eziday"),
    (r"(?:گلوکوفیج|گلوکوفاج|میٹفارمین)", "Glucophage"),
    (r"(?:ڈائیمائیکرون|ڈائیمائکرون|گلیکلازائڈ)", "Diamicron"),
    (r"(?:ایماریل|اماریل|گلیمیپرائڈ)", "Amaryl"),
    (r"(?:تھائیروکسین|تھائروکسین)", "Thyroxine"),

    # Vitamins / Supplements / Respiratory / Drops
    (r"(?:سی\s*اے\s*سی|کیک\s*۱۰۰۰|کیک\s*ہزار|کیلسی)", "Cac-1000 Plus"),
    (r"(?:ایویون|سنی\s*ڈی|انڈراپ\s*ڈی|انڈراپ)", "Sunny D"),
    (r"(?:نیوروبین|نیوروبیون|میتھیکوبال|میتھائی\s*کوبال)", "Neurobion"),
    (r"(?:ڈیلٹاکارٹرل|ڈیلٹا\s*کارٹرل|پریڈنیسولون)", "Deltacortril"),
    (r"(?:ڈیکاڈرون|ڈیکاڈران|بیٹنیسول|بیٹنی\s*سول)", "Betnesol"),
    (r"(?:فیوسیڈین|فیوسڈن|پولی\s*فیکس|پولیفیکس)", "Polyfax"),
    (r"(?:ڈرموویٹ|ڈرمویٹ|بیٹنوویٹ|بیٹنویٹ)", "Dermovate"),
    (r"(?:مونٹیگیٹ|مونٹی\s*گیٹ|مائٹیکا|مونٹیلوکاسٹ)", "Montiget"),
    (r"(?:ہائیڈرلین|ہائیڈرالین|پلمونول|پروسپان|سانکوس)", "Hydryllin"),
    (r"(?:وینٹولین|وینٹولن|سالبوٹامول)", "Ventolin"),
    (r"(?:سیریٹائڈ|سمبیکورٹ)", "Seretide"),

    # ── 2. Dosage Units (Urdu Script → English) ─────────────────────────
    (r"(\d+)\s*(?:مج[ی]?|ملج|ملے\s*گرام|ملکران|ملک\s*گرام|ملی\s*گرام|ملگرام|ملیگرام|ملگرامز|ایم\s*جی|ایمجی)\b", r"\1mg"),
    (r"(\d+)\s*(?:گرام|گرامز)\b", r"\1g"),
    (r"(\d+)\s*(?:ملی\s*لیٹر|ایم\s*ایل)\b", r"\1ml"),

    # ── 3. Urdu Script Frequencies & Directives ─────────────────────────
    # Supports تین ٹی ٹام / تین ٹی تام / ٹی ٹام / تین ٹائم / ٹی ڈی ایس
    (r"(?:تین\s*ٹی\s*ٹام|تین\s*ٹی\s*تام|ٹی\s*ٹام|ٹی\s*تام|تین\s*ٹام|تیڈیل|ٹی\s*ڈی\s*ایس|ٹیڈیل|تین\s+دفعہ|تین\s*(?:ٹائم|طائم|طایم|طاہم|ٹائمز|طائمز|ٹایم)|۳\s*(?:ٹائم|طائم|طایم|طاہم|ٹایم)|3\s*(?:طیم|طائم|طایم|طاہم|ٹایم)|تین\s*مرتبہ|تین\s+بار)", "TDS"),
    (r"(?:دو\s*ٹی\s*ٹام|دو\s*ٹی\s*تام|دو\s*ٹام|بی\s*آئی\s*ڈی|بی\s*ڈی|صبح\s+شام|صبح\s*و\s*شام|دو\s*(?:ٹائم|طائم|طایم|طاہم|ٹائمز|طائمز|ٹایم)|۲\s*(?:ٹائم|طائم|طایم|طاہم|ٹایم)|2\s*(?:طیم|طائم|طایم|طاہم|ٹایم)|دو\s*مرتبہ|دو\s+بار(?!ہ|ا))", "BID"),
    (r"(?:ایک\s*ٹی\s*ٹام|ایک\s*ٹام|او\s*ڈی|ایک\s+دفعہ|ایک\s*(?:ٹائم|طائم|طایم|طاہم|ٹائمز|ٹایم)|1\s*(?:طیم|طائم|طایم|طاہم|ٹایم)|ایک\s*مرتبہ|ایک\s+بار|روزانہ)", "OD"),
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
    (r"(?:اردن|ارڈن)\s*کے?\s*لیے", "4 din کے لیے"),

    # ── 5. Recheckup & Clinical Follow-Up ──────────────────────────────
    # ستو بارہ / دو بارہ سی اچھا کب / اچھا کب / چک کب / چیک کپ / دوبارہ چیکپ
    (r"(?:ستو\s*بارہ|ستوبارہ|سو\s*بارہ|دو\s*بارہ\s*سی\s*اچھا\s*کب|اچھا\s*کب|چیک\s*کب|چک\s*کب|اچھا\s*کپ|دوبارہ\s*چیکپ|دوبارہ\s*چکپ|دوبارہ\s*وزٹ|چیک\s*اپ)", "recheckup"),

    # ── 6. Symptoms & Complaints (Urdu Script → English) ────────────────
    # حیڈے / حیڈے کیا / حیرے کیا / حیرے / ہیڈک / ایڈیکور are all Whisper variants of "headache"
    (r"(?:حی[ڈ|ر][ے|ی|ا]?\s*(?:کیا)?|حیرے\s*کیا|حیرے|حیریک|حیریا|سویئر\s*ہیڈک|ہیڈک|ہیڈیک|سر\s*میں\s*درد|سردرد|سر\s+درد|ایڈیکور|ایڈیک|ھیڈیک)", "headache"),
    (r"(?:صورت|صور|شدید|سوئر|سویئر|انکس\s*ور)\b", "severe"),
    # فیبر is a Whisper variant of "fever"
    (r"(?:فیبر|فیور|بخار|تیز\s*بخار)", "fever"),
    (r"(?:فلو|نزلا|نزلہ|زکام|سوئر\s+فلو)", "flu"),
    (r"(?:کھانسی|شدید\s*کھانسی)", "cough"),
    (r"(?:الٹی|ووماٹینگ|وومٹنگ)", "vomiting"),
    (r"(?:دست|پتلے\s*دست)", "diarrhea"),
    (r"(?:چکر|سر\s*چکر|سر\s*چکرانا)", "dizziness"),

    # ── 7. Word-Number Spacing (after7 → after 7, for5 → for 5) ────────
    (r"\b(after|for|in|within|before)(\d+)\b", r"\1 \2"),
]


def expand_multiplier_notation(text: str) -> str:
    """
    Expands physician multiplier dictation like '2x3 din' -> 'BID 3 din' or '3x5 din' -> 'TDS 5 din'.
    """
    def _repl(m):
        freq_num = m.group(1)
        dur_num = m.group(2)
        unit = m.group(3)
        freq_map = {"1": "OD", "2": "BID", "3": "TDS", "4": "QID"}
        freq_str = freq_map.get(freq_num, f"{freq_num} times a day")
        return f"{freq_str} {dur_num} {unit}"
    return re.sub(r"(\d+)\s*[xX*×]\s*(\d+)\s*(din|days?|دن|دین)\b", _repl, text, flags=re.IGNORECASE)


def autocorrect_transcript(text: str) -> str:
    """
    Phonetically auto-corrects a raw transcribed speech string (English, Roman Urdu, or Urdu script).
    Fixes drug misspellings, converts Urdu dosage units, and standardizes clinical dictation.
    """
    if not text or not isinstance(text, str):
        return ""

    corrected = text

    # Phase 0: Pre-processing (clean Whisper artifacts & multiplier notation)
    corrected = expand_multiplier_notation(corrected)
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
        "year", "your", "above", "should", "could", "their", "severe", "whose", "name",
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
