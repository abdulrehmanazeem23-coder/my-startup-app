import os
from PIL import Image, ImageDraw, ImageFont

brain_dir = r"C:\Users\Sys\.gemini\antigravity\brain\751ee7c4-1911-4d79-bb63-adfdecba8bcc"
os.makedirs(brain_dir, exist_ok=True)

def load_fonts():
    for face in ["arialbd.ttf", "calibrib.ttf", "consolab.ttf"]:
        try:
            return (ImageFont.truetype(face, 13),
                    ImageFont.truetype("consolas.ttf", 12),
                    ImageFont.truetype("arial.ttf", 12))
        except:
            pass
    fb = ImageFont.load_default()
    return fb, fb, fb

FONT_BOLD, FONT_MONO, FONT_REG = load_fonts()

# Colour palette
BG       = (13, 17, 23)
BG2      = (22, 27, 34)
BORDER   = (48, 54, 61)
GRN      = (63, 185, 80)
BLU      = (88, 166, 255)
YEL      = (230, 197, 78)
RED      = (248, 81, 73)
TEAL     = (0, 210, 173)
SLATE    = (139, 148, 158)
WHITE    = (230, 237, 243)
ORANGE   = (255, 166, 77)

def shell_frame(width, height, title, title_col=SLATE):
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, width-1, 34], fill=BG2)
    draw.rectangle([0, 0, width-1, height-1], outline=BORDER, width=1)
    for i, c in enumerate([(220,50,47),(230,180,0),(50,205,50)]):
        draw.ellipse([12+i*20, 10, 24+i*20, 22], fill=c)
    draw.text((width//2 - 140, 10), title, fill=title_col, font=FONT_REG)
    return img, draw

# ─────────────────────────────────────────────────────────────────────────────
# Day 14 Figure 11: backend/nlp/autocorrect.py Code
# ─────────────────────────────────────────────────────────────────────────────
def fig_day14_autocorrect_code():
    img, draw = shell_frame(920, 500, "backend/nlp/autocorrect.py  —  Phonetic Auto-Corrector Engine  [Day 14]")
    lines = [
        ("1 ", "CLINICAL_AUTOCORRECT_RULES = [", BLU),
        ("2 ", "    # Panadol & Paracetamol phonetics & Urdu script auto-correction", SLATE),
        ("3 ", "    (r'\\b(penadol|punadol|panadoll|painadol|panadul|پینادول|پیناڈول)\\b', 'Panadol'),", GRN),
        ("4 ", "    (r'\\b(paracetmol|paracetamal|parasitamol|پیراسیٹامول)\\b', 'Paracetamol'),", GRN),
        ("5 ", "    # Brufen & Augmentin phonetics", SLATE),
        ("6 ", "    (r'\\b(brofen|bruffen|bruphen|بروفن)\\b', 'Brufen'),", YEL),
        ("7 ", "    (r'\\b(augmenten|aggmentin|ogmentin|اگمنٹن)\\b', 'Augmentin'),", YEL),
        ("8 ", "]", WHITE),
        ("9 ", "", WHITE),
        ("10", "def autocorrect_transcript(text: str) -> str:", BLU),
        ("11", "    corrected = text", WHITE),
        ("12", "    # Step 1: Rule-based phonetic & Urdu dictionary replacement", TEAL),
        ("13", "    for pattern, replacement in CLINICAL_AUTOCORRECT_RULES:", WHITE),
        ("14", "        corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)", GRN),
        ("15", "", WHITE),
        ("16", "    # Step 2: Token-by-token fuzzy auto-correct against DRAP catalog (Similarity >= 75%)", TEAL),
        ("17", "    for token in tokens:", WHITE),
        ("18", "        match = process.extractOne(clean_word, DRAP_CATALOG, scorer=fuzz.WRatio)", WHITE),
        ("19", "        if match and match[1] >= 75:", BLU),
        ("20", "            token = re.sub(re.escape(clean_word), match[0], token)", GRN),
        ("21", "    return ' '.join(corrected_tokens)", ORANGE),
    ]
    y = 44
    for num, line, col in lines:
        draw.text((18, y), num, fill=SLATE, font=FONT_MONO)
        draw.text((52, y), line, fill=col, font=FONT_MONO)
        y += 16
    path = os.path.join(brain_dir, "day14_autocorrect_code.png")
    img.save(path); print("Saved:", path)

fig_day14_autocorrect_code()
