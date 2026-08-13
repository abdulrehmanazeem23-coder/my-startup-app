import sys
import os
import json

# Add backend directory to path if running directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nlp.entity_extractor import extract_full_prescription

def run_test():
    print("=" * 65)
    print("ShifaScribe Day 12 — Symptom & Medication Entity Extractor Test")
    print("=" * 65)

    test_sentence = "Mery sir mai do din sey severe headache hai, isey Panadol 500mg TDS likh den."

    print("\nInput Test Sentence:")
    print(f"  \"{test_sentence}\"")
    print("\nExecuting extract_full_prescription()...\n")

    result = extract_full_prescription(test_sentence)

    print("Extracted Prescription JSON Object:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\nKey Assertions & Verification:")
    print(f"  • Symptoms         : {result.get('symptoms')}  (Expected: ['Headache'])")
    print(f"  • Medications      : {result.get('medications')}  (Expected: ['Tab. Panadol 500mg'])")
    print(f"  • Dosage Frequency : {result.get('dosage_frequency')}  (Expected: '1-1-1 (TDS)')")
    print(f"  • Duration         : {result.get('duration')}  (Expected: '2 Days')")

    # Assertions
    assert "Headache" in result["symptoms"], "Symptom extraction failed for Headache!"
    assert any("Panadol 500mg" in med for med in result["medications"]), "Medication extraction failed for Panadol 500mg!"
    assert result["dosage_frequency"] == "1-1-1 (TDS)", "Frequency mapping failed for TDS!"
    assert result["duration"] == "2 Days", "Duration mapping failed for 2 Days!"

    print("\n" + "=" * 65)
    print("ALL ENTITY EXTRACTOR TESTS PASSED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    run_test()
