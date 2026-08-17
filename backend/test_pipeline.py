"""
Comprehensive end-to-end test of the ShifaScribe NLP pipeline.
Tests: autocorrect -> extract_full_prescription for various Urdu/English medical dictations.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

from nlp.autocorrect import autocorrect_transcript
from nlp import extract_full_prescription

def test_case(label, raw):
    print(f"{'='*60}")
    print(f"TEST: {label}")
    print(f"{'='*60}")
    print(f"RAW INPUT:\n  {raw}\n")
    
    corrected = autocorrect_transcript(raw)
    print(f"AFTER AUTOCORRECT:\n  {corrected}\n")
    
    ehr = extract_full_prescription(corrected)
    print(f"EXTRACTED EHR:")
    print(f"  Symptoms:       {ehr.get('symptoms')}")
    print(f"  Medications:    {ehr.get('medications')}")
    print(f"  Frequency:      {ehr.get('dosage_frequency')}")
    print(f"  Duration:       {ehr.get('duration')}")
    print(f"  Clinical Notes: {ehr.get('clinical_notes')}")
    print()
    return ehr


# ═══════════════════════════════════════════════════════════════
# TEST 1: User's exact screenshot text (Urdu script)
# ═══════════════════════════════════════════════════════════════
test_case(
    "User Screenshot Text (Urdu Script)",
    "السلام علیکم میرے پیشنٹ آئے ہیں محمد تارک ان کو کافی دنوں سے سوئر headache ہے اور flu بھی ہے جس کی وجہ سین کو ایک دوز لکھ دیئے جو انہوں نے دن میں 3 طیم کھانی ہے 5 دن کے لیے اور پینڈڈال 200 ملگرام کی ایک دوز لکھ دیئے جو انہوں نے 4 دن کھانی ہے 2 طیم کے لیے اور ساتھ میں پھر انہوں نے میرے پاس 7 دن کے بعد دوارہ سے چکپ کے لیے آنا ہے"
)

# ═══════════════════════════════════════════════════════════════
# TEST 2: Urdu script with بخار, سر درد, Panadol
# ═══════════════════════════════════════════════════════════════
test_case(
    "Urdu Script (بخار + Panadol)",
    "مریض کو بخار ہے اور سر درد ہے اس لیے Panadol 500mg دو ٹائم 5 دن کے لیے"
)

# ═══════════════════════════════════════════════════════════════
# TEST 3: Roman Urdu + English mix
# ═══════════════════════════════════════════════════════════════
test_case(
    "Roman Urdu + English (Augmentin + fever)",
    "patient ko fever hai aur headache hai Augmentin 625mg teen time 7 din"
)

# ═══════════════════════════════════════════════════════════════
# TEST 4: Urdu script phonetic drug name (اوگمینٹن + ملگرام)
# ═══════════════════════════════════════════════════════════════
test_case(
    "Urdu Script Phonetic Drug (اوگمینٹن 500 ملگرام)",
    "پیشنٹ کو سوئر فلو ہے میں نے اوگمینٹن 500 ملگرام لکھی ہے تین طائم 5 دین کے لیے"
)

# ═══════════════════════════════════════════════════════════════
# TEST 5: English with recheckup advice
# ═══════════════════════════════════════════════════════════════
test_case(
    "English recheckup advice",
    "Patient has severe headache and flu, prescribed Tab Panadol 500mg TDS for 5 days. Patient should come for a recheckup after 7 days."
)

# ═══════════════════════════════════════════════════════════════
# TEST 6: Completely Urdu script with common Whisper artifacts
# ═══════════════════════════════════════════════════════════════
test_case(
    "Full Urdu Script (بروفن + فلو + بخار)",
    "مریض کو تیز بخار ہے اور فلو بھی ہے بروفن 400 ملگرام تین ٹائم 3 دن کے لیے"
)

# ═══════════════════════════════════════════════════════════════
# TEST 7: Mixed with misspelled drug name (penadol)
# ═══════════════════════════════════════════════════════════════
test_case(
    "English misspelled drug (penadol 500mg)",
    "patient ko bukhar hai penadol 500mg do time 3 din ke liye khane ke baad"
)

# ═══════════════════════════════════════════════════════════════
# TEST 8: Cefspan in Urdu (سیفسپان)
# ═══════════════════════════════════════════════════════════════
test_case(
    "Urdu Cefspan (سیفسپان/سین)",
    "مریض کو کھانسی ہے سین 200 ملگرام تین طائم 5 دن کے لیے اور 7 دن بعد دوبارہ چیکپ"
)

print("\n" + "="*60)
print("ALL TESTS COMPLETED!")
print("="*60)
