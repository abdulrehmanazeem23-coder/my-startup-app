"""
Test the NLP pipeline with the user's exact test phrase:
"Assalam O Alaikum, I have got a patient over here whose name is Muhammad Tariq,
He has a severe headache and fever due to which I have given him Panadol 200mg
which he has to take 2 times a day for 3 days and Augmentin 500mg which he has
to take 3 times a day for 5 days. And then he has to come in again after 10 days
for a recheckup."

Expected output:
  Symptoms:    [Headache, Fever]
  Medication1: Tab. Panadol 200mg — BID, 3 Days
  Medication2: Tab. Augmentin 500mg — TDS, 5 Days
  Advice:      Recheckup after 10 days
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from nlp.autocorrect import autocorrect_transcript
from nlp import extract_full_prescription

TEST_CASES = [
    {
        "name": "1. Clean English (ideal Whisper output)",
        "text": (
            "Assalam O Alaikum, I have got a patient over here whose name is Muhammad Tariq. "
            "He has a severe headache and fever due to which I have given him Panadol 200mg "
            "which he has to take 2 times a day for 3 days and Augmentin 500mg which he has "
            "to take 3 times a day for 5 days. And then he has to come in again after 10 days "
            "for a recheckup."
        ),
        "expect_drugs": ["Panadol", "Augmentin"],
        "expect_symptoms": ["Headache", "Fever"],
    },
    {
        "name": "2. Simulated Whisper Urdu Output (bilingual code-switched)",
        "text": (
            "اسلام علیکم میرے پاس ایک پیشنٹ آئے ہیں محمد تاریق ان کو سویئر ہیڈک "
            "اور بخار ہے جس کی وجہ سے میں نے ان کو پینڈال 200 ملگرام لکھ دیئے "
            "جو انہوں نے دن میں 2 طیم کھانی ہے 3 دن کے لیے "
            "اور اوگمینٹن 500 ملگرام لکھ دیئے جو انہوں نے دن میں 3 طیم کھانی ہے "
            "5 دن کے لیے اور پھر 10 دن کے بعد دوبارہ چیکپ کے لیے آنا ہے"
        ),
        "expect_drugs": ["Panadol", "Augmentin"],
        "expect_symptoms": ["Headache", "Fever"],
    },
    {
        "name": "3. Simulated Garbled Whisper (worst-case phonetic noise)",
        "text": (
            "اسلام علیکم مرے پاس ایک پیشنٹ آئے محمد تاریق انکس ور حیڈے کیا "
            "اور فیبر ہے ان کو میں نے پنڈال 200 ملے گرام لکھ دیئے "
            "جو انہوں نے دن میں دو طایم کھانی ہے تین دن کے لیے "
            "اور اگمانٹن 500مج لکھ دیئے جو انہوں نے دن میں تین طاہم کھانی ہے "
            "پانچ دن کے لیے اور پھر 10 دنے کے بعد دوبارہ سے چیکپ کے لیے آنا ہے"
        ),
        "expect_drugs": ["Panadol", "Augmentin"],
        "expect_symptoms": ["Headache", "Fever"],
    },
    {
        "name": "4. English with misspelling (augmentun)",
        "text": (
            "Assalam o alaikum patient Muhammad Tariq has severe headache and fever. "
            "I have given him penadol 200mg 2 times a day for 3 days "
            "and augmentun 500mg 3 times a day for 5 days. "
            "Recheckup after 10 days."
        ),
        "expect_drugs": ["Panadol", "Augmentin"],
        "expect_symptoms": ["Headache", "Fever"],
    },
]

all_pass = True
for tc in TEST_CASES:
    print(f"{'='*70}")
    print(f"TEST: {tc['name']}")
    print(f"{'='*70}")

    clean = autocorrect_transcript(tc["text"])
    print(f"  After Autocorrect: {clean[:120]}...")
    print()

    ehr = extract_full_prescription(clean)

    found_drugs = [m["name"] for m in ehr.get("medications_detailed", [])]
    found_symptoms = ehr.get("symptoms", [])
    drugs_ok = all(d in found_drugs for d in tc["expect_drugs"])
    symptoms_ok = all(s in found_symptoms for s in tc["expect_symptoms"])

    print(f"  Symptoms:       {found_symptoms} {'✓' if symptoms_ok else '✗'}")
    print(f"  Medications:    {ehr['medications']}")
    print(f"  Drugs Found:    {found_drugs} {'✓' if drugs_ok else '✗'}")
    print(f"  Frequency:      {ehr['dosage_frequency']}")
    print(f"  Duration:       {ehr['duration']}")
    print(f"  Clinical Notes: {ehr['clinical_notes']}")

    passed = drugs_ok and symptoms_ok
    if not passed:
        all_pass = False
    print(f"  STATUS: {'PASS ✓' if passed else 'FAIL ✗'}")
    print()

print(f"{'='*70}")
print(f"FINAL RESULT: {'ALL 4 TESTS PASSED ✓' if all_pass else 'SOME TESTS FAILED ✗'}")
print(f"{'='*70}")
