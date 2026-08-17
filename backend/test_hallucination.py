"""
Test the hallucination cleaner against real Whisper output artifacts.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

from ai.whisper_service import _clean_hallucinated_repetitions
from nlp.autocorrect import autocorrect_transcript
from nlp import extract_full_prescription


def test_hallucination(label, raw):
    print(f"{'='*60}")
    print(f"TEST: {label}")
    print(f"{'='*60}")
    word_count = len(raw.split())
    print(f"RAW ({word_count} words): {raw[:120]}...")
    
    cleaned = _clean_hallucinated_repetitions(raw)
    print(f"AFTER HALLUCINATION CLEANUP: '{cleaned}'")
    
    if cleaned:
        corrected = autocorrect_transcript(cleaned)
        print(f"AFTER AUTOCORRECT: '{corrected}'")
        ehr = extract_full_prescription(corrected)
        print(f"  Symptoms:    {ehr.get('symptoms')}")
        print(f"  Medications: {ehr.get('medications')}")
        print(f"  Frequency:   {ehr.get('dosage_frequency')}")
        print(f"  Duration:    {ehr.get('duration')}")
        print(f"  Advice:      {ehr.get('clinical_notes')}")
    else:
        print("  [HALLUCINATION DETECTED] Empty output — pure noise, no clinical content.")
    print()


# Test 1: User's exact screenshot — pure repetition with clinical tail
test_hallucination(
    "User's screenshot (علمہ repeated ~150 times + real clinical text at the end)",
    "اسلام علمہ " + "علمہ " * 148 + "عل 100 ملکرام جو انہوں نے 3 دن کے لیے دن میں دو مرتبہ کھانی ہے۔ ساتھ ان کے بعد انہوں نے ری چیکپ کے لئے مرے میں روز دوبارہ سے آنا ہے۔"
)

# Test 2: Pure hallucination (nothing real)
test_hallucination(
    "Pure hallucination (no clinical content)",
    "علمہ " * 200
)

# Test 3: Real clinical text with NO hallucination — should be untouched
test_hallucination(
    "Real clinical text (should NOT be modified)",
    "السلام علیکم میرے پیشنٹ آئے ہیں محمد تارک ان کو کافی دنوں سے سوئر headache ہے اور flu بھی ہے جس کی وجہ سین کو ایک دوز لکھ دیئے جو انہوں نے دن میں 3 طیم کھانی ہے 5 دن کے لیے اور پینڈڈال 200 ملگرام کی ایک دوز لکھ دیئے"
)

# Test 4: Short hallucination prefix + valid clinical dictation
test_hallucination(
    "Short hallucination + valid dictation",
    "علمہ علمہ علمہ علمہ علمہ علمہ علمہ Panadol 500mg teen time 5 din ke liye patient ko bukhar hai"
)


print("\n" + "="*60)
print("ALL HALLUCINATION TESTS COMPLETED!")
print("="*60)
