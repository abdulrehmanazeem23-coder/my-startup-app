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
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception as e:
            print(f"[DRAP Validator Warning] Could not read DRAP catalog JSON: {e}")
    
    # Comprehensive fallback catalog
    return [
        "Panadol", "Paracetamol", "Calpol", "Disprin", "Aspirin", "Brufen", "Ibuprofen", "Ponstan",
        "Augmentin", "Amoxicillin", "Amoxil", "Ampicillin", "Cefspan", "Cefixime", "Ceftriaxone", "Rocephin",
        "Klaricid", "Clarithromycin", "Azomax", "Azithromycin", "Zithromax", "Flagyl", "Metronidazole",
        "Entamizole", "Cipro", "Ciprofloxacin", "Ciproxin", "Leflox", "Levofloxacin", "Cravit", "Moxiget",
        "Moxifloxacin", "Velosef", "Cephradine", "Septran", "Vibramycin", "Doxycycline", "Dalacin",
        "Clindamycin", "Linz", "Linezolid", "Meronem", "Meropenem", "Monurol", "Fosfomycin", "Risek",
        "Omeprazole", "Losec", "Nexum", "Esomeprazole", "Ezome", "Gaviscon", "Mucaine", "Simeco",
        "Digas", "Somogel", "Zantac", "Ranitidine", "Famotidine", "Gravinate", "Dimenhydrinate", "Motilium",
        "Domperidone", "Navidoxine", "Maxolon", "Metoclopramide", "Buscopan", "Hyoscine", "Colofac",
        "Mebeverine", "Spasler", "Duspatalin", "Ganaton", "Itopride", "Duphalac", "Lactulose", "Ezilax",
        "Cremaffin", "Rigix", "Cetirizine", "Softin", "Loratadine", "T-Day", "Levocetirizine", "Zyrtec",
        "Telfast", "Fexofenadine", "Xyzal", "Avil", "Pheniramine", "Kestine", "Ebastine", "Arinac",
        "Panadol CF", "Actifed", "Sancos", "Pulmonol", "Ascoril", "Ventolin", "Salbutamol", "Clenil",
        "Beclomethasone", "Seretide", "Flixonase", "Fluticasone", "Symbicort", "Budecort", "Budesonide",
        "Montiget", "Montelukast", "Myteka", "Romilast", "Airfast", "Hydryllin", "Prospan", "Ivy",
        "Ivystar", "Voltral", "Diclofenac", "Caflam", "Dicloran", "Apranax", "Naproxen", "Synflex",
        "Brexin", "Piroxicam", "Toradol", "Ketorolac", "Tramal", "Tramadol", "Nuberol", "Nuberol Forte",
        "Muscoril", "Thiocolchicoside", "Myonal", "Eperisone", "Celebrex", "Celecoxib", "Arcoxia",
        "Etoricoxib", "Gabica", "Pregabalin", "Basogabin", "Lyrica", "Neurobion", "Methycobal",
        "Mecobalamin", "Concor", "Bisoprolol", "Tenormin", "Atenolol", "Lopresor", "Metoprolol",
        "Inderal", "Propranolol", "Norvasc", "Amlodipine", "Softvasc", "Cardizem", "Diltiazem",
        "Capoten", "Captopril", "Zestril", "Lisinopril", "Tanatril", "Cozaar", "Losartan", "Eziday",
        "Angizaar", "Diovan", "Valsartan", "Exforge", "Micardis", "Telmisartan", "Lowplat", "Clopidogrel",
        "Plavix", "Lipiget", "Atorvastatin", "Lipitor", "Rosuvastatin", "Lasix", "Furosemide",
        "Aldactone", "Spironolactone", "Natrilix", "Indapamide", "Glucophage", "Metformin", "Neodipar",
        "Diamicron", "Gliclazide", "Amaryl", "Glimepiride", "Januvia", "Sitagliptin", "Galvus",
        "Vildagliptin", "Jardiance", "Empagliflozin", "Forxiga", "Dapagliflozin", "Trajenta", "Linagliptin",
        "Thyroxine", "Levothyroxine", "Surbex", "Surbex-Z", "Theragran", "Becotin", "Sangobion",
        "Fefol-Vit", "Iberet", "Iberet Folic", "Tri-Hemic", "Vidaylin", "Cac-1000", "Cac-1000 Plus",
        "Calcee", "Osteocare", "Bonex", "Evion", "Sunny D", "Indrop-D", "Max-D", "Deltacortril",
        "Prednisolone", "Decadron", "Dexamethasone", "Solu-Medrol", "Methylprednisolone", "Betnesol",
        "Betamethasone", "Hydrocortisone", "Fucidin", "Fusidic Acid", "Polyfax", "Dermovate", "Clobetasol",
        "Betnovate", "Travocort", "Kenacomb", "Tobradex", "Tobramycin", "Moxidex", "Betnesol-N",
        "Otosporin", "Secnidazole", "Arinate"
    ]

# Module-level cached catalog
DRAP_CATALOG = load_drap_catalog()


# ---------------------------------------------------------------------------
# Drug Name & Form Parsing Helper
# ---------------------------------------------------------------------------

FORM_PREFIXES = ["Tab.", "Cap.", "Syrup", "Syp.", "Inj.", "Ointment", "Drops", "Tablet", "Capsule", "Sachet", "Inhaler"]

def parse_drug_components(med_str: str) -> Tuple[Optional[str], str, Optional[str]]:
    """
    Parses a medication string like 'Tab. Punudol 500mg' or 'Punudol 500mg' or '200mgr'
    into (form_prefix, raw_drug_name, strength_dosage).
    """
    clean_str = med_str.strip()
    
    # Normalize common suffix typos like '200mgr' -> '200mg'
    clean_str = re.sub(r"(\d+)\s*mgr\b", r"\1mg", clean_str, flags=re.IGNORECASE)

    # Check for leading form prefix
    found_form = None
    for form in FORM_PREFIXES:
        if clean_str.lower().startswith(form.lower()):
            found_form = "Tab." if form.lower() in ["tab.", "tablet"] else ("Cap." if form.lower() in ["cap.", "capsule"] else form)
            clean_str = clean_str[len(form):].strip()
            break

    # Extract strength dosage (e.g. 500mg, 250mg, 10ml, 1g, 400mcg, 5000iu, 10drops)
    strength_match = re.search(r"\b(\d+\s*(?:mg|g|ml|mcg|iu|drops?|drop))\b", clean_str, re.IGNORECASE)
    found_strength = None
    if strength_match:
        found_strength = strength_match.group(1).replace(" ", "")
        # Remove strength from drug name candidate
        drug_name_candidate = re.sub(r"\b\d+\s*(?:mg|g|ml|mcg|iu|drops?|drop)\b", "", clean_str, flags=re.IGNORECASE).strip()
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
    elif corrected_drug_name in ["Risek", "Omeprazole", "Losec", "Nexum", "Esomeprazole", "Ezome", "Gabica", "Basogabin", "Lyrica", "Indrop-D"]:
        components.append("Cap.")
    elif "ml" in (strength or "").lower() or corrected_drug_name in ["Hydryllin", "Prospan", "Ventocough", "Ascoril", "Pulmonol", "Sancos", "Actifed", "Duphalac", "Cremaffin"]:
        components.append("Syrup")
    elif "drop" in (strength or "").lower():
        components.append("Drops")
    else:
        components.append("Tab.")

    components.append(corrected_drug_name)

    if strength:
        components.append(strength.lower())

    return " ".join(components)
