"""
ShifaScribe NLP & RegEx Mapping Module
Parses unstructured Urdu/English clinical transcription strings into structured medical directives,
auto-corrects phonetic speech misspellings, and validates drug names against the DRAP catalog.
"""

from .regex_mapper import parse_clinical_text
from .drap_validator import validate_medication
from .autocorrect import autocorrect_transcript
from .entity_extractor import (
    extract_symptoms,
    extract_medications,
    extract_medications_detailed,
    extract_full_prescription,
)

__all__ = [
    "parse_clinical_text",
    "validate_medication",
    "autocorrect_transcript",
    "extract_symptoms",
    "extract_medications",
    "extract_medications_detailed",
    "extract_full_prescription",
]
