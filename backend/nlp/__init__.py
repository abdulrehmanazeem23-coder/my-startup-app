"""
ShifaScribe NLP & RegEx Mapping Module
Parses unstructured Urdu/English clinical transcription strings into structured medical directives.
"""

from .regex_mapper import parse_clinical_text

__all__ = ["parse_clinical_text"]
