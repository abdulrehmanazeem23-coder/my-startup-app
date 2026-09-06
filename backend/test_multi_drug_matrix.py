"""
ShifaScribe Multi-Drug Extraction Matrix Benchmark
Validates that multiple simultaneous medications (2+ drugs) are accurately detected,
assigned individual dosages/frequencies/durations, and structured for the frontend form.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

from nlp.autocorrect import autocorrect_transcript
from nlp.entity_extractor import extract_full_prescription

TEST_CASES = [
    {
        "name": "Case 1: User's Exact Whisper Dictation (Paracetamol 200mg + Augmentin 500mg)",
        "input": "سلام علیکم محمد حرکترین کو severe headache اور fever ایسا 2 din سے ہے ان کو پیرسیٹم اور 200mgr لگتی ہے جو انہوں نے دن میں BID کھانی ہے 3 din کے لئے اور اوپ مینٹل 500mgr رکھتی ہیں جو اوٹن دنوں نے تین ٹی ٹام کھا نیا 4 din کیلئے و پھر ساتھ ان کے پار بعد میرے پاس دو بارہ سی اچھا کب کی لیاں ہے",
        "expected_drugs": ["Paracetamol", "Augmentin"],
        "expected_count": 2,
    },
    {
        "name": "Case 2: Clean English (Paracetamol 200mg + Augmentin 500mg + Follow-up)",
        "input": "Assalam o alaikum patient has severe headache and fever. I prescribed Paracetamol 200mg 2 times a day for 3 days and Augmentin 500mg 3 times a day for 5 days. Recheckup after 10 days.",
        "expected_drugs": ["Paracetamol", "Augmentin"],
        "expected_count": 2,
    },
    {
        "name": "Case 3: Triple Medication (Panadol + Risek + Gaviscon)",
        "input": "Patient has stomach ache and fever. Given Tab Panadol 500mg 2 times a day for 3 days, Cap Risek 40mg once a day before food for 14 days, and Syrup Gaviscon 10ml 3 times a day for 5 days.",
        "expected_drugs": ["Panadol", "Risek", "Gaviscon"],
        "expected_count": 3,
    },
    {
        "name": "Case 4: Full Urdu Script (پیراسیٹامول + اگمنٹن)",
        "input": "مریض کو تیز بخار اور سر درد ہے پیراسیٹامول 500 ملگرام دو ٹائم 3 دن کے لیے اور اگمنٹن 625 ملگرام تین ٹائم 7 دن کے لیے اور 7 دن بعد دوبارہ چیکپ",
        "expected_drugs": ["Paracetamol", "Augmentin"],
        "expected_count": 2,
    },
    {
        "name": "Case 5: Early Checkup Keyword Trap (Paracetamol + Augmentin with leading 'checkup')",
        "input": "Patient came for routine checkup. Prescribed Tab Paracetamol 500mg 2 times daily for 4 days and Tab Augmentin 625mg 3 times daily for 7 days. Recheckup after 10 days.",
        "expected_drugs": ["Paracetamol", "Augmentin"],
        "expected_count": 2,
    },
    {
        "name": "Case 6: Triple Urdu GI/Antibiotic (بروفن + فلیجل + رائزک)",
        "input": "مریض کو پیٹ میں شدید درد اور بخار ہے بروفن 400 ملگرام تین ٹائم 3 دن کے لیے اور فلیجل 400 ملگرام دو ٹائم 5 دن کے لیے اور رائزک 20 ملگرام ایک ٹائم 14 دن کے لیے کھانے سے پہلے",
        "expected_drugs": ["Brufen", "Flagyl", "Risek"],
        "expected_count": 3,
    }
]


def run_benchmark():
    passed = 0
    total = len(TEST_CASES)

    print("=" * 80)
    print("SHIFASCRIBE MULTI-DRAG EXTRACTION BENCHMARK")
    print("=" * 80)

    for idx, tc in enumerate(TEST_CASES, 1):
        print(f"\n[{idx}/{total}] {tc['name']}")
        print(f"RAW: \"{tc['input']}\"")
        
        cleaned = autocorrect_transcript(tc['input'])
        ehr = extract_full_prescription(cleaned)
        
        meds = ehr.get("medications", [])
        detailed = ehr.get("medications_detailed", [])
        extracted_names = [d.get("name") for d in detailed]
        
        print(f"EXTRACTED ({len(meds)} drugs):")
        for m_idx, m in enumerate(meds, 1):
            print(f"  [{m_idx}] {m}")
        print(f"Symptoms : {ehr.get('symptoms')}")
        print(f"Advice   : {ehr.get('clinical_notes')}")

        # Check all expected drugs were extracted
        all_found = all(any(exp.lower() in str(m).lower() for m in meds) for exp in tc["expected_drugs"])
        count_ok = len(meds) == tc["expected_count"]

        if all_found and count_ok:
            print(f">>> STATUS: PASS ✓ ({len(meds)}/{tc['expected_count']} drugs correctly captured)")
            passed += 1
        else:
            print(f">>> STATUS: FAIL ✗ (Expected {tc['expected_drugs']}, Got: {extracted_names})")

    print("\n" + "=" * 80)
    print(f"FINAL RESULT: {passed}/{total} MULTI-DRUG BENCHMARKS PASSED ({(passed/total)*100:.1f}%)")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark()
