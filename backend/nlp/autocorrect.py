"""
ShifaScribe Clinical Text Auto-Corrector Engine
Phonetically auto-corrects noisy Whisper speech transcripts, Urdu transliterations,
and drug name misspellings (e.g. "penadol", "punadol", "پینادول" -> "Panadol").
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

# Explicit phonetic misspelling & Urdu transliteration lookup rules
CLINICAL_AUTOCORRECT_RULES = [
    # Panadol & Paracetamol misspellings & Urdu script
    (r"\b(penadol|punadol|panadoll|painadol|panadul|panadoll?|پینادول|پیناڈول|پینا ڈول)\b", "Panadol"),
    (r"\b(paracetmol|paracetamal|parasitamol|پیراسیٹامول)\b", "Paracetamol"),
    
    # Brufen & Ibuprofen misspellings
    (r"\b(brofen|bruffen|bruphen|بروفن)\b", "Brufen"),
    (r"\b(ibuprofen|ibrufen)\b", "Ibuprofen"),
    
    # Augmentin misspellings
    (r"\b(augmenten|aggmentin|ogmentin|اگمنٹن)\b", "Augmentin"),
    
    # Ponstan & Disprin misspellings
    (r"\b(ponsten|ponstaan|پونسٹان)\b", "Ponstan"),
    (r"\b(dispren|desprin|ڈسپرین)\b", "Disprin"),
    
    # Flagyl & Entamizole misspellings
    (r"\b(flygyl|flgyl|flagil|فلیجل)\b", "Flagyl"),
    
    # Clinical directives & frequency misspellings
    (r"\b(subah\s+sham|suba\s+sham|صبح\s*شام)\b", "subah shaam"),
    (r"\b(din\s+me\s+tin\s+dafa|din\s+mai\s+3\s+dafa)\b", "din mai teen dafa"),
]

def autocorrect_transcript(text: str) -> str:
    """
    Phonetically auto-corrects a raw transcribed speech string.
    Fixes drug misspellings (penadol/punadol -> Panadol) and standardizes clinical dictation.
    """
    if not text or not isinstance(text, str):
        return ""

    corrected = text

    # Step 1: Apply rule-based phonetic & Urdu dictionary auto-corrections
    for pattern, replacement in CLINICAL_AUTOCORRECT_RULES:
        corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)

    # Step 2: Token-by-token fuzzy auto-correction against DRAP catalog
    tokens = corrected.split()
    corrected_tokens = []
    
    # Stopwords to exclude from fuzzy drug matching
    stopwords = {
        "with", "from", "that", "this", "have", "take", "give", "days", "weeks", "months",
        "patient", "severe", "headache", "fever", "cough", "pain", "likh", "dene", "karo",
        "din", "hafta", "mahina", "raat", "subah", "shaam", "khaney", "pehle", "baad"
    }

    for token in tokens:
        # Extract word characters
        clean_word = re.sub(r"[^\w]", "", token)
        if len(clean_word) >= 4 and clean_word.lower() not in stopwords:
            # Check fuzzy match against DRAP catalog
            match = process.extractOne(clean_word, DRAP_CATALOG, scorer=fuzz.WRatio)
            if match and match[1] >= 75:  # 75%+ Levenshtein similarity
                matched_drug = match[0]
                # Replace fuzzy typo with official drug name
                token = re.sub(re.escape(clean_word), matched_drug, token, flags=re.IGNORECASE)
        corrected_tokens.append(token)

    return " ".join(corrected_tokens)
