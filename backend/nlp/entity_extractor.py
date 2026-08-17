"""
ShifaScribe NLP Entity Extractor Module
Extracts localized Symptoms (chief complaints) and Prescribed Medications (drugs, forms, strengths)
from unstructured code-switched (Urdu/English) transcription strings and validates them against the DRAP catalog.
"""

import re
from typing import List, Dict, Any, Optional

from .regex_mapper import parse_clinical_text
from .drap_validator import validate_medication


# ---------------------------------------------------------------------------
# Symptom Keywords & Mappings
# ---------------------------------------------------------------------------

SYMPTOM_LOOKUP = [
    # Headache / Head pain
    (r"\b(headache|sir\s*(?:mai|mein)?\s*dard|head\s+pain|sir\s+dard|سویئر\s*ہیڈک|ہیڈک|ہیڈیک|سر\s*میں\s*درد)\b", "Headache"),
    # Chest pain
    (r"\b(chest\s+pain|sine\s*(?:mai|mein)?\s*dard|seene\s*(?:mai|mein)?\s*dard)\b", "Chest Pain"),
    # Chest tightness
    (r"\b(chest\s+tightness|sine\s*(?:mai|mein)?\s*jakdan|seene\s*(?:mai|mein)?\s*jakdan)\b", "Chest Tightness"),
    # Abdominal / Stomach pain
    (r"\b(stomach\s+pain|stomach\s+ache|pait\s*(?:mai|mein)?\s*dard|pait\s+dard)\b", "Abdominal Pain"),
    # General pain / dard
    (r"\b(body\s+ache|jism\s*(?:mai|mein)?\s*dard|jism\s+dard)\b", "Body Ache"),
    # Fever / Bukhar
    (r"\b(fever|high\s+fever|bukhar|buhar|تبہ|بخار|فیور)\b", "Fever"),
    # Cough / Khansi
    (r"\b(cough|persistent\s+cough|khansi|کھانسی)\b", "Cough"),
    # Vomiting / Ulti
    (r"\b(vomiting|vomit|ulti|الٹی|ووماٹینگ|وومٹنگ)\b", "Vomiting"),
    # Nausea / Matli
    (r"\b(nausea|matli)\b", "Nausea"),
    # Flu / Cold / Zukaam / Nazla
    (r"\b(flu|cold|zukaam|zukam|nazla|نزلہ|زکام|فلو)\b", "Flu/Cold"),
    # Dizziness / Chakar
    (r"\b(dizziness|dizzy|chakar|چکر)\b", "Dizziness"),
    # Diarrhea / Dast
    (r"\b(diarrhea|loose\s+motions?|dast|دست)\b", "Diarrhea"),
    # Sore throat / Gala kharab
    (r"\b(sore\s+throat|gala\s+kharab|gale\s*(?:mai|mein)?\s*dard)\b", "Sore Throat"),
    # Shortness of breath / Saans mai takleef
    (r"\b(shortness\s+of\s+breath|breathlessness|saans\s+(?:mai|mein)?\s*takleef)\b", "Shortness of Breath"),
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


# ---------------------------------------------------------------------------
# Extraction Functions
# ---------------------------------------------------------------------------

def extract_symptoms(text: str) -> List[str]:
    """
    Extracts clinical symptoms / chief complaints from unstructured text.

    Args:
        text (str): Input medical transcribed string.

    Returns:
        List[str]: Array of extracted, normalized symptom strings e.g. ["Headache", "Fever"]
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


def extract_medications(text: str) -> List[str]:
    """
    Extracts prescribed medications, strength dosages, and drug forms from text.

    Args:
        text (str): Input medical transcribed string.

    Returns:
        List[str]: Array of formatted medication strings e.g. ["Tab. Panadol 500mg"]
    """
    if not text or not isinstance(text, str):
        return []

    medications = []

    # Pattern 1: Form (Tab/Syrup/Cap) + Drug Name + Strength (e.g., "Tab Panadol 500mg" or "Panadol 500mg")
    # Matches optional form + drug name + dosage strength (e.g. 500mg, 250mg, 10ml, 1g, 40mg)
    drug_regex = r"\b(?:(tab|tablet|tablets|cap|capsule|capsules|syrup|syp|inj|injection)\.?\s+)?([a-zA-Z]{3,20})\s+(\d+\s*(?:mg|g|ml|mcg))\b"
    matches = re.findall(drug_regex, text, re.IGNORECASE)

    for form, drug_name, strength in matches:
        drug_name_clean = drug_name.strip().title()
        strength_clean = strength.strip().lower()

        # Filter out non-drug words matched by regex (e.g. "for 2 days")
        if drug_name_clean.lower() in KNOWN_DRUGS or len(drug_name_clean) >= 3:
            # Skip words that are time/unit words
            if drug_name_clean.lower() in ["days", "din", "hafta", "month", "hours", "ghante", "take", "for", "sey", "mai", "mein"]:
                continue

            form_clean = FORM_PREFIX_MAP.get(form.lower().strip(), "Tab.") if form else "Tab."
            
            # Use Syrup if strength is in ml
            if "ml" in strength_clean and not form:
                form_clean = "Syrup"

            formatted_med = f"{form_clean} {drug_name_clean} {strength_clean}"
            if formatted_med not in medications:
                medications.append(formatted_med)

    # Pattern 2: Also capture known drug names without explicit strength in regex match
    for drug in KNOWN_DRUGS:
        if re.search(r"\b" + re.escape(drug) + r"\b", text, re.IGNORECASE):
            # Check if this drug is already in medications
            if not any(drug.lower() in m.lower() for m in medications):
                strength_match = re.search(r"\b(\d+\s*(?:mg|g|ml))\b", text, re.IGNORECASE)
                strength_str = strength_match.group(1).lower() if strength_match else "500mg"
                formatted_med = f"Tab. {drug.title()} {strength_str}"
                if formatted_med not in medications:
                    medications.append(formatted_med)

    return medications


WORD_NUM_MAP = {
    'ek': '1', 'one': '1', 'do': '2', 'two': '2', 'teen': '3', 'three': '3', 'char': '4', 'chahr': '4', 'four': '4',
    'paanch': '5', 'panch': '5', 'five': '5', 'chhe': '6', 'che': '6', 'six': '6', 'saat': '7', 'seven': '7',
    'aath': '8', 'eight': '8', 'nau': '9', 'nine': '9', 'das': '10', 'ten': '10', 'pandrah': '15', 'fifteen': '15',
    'ایک': '1', 'دو': '2', 'تین': '3', 'چار': '4', 'پانچ': '5', 'چھ': '6', 'سات': '7', 'آٹھ': '8', 'نو': '9', 'دس': '10'
}


def extract_clinical_notes(text: str) -> str:
    """
    Extracts doctor clinical advice, precautions, and follow-up recheckup instructions
    from clinical audio dictation (e.g. 'Patient should come for a recheckup after 7 days' -> 'Follow-up recheckup advised after 7 days.').
    """
    if not text or not isinstance(text, str):
        return "Standard OPD Follow-up & Care."

    t = text.lower()

    # Pattern A: [number/word] [days/din] ... [recheckup/dobara/visit/dawara/checkup]
    mA = re.search(
        r"(\d+|ek|one|do|two|teen|three|char|chahr|four|paanch|panch|five|chhe|che|six|saat|seven|aath|eight|nau|nine|das|ten|pandrah|fifteen|ایک|دو|تین|چار|پانچ|سات)\s*(din|days?|hafte|weeks?|mahina|months?|دین|دن)\s*(?:[^\w\s]+\s*|\w+\s+){0,5}(?:dobara|recheckup|re-checkup|checkup|visit|چیکپ|وزٹ|چیکٹ|دوارہ|چکپ)",
        t
    )
    # Pattern B: [recheckup/dobara/visit/dawara/checkup] ... [number/word] [days/din]
    mB = re.search(
        r"(?:dobara|recheckup|re-checkup|checkup|visit|چیکپ|وزٹ|چیکٹ|دوارہ|چکپ)\s*(?:[^\w\s]+\s*|\w+\s+){0,5}(\d+|ek|one|do|two|teen|three|char|chahr|four|paanch|five|chhe|che|six|saat|seven|aath|eight|nau|nine|das|ten|pandrah|fifteen|ایک|دو|تین|چار|پانچ|سات)\s*(din|days?|hafte|weeks?|mahina|months?|دین|دن)",
        t
    )

    m = mA or mB
    if m:
        raw_num, raw_unit = m.group(1), m.group(2)
        num_clean = WORD_NUM_MAP.get(raw_num, raw_num)
        unit_clean = "days" if any(u in raw_unit for u in ["din", "day", "دین", "دن"]) else ("weeks" if any(u in raw_unit for u in ["haft", "week", "ہفت"]) else "months")
        return f"Follow-up recheckup advised after {num_clean} {unit_clean}."

    if any(k in t for k in ["dobara", "recheckup", "re-checkup", "checkup", "visit", "چیکپ", "وزٹ", "چیکٹ", "دوارہ|چکپ"]):
        return "Follow-up OPD recheckup advised."

    return "Standard OPD Follow-up & Care."


def extract_full_prescription(raw_text: str) -> Dict[str, Any]:
    """
    Master NLP Extraction Function:
    Combines RegEx duration/frequency mapper with Symptom & Medication entity extractors
    and validates all extracted drug names against the official DRAP medicine catalog via fuzzy matching.
    """
    parsed_regex = parse_clinical_text(raw_text)
    symptoms = extract_symptoms(raw_text)
    raw_medications = extract_medications(raw_text)

    # Pass all extracted medications through DRAP fuzzy matching catalog validator
    validated_medications = []
    for med in raw_medications:
        validated = validate_medication(med, threshold=70)
        if validated and validated not in validated_medications:
            validated_medications.append(validated)

    clinical_notes = extract_clinical_notes(raw_text)

    return {
        "symptoms": symptoms,
        "medications": validated_medications,
        "dosage_frequency": parsed_regex.get("dosage_frequency", "As Directed"),
        "duration": parsed_regex.get("duration", "Not Specified"),
        "food_relation": parsed_regex.get("food_relation"),
        "full_dosage_frequency": parsed_regex.get("full_dosage_frequency"),
        "clinical_notes": clinical_notes,
        "raw_input": raw_text or "",
    }
