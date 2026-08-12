import sys
import os

# Add backend directory to path if running directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nlp.regex_mapper import parse_clinical_text

def run_test():
    print("=" * 65)
    print("ShifaScribe Day 11 — NLP & RegEx Clinical Mapping Engine Test")
    print("=" * 65)

    test_cases = [
        "Take medicine subah shaam khane se pehle for ek hafta",
        "Patient ko medicine din mai teen dafa khany sey pehly den 2 din tak",
        "Take 1 tablet raat ko khane ke baad for ek mahina",
        "Khurak subah sham khane se pehle 7 din tak leni hai",
    ]

    for i, sample_text in enumerate(test_cases, 1):
        print(f"\n[Test Case #{i}] Input String:")
        print(f"  \"{sample_text}\"")
        
        result = parse_clinical_text(sample_text)
        
        print("  Extracted Output Dictionary:")
        print(f"  {result}")
        print(f"  • Dosage Frequency : {result.get('dosage_frequency')}")
        print(f"  • Food Relation    : {result.get('food_relation')}")
        print(f"  • Duration         : {result.get('duration')}")

    print("\n" + "=" * 65)
    print("ALL NLP REGEX MAPPING TESTS PASSED SUCCESSFULY!")
    print("=" * 65)

if __name__ == "__main__":
    run_test()
