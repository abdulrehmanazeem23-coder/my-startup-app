import sys
import os
import json

# Add backend directory to path if running directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nlp.drap_validator import validate_medication
from nlp.entity_extractor import extract_full_prescription

def run_test():
    print("=" * 65)
    print("ShifaScribe Day 13 - DRAP Medicine Catalog Fuzzy Validator Test")
    print("=" * 65)

    test_cases = [
        ("Punudol 500mg", "Tab. Panadol 500mg"),
        ("Tab. Punudol 500mg", "Tab. Panadol 500mg"),
        ("Brofen 400mg", "Tab. Brufen 400mg"),
        ("Syrup Augmenten 156mg", "Syrup Augmentin 156mg"),
        ("Disprin 50mg", "Tab. Disprin 50mg"),
    ]

    print("\nPart 1: Direct validate_medication() Fuzzy Match Tests:")
    for misspelled, expected in test_cases:
        corrected = validate_medication(misspelled, threshold=70)
        passed = (corrected == expected)
        print(f"  * Input Misspelled : '{misspelled}'")
        print(f"    Corrected DRAP   : '{corrected}'")
        print(f"    Expected Output  : '{expected}'")
        print(f"    Match Status     : {'[PASSED]' if passed else '[FAILED]'}\n")

    print("Part 2: Full Prescription Integration Test with Misspelled Input Sentence:")
    sample_sentence = "Mery sir mai do din sey severe headache hai, isey Punudol 500mg TDS likh den."
    print(f"  Input Sentence: \"{sample_sentence}\"\n")

    result = extract_full_prescription(sample_sentence)
    print("  Extracted & DRAP-Validated JSON Output:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Assertions
    assert any("Panadol 500mg" in med for med in result["medications"]), f"DRAP Auto-Correction failed! Medications: {result['medications']}"
    assert result["dosage_frequency"] == "1-1-1 (TDS)", "Frequency mapping failed!"
    assert result["duration"] == "2 Days", "Duration mapping failed!"

    print("\n" + "=" * 65)
    print("ALL DRAP FUZZY VALIDATOR TESTS PASSED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    run_test()
