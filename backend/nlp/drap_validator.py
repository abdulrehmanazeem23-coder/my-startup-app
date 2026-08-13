"""
ShifaScribe DRAP Medicine Catalog Fallback Validator
Uses Levenshtein fuzzy string distance matching (thefuzz) to cross-match predicted
transcribed drug phonetics against the official DRAP (Drug Regulatory Authority of Pakistan) catalog.
"""

import os
import json
import re
from typing import List, Tuple, Optional
from thefuzz import process, fuzz


# ---------------------------------------------------------------------------
# Catalog Loader
# ---------------------------------------------------------------------------

CATALOG_PATH = os.path.join(os.path.dirname(__file__), "drap_catalog.json")

def load_drap_catalog() -> List[str]:
    """Loads official DRAP medicine catalog from JSON file."""
    if os.path.exists(CATALOG_PATH):
        try:
            with open(CATALOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[DRAP Validator Warning] Could not read DRAP catalog JSON: {e}")
    
    # Fallback catalog
    return [
        "Panadol", "Brufen", "Ponstan", "Augmentin", "Disprin", "Arinate",
        "Flagyl", "Paracetamol", "Rigix", "Softin", "Arinac", "Surbex",
        "Omeprazole", "Risek", "Gravinate", "Entamizole", "Zantac",
        "Cefspan", "Klaricid", "Azomax", "Cipro", "Ciprofloxacin", "Amoxicillin"
    ]

# Module-level cached catalog
DRAP_CATALOG = load_drap_catalog()


# ---------------------------------------------------------------------------
# Drug Name & Form Parsing Helper
# ---------------------------------------------------------------------------

FORM_PREFIXES = ["Tab.", "Cap.", "Syrup", "Inj.", "Ointment", "Drops", "Tablet", "Capsule"]

def parse_drug_components(med_str: str) -> Tuple[Optional[str], str, Optional[str]]:
    """
    Parses a medication string like 'Tab. Punudol 500mg' or 'Punudol 500mg'
    into (form_prefix, raw_drug_name, strength_dosage).
    """
    clean_str = med_str.strip()
    
    # Check for leading form prefix
    found_form = None
    for form in FORM_PREFIXES:
        if clean_str.lower().startswith(form.lower()):
            found_form = form
            clean_str = clean_str[len(form):].strip()
            break

    # Extract strength dosage (e.g. 500mg, 250mg, 10ml, 1g)
    strength_match = re.search(r"\b(\d+\s*(?:mg|g|ml|mcg))\b", clean_str, re.IGNORECASE)
    found_strength = None
    if strength_match:
        found_strength = strength_match.group(1)
        # Remove strength from drug name candidate
        drug_name_candidate = re.sub(r"\b\d+\s*(?:mg|g|ml|mcg)\b", "", clean_str, flags=re.IGNORECASE).strip()
    else:
        drug_name_candidate = clean_str

    return found_form, drug_name_candidate, found_strength


# ---------------------------------------------------------------------------
# Primary Validation Function
# ---------------------------------------------------------------------------

def validate_medication(extracted_drug: str, threshold: int = 70) -> str:
    """
    Validates and auto-corrects an extracted drug string against official DRAP catalog
    using fuzzy string distance matching.

    Args:
        extracted_drug (str): Raw extracted drug string e.g. "Punudol 500mg" or "Tab. Punudol 500mg"
        threshold (int): Fuzzy matching similarity threshold (0-100). Default is 70%.

    Returns:
        str: Corrected DRAP medication string e.g. "Tab. Panadol 500mg" (or original if score < threshold).
    """
    if not extracted_drug or not isinstance(extracted_drug, str):
        return extracted_drug or ""

    form_prefix, drug_name, strength = parse_drug_components(extracted_drug)

    if not drug_name:
        return extracted_drug

    # Fuzzy match candidate drug name against official DRAP catalog using WRatio / Levenshtein ratio
    match = process.extractOne(drug_name, DRAP_CATALOG, scorer=fuzz.WRatio)

    if match:
        matched_name, score = match[0], match[1]
        print(f"[DRAP Validator] Match evaluated: '{drug_name}' -> '{matched_name}' (Similarity Score: {score}%)")

        if score >= threshold:
            corrected_drug_name = matched_name
        else:
            corrected_drug_name = drug_name.title()
    else:
        corrected_drug_name = drug_name.title()

    # Re-assemble formatted medication string
    components = []
    if form_prefix:
        components.append(form_prefix)
    elif not form_prefix and "ml" not in (strength or "").lower():
        components.append("Tab.")
    elif not form_prefix and "ml" in (strength or "").lower():
        components.append("Syrup")

    components.append(corrected_drug_name)

    if strength:
        components.append(strength.lower())

    return " ".join(components)
