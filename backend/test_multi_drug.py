"""
Test segment-aware per-drug extraction on multi-medicine dictations.
"""
import sys
import re
sys.stdout.reconfigure(encoding="utf-8")

from nlp.autocorrect import autocorrect_transcript
from nlp.regex_mapper import parse_clinical_text
from nlp.drap_validator import validate_medication

KNOWN_DRUGS = [
    "panadol", "paracetamol", "augmentin", "brufen", "ibuprofen", "flagyl",
    "metronidazole", "disprin", "aspirin", "rigix", "softin", "arinac",
    "ponstan", "surbex", "omeprazole", "risek", "gravinate", "entamizole",
    "zantac", "cefspan", "klaricid", "azomax", "basogabin", "flygyl",
    "amoxicillin", "cipro", "ciprofloxacin", "secnidazole", "gaviscon",
    "calpol", "arinate", "famotidine", "loratadine", "cetirizine", "tramal"
]

FORM_PREFIX_MAP = {
    "tab": "Tab.", "tablet": "Tab.", "tablets": "Tab.",
    "cap": "Cap.", "capsule": "Cap.", "capsules": "Cap.",
    "syrup": "Syrup", "syp": "Syrup",
    "inj": "Inj.", "injection": "Inj.",
    "ointment": "Ointment", "drops": "Drops"
}

def extract_medications_with_details(clean_text: str):
    drug_spans = []
    
    # 1. Pattern: [Optional Form] + Drug Name + Strength
    p1 = r"\b(?:(tab|tablet|tablets|cap|capsule|capsules|syrup|syp|inj|injection)\.?\s+)?([a-zA-Z]{3,20})\s+(\d+\s*(?:mg|g|ml|mcg))\b"
    for m in re.finditer(p1, clean_text, re.IGNORECASE):
        form, name, strength = m.group(1), m.group(2), m.group(3)
        if name.lower() in KNOWN_DRUGS or len(name) >= 3:
            if name.lower() not in ["days", "din", "hafta", "month", "hours", "ghante", "take", "for", "sey", "mai", "mein"]:
                drug_spans.append({
                    "start": m.start(),
                    "end": m.end(),
                    "form": form,
                    "name": name,
                    "strength": strength,
                    "match": m.group(0)
                })

    # 2. Pattern: Known drug name without explicit strength adjacent
    for drug in KNOWN_DRUGS:
        for m in re.finditer(r"\b" + re.escape(drug) + r"\b", clean_text, re.IGNORECASE):
            if not any(s["start"] <= m.start() <= s["end"] for s in drug_spans):
                nearby = clean_text[m.end():m.end() + 30]
                sm = re.search(r"\b(\d+\s*(?:mg|g|ml))\b", nearby, re.IGNORECASE)
                strength = sm.group(1) if sm else "500mg"
                drug_spans.append({
                    "start": m.start(),
                    "end": m.end(),
                    "form": None,
                    "name": drug,
                    "strength": strength,
                    "match": m.group(0)
                })

    drug_spans.sort(key=lambda x: x["start"])

    # Remove duplicates matching the exact same drug name
    unique_spans = []
    seen_drugs = set()
    for d in drug_spans:
        if d["name"].lower() not in seen_drugs:
            seen_drugs.add(d["name"].lower())
            unique_spans.append(d)

    medications_detailed = []
    medications_display = []
    
    advice_pattern = r"(?:dobara|recheckup|re-checkup|checkup|visit|چیکپ|وزٹ|چیکٹ|دوارہ|چکپ)"
    advice_match = re.search(advice_pattern, clean_text, re.IGNORECASE)
    advice_start = advice_match.start() if advice_match else len(clean_text)

    for idx, d in enumerate(unique_spans):
        seg_start = d["start"]
        seg_end = unique_spans[idx + 1]["start"] if idx + 1 < len(unique_spans) else advice_start
        seg_text = clean_text[seg_start:seg_end]
        
        parsed = parse_clinical_text(seg_text)
        
        form_clean = FORM_PREFIX_MAP.get((d["form"] or "").lower(), "Tab.")
        if "ml" in d["strength"].lower() and not d["form"]:
            form_clean = "Syrup"
        elif "cap" in (d["form"] or "").lower() or d["name"].lower() in ["risek", "omeprazole"]:
            form_clean = "Cap."
            
        validated_name = validate_medication(f"{form_clean} {d['name'].title()} {d['strength']}")
        
        freq = parsed.get("full_dosage_frequency") or parsed.get("dosage_frequency") or "As Directed"
        dur = parsed.get("duration") or "Not Specified"
        
        if dur != "Not Specified" and freq != "As Directed":
            display_item = f"{validated_name} — {freq}, {dur}"
        elif freq != "As Directed":
            display_item = f"{validated_name} — {freq}"
        elif dur != "Not Specified":
            display_item = f"{validated_name} — {dur}"
        else:
            display_item = validated_name

        medications_detailed.append({
            "name": d["name"].title(),
            "strength": d["strength"].lower(),
            "form": form_clean,
            "formatted": validated_name,
            "frequency": freq,
            "duration": dur,
            "instruction": display_item
        })
        medications_display.append(display_item)

    return medications_display, medications_detailed


# Test Cases
test_inputs = [
    (
        "User 2-Drug Dictation",
        "السلام علیکم میرے پیشنٹ آئے ہیں محمد تارک ان کو کافی دنوں سے سوئر headache ہے اور flu بھی ہے جس کی وجہ اوگمینٹن 500 ملگرام لکھ دی ہے جو انہوں نے دن میں 3 طائم کھانی ہے 5 دن کے لیے اور پینڈول 200 ملگرام کی ایک دوز لکھ دی ہے جو انہوں نے 4 دن کھانی ہے 2 طائم کے لیے اور ساتھ میں پھر انہوں نے میرے پاس 7 دن کے بعد دوبارہ چیکپ کے لیے آنا ہے"
    ),
    (
        "English 3-Drug Dictation",
        "Patient has severe fever. Prescribed Tab Panadol 500mg TDS for 3 days, Cap Risek 40mg OD for 14 days before food, and Tab Brufen 400mg BID for 5 days. Recheckup after 7 days."
    ),
    (
        "Urdu 2-Drug Dictation with Cefspan & Panadol",
        "مریض کو شدید نزلہ اور زکام ہے سین 200 ملگرام 3 طیم 5 دن کے لیے اور پینڈڈال 500 ملگرام 2 طیم 3 دن کے لیے"
    )
]

for label, raw in test_inputs:
    print("=" * 65)
    print(f"TEST: {label}")
    print("=" * 65)
    clean = autocorrect_transcript(raw)
    print(f"Cleaned:\n  {clean}\n")
    display_list, detailed_list = extract_medications_with_details(clean)
    print("Prescribed Medications Display List:")
    for item in display_list:
        print(f"  • {item}")
    print("\nDetailed Structured Breakdown:")
    for d in detailed_list:
        print(f"  Drug: {d['name']} ({d['strength']}) | Form: {d['form']} | Freq: {d['frequency']} | Dur: {d['duration']}")
    print()
