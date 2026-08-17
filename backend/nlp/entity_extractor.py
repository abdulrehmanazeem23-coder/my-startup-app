"""
ShifaScribe NLP Entity Extractor Module
Extracts localized Symptoms (chief complaints) and Multi-Drug Prescribed Medications
with individual dosage frequencies, strengths, and durations per medication.
Validates all drug names against the official DRAP (Drug Regulatory Authority of Pakistan) catalog.
"""

import re
from typing import List, Dict, Any, Optional, Tuple

from .regex_mapper import parse_clinical_text
from .drap_validator import validate_medication


# ---------------------------------------------------------------------------
# Symptom Keywords & Mappings
# ---------------------------------------------------------------------------

SYMPTOM_LOOKUP = [
    # Headache / Head pain
    (r"\b(headache|sir\s*(?:mai|mein)?\s*dard|head\s+pain|sir\s+dard|سویئر\s*ہیڈک|ہیڈک|ہیڈیک|سر\s*میں\s*درد|سردرد|سر\s+درد)\b", "Headache"),
    # Chest pain
    (r"\b(chest\s+pain|sine\s*(?:mai|mein)?\s*dard|seene\s*(?:mai|mein)?\s*dard|سینے\s*میں\s*درد)\b", "Chest Pain"),
    # Chest tightness
    (r"\b(chest\s+tightness|sine\s*(?:mai|mein)?\s*jakdan|seene\s*(?:mai|mein)?\s*jakdan|سینے\s*میں\s*جکڑن)\b", "Chest Tightness"),
    # Abdominal / Stomach pain
    (r"\b(stomach\s+pain|stomach\s+ache|pait\s*(?:mai|mein)?\s*dard|pait\s+dard|پیٹ\s*میں\s*درد|پیٹ\s+درد)\b", "Abdominal Pain"),
    # General pain / dard
    (r"\b(body\s+ache|jism\s*(?:mai|mein)?\s*dard|jism\s+dard|جسم\s*میں\s*درد|درد)\b", "Body Ache"),
    # Fever / Bukhar
    (r"\b(fever|high\s+fever|bukhar|buhar|تبہ|بخار|تیز\s*بخار|فیور)\b", "Fever"),
    # Cough / Khansi
    (r"\b(cough|persistent\s+cough|khansi|کھانسی|شدید\s*کھانسی)\b", "Cough"),
    # Vomiting / Ulti
    (r"\b(vomiting|vomit|ulti|الٹی|ووماٹینگ|وومٹنگ)\b", "Vomiting"),
    # Nausea / Matli
    (r"\b(nausea|matli|متلی)\b", "Nausea"),
    # Flu / Cold / Zukaam / Nazla
    (r"\b(flu|cold|zukaam|zukam|nazla|نزلہ|زکام|فلو|سوئر\s+فلو|سوئیر\s+فلو)\b", "Flu/Cold"),
    # Dizziness / Chakar
    (r"\b(dizziness|dizzy|chakar|چکر|سر\s*چکرانا)\b", "Dizziness"),
    # Diarrhea / Dast
    (r"\b(diarrhea|loose\s+motions?|dast|دست|پیچش)\b", "Diarrhea"),
    # Sore throat / Gala kharab
    (r"\b(sore\s+throat|gala\s+kharab|gale\s*(?:mai|mein)?\s*dard|گلے\s*میں\s*درد|گلا\s*خراب)\b", "Sore Throat"),
    # Shortness of breath / Saans mai takleef
    (r"\b(shortness\s+of\s+breath|breathlessness|saans\s+(?:mai|mein)?\s*takleef|سانس\s*میں\s*تکلیف)\b", "Shortness of Breath"),
]


# ---------------------------------------------------------------------------
# Common Drug Names & Dosage Form Definitions
# ---------------------------------------------------------------------------

KNOWN_DRUGS = [
    "panadol", "paracetamol", "augmentin", "brufen", "ibuprofen", "flagyl",
    "metronidazole", "disprin", "aspirin", "rigix", "softin", "arinac",
    "ponstan", "surbex", "omeprazole", "risek", "gravinate", "entamizole",
    "zantac", "cefspan", "klaricid", "azomax", "basogabin", "flygyl",
    "amoxicillin", "cipro", "ciprofloxacin", "secnidazole", "gaviscon",
    "calpol", "arinate", "famotidine", "loratadine", "cetirizine", "tramal"
]

FORM_PREFIX_MAP = {
    "tab": "Tab.",
    "tablet": "Tab.",
    "tablets": "Tab.",
    "cap": "Cap.",
    "capsule": "Cap.",
    "capsules": "Cap.",
    "syrup": "Syrup", "syp": "Syrup",
    "inj": "Inj.", "injection": "Inj.",
    "ointment": "Ointment",
    "drops": "Drops",
}

WORD_NUM_MAP = {
    "ek": "1", "one": "1", "do": "2", "two": "2", "teen": "3", "three": "3", "char": "4", "chahr": "4", "four": "4",
    "paanch": "5", "panch": "5", "five": "5", "chhe": "6", "che": "6", "six": "6", "saat": "7", "seven": "7",
    "aath": "8", "eight": "8", "nau": "9", "nine": "9", "das": "10", "ten": "10", "pandrah": "15", "fifteen": "15",
    "ایک": "1", "دو": "2", "تین": "3", "چار": "4", "پانچ": "5", "چھ": "6", "سات": "7", "آٹھ": "8", "نو": "9", "دس": "10"
}


# ---------------------------------------------------------------------------
# Symptom Extraction
# ---------------------------------------------------------------------------

def extract_symptoms(text: str) -> List[str]:
    """
    Extracts clinical symptoms / chief complaints from unstructured text.
    """
    if not text or not isinstance(text, str):
        return []

    text_lower = text.lower()
    extracted_symptoms = []

    for pattern, label in SYMPTOM_LOOKUP:
        if re.search(pattern, text_lower, re.IGNORECASE):
            if label not in extracted_symptoms:
                extracted_symptoms.append(label)

    # Fallback generic pattern: [severe|mild] [symptom_word]
    if not extracted_symptoms:
        generic_pattern = r"\b(severe|mild|acute|chronic)?\s*(headache|fever|cough|pain|bukhar|khansi|vomiting|dard)\b"
        matches = re.findall(generic_pattern, text_lower, re.IGNORECASE)
        for severity, symptom in matches:
            formatted = f"{severity.title()} {symptom.title()}".strip() if severity else symptom.title()
            if formatted not in extracted_symptoms:
                extracted_symptoms.append(formatted)

    return extracted_symptoms


# ---------------------------------------------------------------------------
# Segment-Aware Multi-Drug Extraction Engine
# ---------------------------------------------------------------------------

def extract_medications_detailed(clean_text: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Segment-Aware Multi-Drug Extraction Engine:
    Identifies all prescribed medications and extracts individual dosages,
    frequencies, and durations for each specific drug based on surrounding text proximity.
    
    Returns:
        Tuple of (display_strings_list, detailed_objects_list)
    """
    if not clean_text or not isinstance(clean_text, str):
        return [], []

    drug_spans = []

    # Pattern 1: [Optional Form] + Drug Name + Strength (e.g. "Tab Panadol 500mg" or "Augmentin 500mg")
    p1 = r"\b(?:(tab|tablet|tablets|cap|capsule|capsules|syrup|syp|inj|injection)\.?\s+)?([a-zA-Z]{3,20})\s+(\d+\s*(?:mg|g|ml|mcg))\b"
    for m in re.finditer(p1, clean_text, re.IGNORECASE):
        form, name, strength = m.group(1), m.group(2), m.group(3)
        if name.lower() in KNOWN_DRUGS or len(name) >= 3:
            if name.lower() not in ["days", "din", "hafta", "month", "hours", "ghante", "take", "for", "sey", "mai", "mein"]:
                drug_spans.append({
                    "start": m.start(),
                    "end": m.end(),
                    "form": form,
                    "name": name,
                    "strength": strength,
                    "match": m.group(0),
                })

    # Pattern 2: Known drug name mentioned without explicit adjacent strength
    for drug in KNOWN_DRUGS:
        for m in re.finditer(r"\b" + re.escape(drug) + r"\b", clean_text, re.IGNORECASE):
            if not any(s["start"] <= m.start() <= s["end"] for s in drug_spans):
                nearby = clean_text[m.end():m.end() + 35]
                sm = re.search(r"\b(\d+\s*(?:mg|g|ml))\b", nearby, re.IGNORECASE)
                strength = sm.group(1) if sm else "500mg"
                drug_spans.append({
                    "start": m.start(),
                    "end": m.end(),
                    "form": None,
                    "name": drug,
                    "strength": strength,
                    "match": m.group(0),
                })

    drug_spans.sort(key=lambda x: x["start"])

    # Deduplicate spans by drug name to prevent identical repeats
    unique_spans = []
    seen_drugs = set()
    for d in drug_spans:
        drug_key = d["name"].lower()
        if drug_key not in seen_drugs:
            seen_drugs.add(drug_key)
            unique_spans.append(d)

    # Locate boundary where follow-up advice / recheckup begins
    advice_pattern = r"(?:dobara|recheckup|re-checkup|checkup|visit|چیکپ|وزٹ|چیکٹ|دوارہ|چکپ)"
    advice_match = re.search(advice_pattern, clean_text, re.IGNORECASE)
    advice_start = advice_match.start() if advice_match else len(clean_text)

    medications_detailed = []
    medications_display = []

    for idx, d in enumerate(unique_spans):
        seg_start = d["start"]
        seg_end = unique_spans[idx + 1]["start"] if idx + 1 < len(unique_spans) else advice_start
        seg_text = clean_text[seg_start:seg_end]

        # Parse frequency, duration, food relation within this specific drug segment
        parsed = parse_clinical_text(seg_text)

        form_clean = FORM_PREFIX_MAP.get((d["form"] or "").lower(), "Tab.")
        if "ml" in d["strength"].lower() and not d["form"]:
            form_clean = "Syrup"
        elif "cap" in (d["form"] or "").lower() or d["name"].lower() in ["risek", "omeprazole"]:
            form_clean = "Cap."

        # Pass through DRAP fuzzy validator
        validated_name = validate_medication(f"{form_clean} {d['name'].title()} {d['strength']}")

        freq = parsed.get("full_dosage_frequency") or parsed.get("dosage_frequency") or "As Directed"
        dur = parsed.get("duration") or "Not Specified"

        # Format comprehensive display string
        if dur != "Not Specified" and freq != "As Directed":
            display_item = f"{validated_name} — {freq}, {dur}"
        elif freq != "As Directed":
            display_item = f"{validated_name} — {freq}"
        elif dur != "Not Specified":
            display_item = f"{validated_name} — {dur}"
        else:
            display_item = validated_name

        med_obj = {
            "name": d["name"].title(),
            "strength": d["strength"].lower(),
            "form": form_clean,
            "formatted": validated_name,
            "frequency": freq,
            "duration": dur,
            "instruction": display_item,
        }

        medications_detailed.append(med_obj)
        medications_display.append(display_item)

    return medications_display, medications_detailed


def extract_medications(text: str) -> List[str]:
    """
    Extracts prescribed medications with individual dosage instructions.
    Returns list of formatted medication strings.
    """
    display_list, _ = extract_medications_detailed(text)
    return display_list


# ---------------------------------------------------------------------------
# Clinical Advice & Follow-Up Extraction
# ---------------------------------------------------------------------------

def extract_clinical_notes(text: str) -> str:
    """
    Extracts doctor clinical advice, precautions, and follow-up recheckup instructions
    from clinical audio dictation (e.g. 'Patient should come for a recheckup after 7 days' -> 'Follow-up recheckup advised after 7 days.').
    """
    if not text or not isinstance(text, str):
        return "Standard OPD Follow-up & Care."

    t = text.lower()

    # Pattern 1: [recheckup/dobara/visit/checkup] ... [after/in] [number/word] [days/weeks/din]
    m1 = re.search(
        r"(?:dobara|recheckup|re-checkup|checkup|visit|چیکپ|وزٹ|چیکٹ|دوارہ|چکپ|آنا\s*ہے)\s*(?:[^\w\s]+\s*|\w+\s+){0,6}(?:after|in|baad|کے\s*بعد|ک\s*بعد)?\s*(\d+|ek|one|do|two|teen|three|char|chahr|four|paanch|five|chhe|che|six|saat|seven|aath|eight|nau|nine|das|ten|pandrah|fifteen|ایک|دو|تین|چار|پانچ|سات)\s*(din|days?|hafte|weeks?|mahina|months?|دین|دن)",
        t
    )
    # Pattern 2: [number/word] [days/din] [after / ke baad] ... [recheckup/dobara/visit/checkup]
    m2 = re.search(
        r"(\d+|ek|one|do|two|teen|three|char|chahr|four|paanch|panch|five|chhe|che|six|saat|seven|aath|eight|nau|nine|das|ten|pandrah|fifteen|ایک|دو|تین|چار|پانچ|سات)\s*(din|days?|hafte|weeks?|mahina|months?|دین|دن)\s*(?:ke\s+baad|kay\s+baad|baad|after|کے\s*بعد|ک\s*بعد)?\s*(?:[^\w\s]+\s*|\w+\s+){0,6}(?:dobara|recheckup|re-checkup|checkup|visit|چیکپ|وزٹ|چیکٹ|دوارہ|چکپ|آنا\s*ہے)",
        t
    )

    m = m1 or m2
    if m:
        raw_num, raw_unit = m.group(1), m.group(2)
        num_clean = WORD_NUM_MAP.get(raw_num, raw_num)
        unit_clean = "days" if any(u in raw_unit for u in ["din", "day", "دین", "دن"]) else ("weeks" if any(u in raw_unit for u in ["haft", "week", "ہفت"]) else "months")
        return f"Follow-up recheckup advised after {num_clean} {unit_clean}."

    if any(k in t for k in ["dobara", "recheckup", "re-checkup", "checkup", "visit", "چیکپ", "وزٹ", "چیکٹ", "دوارہ", "چکپ"]):
        return "Follow-up OPD recheckup advised."

    return "Standard OPD Follow-up & Care."


# ---------------------------------------------------------------------------
# Master Prescription Extraction
# ---------------------------------------------------------------------------

def extract_full_prescription(raw_text: str) -> Dict[str, Any]:
    """
    Master NLP Extraction Function:
    Extracts Symptoms, Multi-Drug Prescriptions with individual instructions,
    Dosage Frequencies, Durations, and Clinical Advice Notes.
    """
    symptoms = extract_symptoms(raw_text)
    medications_display, medications_detailed = extract_medications_detailed(raw_text)
    clinical_notes = extract_clinical_notes(raw_text)

    # Primary or summary frequency/duration
    if medications_detailed:
        primary_freq = medications_detailed[0].get("frequency", "As Directed")
        primary_dur = medications_detailed[0].get("duration", "Not Specified")
    else:
        parsed_regex = parse_clinical_text(raw_text)
        primary_freq = parsed_regex.get("dosage_frequency", "As Directed")
        primary_dur = parsed_regex.get("duration", "Not Specified")

    return {
        "symptoms": symptoms,
        "medications": medications_display,
        "medications_detailed": medications_detailed,
        "dosage_frequency": primary_freq,
        "duration": primary_dur,
        "clinical_notes": clinical_notes,
        "raw_input": raw_text or "",
    }
