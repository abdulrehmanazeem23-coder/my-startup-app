"""
ShifaScribe NLP RegEx Mapping Engine
Parses unstructured code-switched (Urdu/English) speech strings and maps colloquial
time durations and timing idioms to standardized medical directives.
"""

import re
from typing import Dict, Optional


# ---------------------------------------------------------------------------
# Entity Conversion Lookup Tables & Pattern Definitions
# ---------------------------------------------------------------------------

# Dosage Frequency Rules (Pattern -> Clean Medical Standard)
FREQUENCY_PATTERNS = [
    # TDS (Three Times Daily)
    (
        r"\b(din\s+(?:mai|mein|mian)\s+(?:teen|3)\s+(?:dafa|time|times|طیم|مرتبہ|بار)|(?:teen|3)\s+(?:dafa|time|times|طیم|مرتبہ|بار)\s*(?:din\s+(?:mai|mein))?|دن\s*میں\s*(?:تین|3|۳)\s*(?:دفعہ|ٹائم|طائم|طیم|مرتبہ|بار)|تین\s*(?:ٹائم|طائم|طیم|مرتبہ|بار)|[3۳]\s*(?:ٹائم|طائم|طیم|مرتبہ|بار)|tds|t\.d\.s|three\s+times\s+a\s+day)\b",
        "1-1-1 (TDS)",
    ),
    # BID (Twice Daily)
    (
        r"\b(subah\s+o?\s*shaam|subah\s+sham|subah\s+o?\s*shaam|صبح\s*شام|صبح\s*و\s*شام|din\s+(?:mai|mein|mian)\s+(?:do|2)\s+(?:dafa|time|times|طیم|مرتبہ|بار)|(?:do|2)\s+(?:dafa|time|times|طیم|مرتبہ|بار)\s*(?:din\s+(?:mai|mein))?|دن\s*میں\s*(?:دو|2|۲)\s*(?:دفعہ|ٹائم|طائم|طیم|مرتبہ|بار)|دو\s*(?:ٹائم|طائم|طیم|مرتبہ|بار)|[2۲]\s*(?:ٹائم|طائم|طیم|مرتبہ|بار)|bid|b\.i\.d|twice\s+daily)\b",
        "1-0-1 (BID)",
    ),
    # OD (Once Daily)
    (
        r"\b(din\s+(?:mai|mein|mian)\s+(?:ek|1)\s+(?:dafa|time|times|طیم|مرتبہ|بار)|(?:ek|1)\s+(?:dafa|time|times|طیم|مرتبہ|بار)\s*(?:din\s+(?:mai|mein))?|ایک\s*(?:دفعہ|مرتبہ|بار)\s*دن\s*میں|دن\s*میں\s*ایک\s*(?:دفعہ|مرتبہ|بار)|ایک\s*(?:ٹائم|طائم|طیم|مرتبہ|بار)|[1۱]\s*(?:ٹائم|طائم|طیم|مرتبہ|بار)|روزانہ|od|o\.d|once\s+daily)\b",
        "1-0-0 (OD)",
    ),
    # QHS (Nightly)
    (
        r"\b(raat\s+ko(?:\s+ek\s+dafa)?|راات\s*کو|رات\s*کو|qhs|q\.h\.s|nightly)\b",
        "0-0-1 (QHS)",
    ),
    # Q8H (Every 8 hours)
    (
        r"\b(har\s+(?:8|aath)\s+(?:ghante|ghente|hours?)|q8h|q\.8\.h)\b",
        "Every 8 Hours (Q8H)",
    ),
]

# Food / Timing Relation Rules
TIMING_RELATION_PATTERNS = [
    # Khane se pehle / Before food
    (
        r"\b(khan[ea]\s+se\s+pehle|khany\s+sey\s+pehly|khan[ea]\s+sey\s+pehl[ea]|کھانے\s*سے\s*پہلے|before\s+food|before\s+meals?)\b",
        "Before Food",
    ),
    # Khane ke baad / After food
    (
        r"\b(khan[ea]\s+k[eb]\s+baad|khany\s+kay\s+baad|کھانے\s*کے\s*بعد|after\s+food|after\s+meals?)\b",
        "After Food",
    ),
]

# Word to Number Converter for Urdu & English Transliteration
WORD_TO_NUM = {
    "ek": 1, "one": 1, "1": 1, "ایک": 1,
    "do": 2, "two": 2, "2": 2, "دو": 2,
    "teen": 3, "three": 3, "3": 3, "تین": 3,
    "char": 4, "chahr": 4, "four": 4, "4": 4, "چار": 4,
    "paanch": 5, "panch": 5, "five": 5, "5": 5, "پانچ": 5,
    "chhe": 6, "che": 6, "six": 6, "6": 6, "چھ": 6,
    "saat": 7, "seven": 7, "7": 7, "سات": 7,
    "aath": 8, "eight": 8, "8": 8, "آٹھ": 8,
    "nau": 9, "nine": 9, "9": 9, "نو": 9,
    "das": 10, "ten": 10, "10": 10, "دس": 10,
    "pandrah": 15, "fifteen": 15, "15": 15, "پندرہ": 15,
    "bees": 20, "twenty": 20, "20": 20, "بیس": 20,
    "tees": 30, "thirty": 30, "30": 30, "تیس": 30,
}

# Explicit Duration Idioms Mapping
EXPLICIT_DURATION_MAP = [
    (r"\b(ek\s+hafta|1\s+hafta|one\s+week|hafta|ہفتہ|ایک\s*ہفتہ)\b", "7 Days"),
    (r"\b(do\s+hafta|2\s+hafta|do\s+hafte|2\s+hafte|two\s+weeks|دو\s*ہفتے)\b", "14 Days"),
    (r"\b(teen\s+hafta|3\s+hafta|three\s+weeks)\b", "21 Days"),
    (r"\b(ek\s+mahina|1\s+mahina|one\s+month|mahina|مہینہ|ایک\s*مہینہ)\b", "30 Days"),
    (r"\b(do\s+mahina|2\s+mahina|two\s+months|دو\s*مہینے)\b", "60 Days"),
    (r"(?:do\s+din|2\s+din|2\s*دن|دو\s*دن)", "2 Days"),
    (r"(?:teen\s+din|3\s+din|3\s*دن|تین\s*دن)", "3 Days"),
    (r"(?:char\s+din|4\s+din|4\s*دن|چار\s*دن)", "4 Days"),
    (r"(?:paanch\s+din|5\s+din|5\s*دن|پانچ\s*دن)", "5 Days"),
    (r"(?:saat\s+din|7\s+din|7\s*دن|سات\s*دن)", "7 Days"),
]


# ---------------------------------------------------------------------------
# Core Parsing Function
# ---------------------------------------------------------------------------

def parse_clinical_text(raw_text: str) -> Dict[str, Optional[str]]:
    """
    Parses a clinical transcribed text string (Urdu, English, or Code-Switched)
    and extracts structured medical dosage frequency, food timing relations, and duration.

    Args:
        raw_text (str): The raw transcribed string from Whisper AI.

    Returns:
        dict: A dictionary containing:
            - 'dosage_frequency': Formatted directive e.g. "1-0-1 (BID)" or "1-0-1 (BID) - Before Food"
            - 'food_relation': Timing relation e.g. "Before Food" / "After Food" (or None)
            - 'duration': Formatted duration e.g. "7 Days", "2 Days", "30 Days" (or None)
            - 'raw_input': The original raw text string
    """
    if not raw_text or not isinstance(raw_text, str):
        return {
            "dosage_frequency": "Not Specified",
            "food_relation": None,
            "duration": "Not Specified",
            "raw_input": raw_text or "",
        }

    text_lower = raw_text.lower().strip()

    # 1. Match Dosage Frequency
    dosage_freq = None
    for pattern, label in FREQUENCY_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            dosage_freq = label
            break

    # 2. Match Food / Timing Relation
    food_relation = None
    for pattern, label in TIMING_RELATION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            food_relation = label
            break

    # 3. Match Duration
    duration = None

    # Check explicit duration idioms first
    for pattern, label in EXPLICIT_DURATION_MAP:
        if re.search(pattern, text_lower, re.IGNORECASE):
            duration = label
            break

    # If no explicit duration found, try generic RegEx numerical bounds
    if not duration:
        # Pattern: [number/word] [din|days|hafta|hafte|weeks|mahina|mahine|months]
        dur_pattern = r"\b(\d+|ek|one|do|two|teen|three|char|chahr|four|paanch|panch|five|chhe|che|six|saat|seven|aath|eight|nau|nine|das|ten|pandrah|fifteen)\s*(?:sey|se|for|ke\s+liye|kay\s+liye)?\s*(din|days?|hafta|hafte|weeks?|mahina|mahine|months?)\b"
        match = re.search(dur_pattern, text_lower, re.IGNORECASE)
        if match:
            num_str, unit_str = match.group(1), match.group(2)
            num_val = WORD_TO_NUM.get(num_str, int(num_str) if num_str.isdigit() else 1)

            if "hafta" in unit_str or "hafte" in unit_str or "week" in unit_str:
                days_total = num_val * 7
                duration = f"{days_total} Days"
            elif "mahina" in unit_str or "mahine" in unit_str or "month" in unit_str:
                days_total = num_val * 30
                duration = f"{days_total} Days"
            else:
                unit_label = "Day" if num_val == 1 else "Days"
                duration = f"{num_val} {unit_label}"

    # Default fallback if frequency or duration couldn't be extracted
    if not dosage_freq:
        dosage_freq = "As Directed"
    if not duration:
        duration = "Not Specified"

    # Assemble combined dosage frequency including timing relation if present
    full_dosage_frequency = dosage_freq
    if food_relation and food_relation not in dosage_freq:
        full_dosage_frequency = f"{dosage_freq} - {food_relation}"

    return {
        "dosage_frequency": dosage_freq,
        "food_relation": food_relation,
        "full_dosage_frequency": full_dosage_frequency,
        "duration": duration,
        "raw_input": raw_text,
    }
