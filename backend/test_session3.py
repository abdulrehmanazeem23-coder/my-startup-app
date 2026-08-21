"""Test the full pipeline with the user's Session 3 exact Whisper output, including hallucination garbage."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from ai.whisper_service import _clean_character_soup_hallucination, _clean_hallucinated_repetitions
from nlp.autocorrect import autocorrect_transcript
from nlp import extract_full_prescription

# The user's EXACT Whisper output (including the hallucination garbage at the end)
raw_full = ("اسلام علیکم میرے پراسی ایک پیشنٹ آئے محمد تاریق ان کو صور headache اور fever ہے "
    "دو دن سے ان کو میں پلڈٹال 300mg لکھ دیئے جو انہوں نے دن میں دو طایم کھانی ہے چار دن کے لیے "
    "اور Augmentinڈ دیس 500 ملے گرام دکھ لیئی جو اینہوں کو چاردنڑ کھا نی ہے دن مہت تین طاہم "
    "اور پھر ساتھ ان کے بعد مریں پس BIDا چیکپ کے لئے آنا ہے "
    "ٸڈی ای ١ی ٨ی ٰی ٧ی ٵی ٱی ٲی ٴی ٿی ٳی ٟی ٷی ٪ی ٽی وی ٢ی ٠ی "
    "ٍی ّی ٗی ًی ٌی ُی ٓی ٔی هی ٕی ـی ٘ی ِی يی ىی َی فی می نی لی قی "
    "ٚی ٶی پی ٻی ٙ ٟ ٹی ٭ی ٯ ٹ ٹٰی٤ ٹڈ ٹو ٟ٤ٰ ٹق ٹک ٹ کتی كی ٺی ٩ "
    "ٹع ٹٹ ٹپ ٹیک ٹم ٹت ٹب ٹ کے ٹر ٹف ٹئ ٹس ٹل ٹے ٹحی ْ ٹخ ٹری ٹش ٹال ٹین "
    "ٹص ٹلا ٹث ٹط ٹج ٹد ٹچ ٹاد ٹز ٹغ ٹاز ٹاس ٹصل ٹقط اپنے اپنا اپسی بہت اپر اپی "
    "بھی اپتی بھرکی ہے اپا اپپی اپ پی بیٹھنے کے لئے اگر ایک اپٹی بارے میں اپکی بات کرتا ہے ODی میں ایک پیٹی ایک کاری ہے")

print("=" * 65)
print("STEP 1: HALLUCINATION CLEANER")
print("=" * 65)
print(f"Input tokens: {len(raw_full.split())}")

after_rep_clean = _clean_hallucinated_repetitions(raw_full)
after_soup_clean = _clean_character_soup_hallucination(after_rep_clean)

print(f"Output tokens: {len(after_soup_clean.split())}")
print(f"Cleaned: {after_soup_clean}")
print()

print("=" * 65)
print("STEP 2: AUTOCORRECT")
print("=" * 65)
corrected = autocorrect_transcript(after_soup_clean)
print(f"Corrected: {corrected}")
print()

print("=" * 65)
print("STEP 3: EXTRACTION")
print("=" * 65)
ehr = extract_full_prescription(corrected)
for k, v in ehr.items():
    if k != "raw_input":
        print(f"  {k}: {v}")

# Verify
drugs = [m["name"] for m in ehr.get("medications_detailed", [])]
symptoms = ehr.get("symptoms", [])
print()
print("=" * 65)
has_panadol = "Panadol" in drugs
has_augmentin = "Augmentin" in drugs
has_headache = "Headache" in symptoms
has_fever = "Fever" in symptoms

print(f"Panadol found:   {'PASS' if has_panadol else 'FAIL'}")
print(f"Augmentin found: {'PASS' if has_augmentin else 'FAIL'}")
print(f"Headache found:  {'PASS' if has_headache else 'FAIL'}")
print(f"Fever found:     {'PASS' if has_fever else 'FAIL'}")
all_pass = has_panadol and has_augmentin and has_headache and has_fever
print(f"OVERALL: {'ALL PASS' if all_pass else 'SOME FAILED'}")
print("=" * 65)
