"""Test with the user's EXACT latest Whisper transcriptions"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from nlp.autocorrect import autocorrect_transcript
from nlp import extract_full_prescription

WHISPER_OUTPUTS = [
    {
        "name": "Session 3 Whisper Output (2026-08-21)",
        "raw": "اسلام علیکم مرے پاس ایک پیشنٹ آئے محمد تاریق ان کو صور headache اور fever ہے دو دن سے ان کو میں پلڈٹال 300mg لکھ دیئے جو انہوں نے دن میں دو طایم کھانی ہے چار دن کے لیے اور Augmentinڈ دیس 500 ملے گرام دکھ لیئی جو اینہوں کو چاردنڑ کھا نی ہے دن مہت تین طاہم اور پھر ساتھ ان کے بعد مریں پس BIDا چیکپ کے لئے آنا ہے",
        "expect_drugs": ["Panadol", "Augmentin"],
        "expect_symptoms": ["Headache", "Fever"],
    },
    {
        "name": "Session 2 Whisper Output (2026-08-20)",
        "raw": "اسلام علیکم ایک پیشنٹ آرکا ہمارے کے ان کو صورت ایڈیکور fever ہے 2 دن سے میں نے ان کو پنڈال 500مج لکھے دیا جو انہوں نے دن میں 3 times 4 دن کے لکھی ہانی ہے اور اگمانٹن 200مج کھانی ہاں لکے دی جو اینہوں پانچ دن دنوں میں 2 times کھا نیے اور پھر 6 دن کی بعد 7 دنے کے بعد میرے بات دوارہ سے چیکپ کے لیان ہے",
        "expect_drugs": ["Panadol", "Augmentin"],
        "expect_symptoms": ["Headache", "Fever"],
    },
    {
        "name": "Session 1 Whisper Output (Urdu Script)",
        "raw": "السلام علیکم میرے پیشنٹ آئے ہیں محمد تارک ان کو کافی دنوں سے سوئر headache ہے اور flu بھی ہے جس کی وجہ سین کو ایک دوز لکھ دیئے جو انہوں نے دن میں 3 طیم کھانی ہے 5 دن کے لیے اور پینڈڈال 200 ملگرام کی ایک دوز لکھ دیئے جو انہوں نے 4 دن کھانی ہے 2 طیم کے لیے اور ساتھ میں پھر انہوں نے میرے پاس 7 دن کے بعد دوارہ سے چکپ کے لیے آنا ہے",
        "expect_drugs": ["Cefspan", "Panadol"],
        "expect_symptoms": ["Headache"],
    },
]

all_pass = True
for tc in WHISPER_OUTPUTS:
    print(f"{'='*65}")
    print(f"TEST: {tc['name']}")
    print(f"{'='*65}")
    
    clean = autocorrect_transcript(tc["raw"])
    print(f"Cleaned: {clean[:100]}...")
    
    ehr = extract_full_prescription(clean)
    
    # Check drugs
    found_drugs = [m["name"] for m in ehr.get("medications_detailed", [])]
    drugs_ok = all(d in found_drugs for d in tc["expect_drugs"])
    
    # Check symptoms
    found_symptoms = ehr.get("symptoms", [])
    symptoms_ok = all(s in found_symptoms for s in tc["expect_symptoms"])
    
    status = "PASS" if (drugs_ok and symptoms_ok) else "FAIL"
    if status == "FAIL":
        all_pass = False
    
    print(f"  Symptoms:    {found_symptoms} {'✓' if symptoms_ok else '✗ EXPECTED: ' + str(tc['expect_symptoms'])}")
    print(f"  Medications: {ehr['medications']}")
    print(f"  Drugs Found: {found_drugs} {'✓' if drugs_ok else '✗ EXPECTED: ' + str(tc['expect_drugs'])}")
    print(f"  Frequency:   {ehr['dosage_frequency']}")
    print(f"  Duration:    {ehr['duration']}")
    print(f"  Advice:      {ehr['clinical_notes']}")
    print(f"  STATUS: {status}")
    print()

print(f"{'='*65}")
print(f"FINAL RESULT: {'ALL TESTS PASSED ✓' if all_pass else 'SOME TESTS FAILED ✗'}")
print(f"{'='*65}")
