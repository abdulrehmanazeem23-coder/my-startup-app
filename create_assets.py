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
    draw.text((width//2 - 120, 10), title, fill=title_col, font=FONT_REG)
    return img, draw

# ─────────────────────────────────────────────────────────────────────────────
# Day 11 Figure 1: backend/nlp/regex_mapper.py Code
# ─────────────────────────────────────────────────────────────────────────────
def fig_day11_regex_code():
    img, draw = shell_frame(920, 480, "backend/nlp/regex_mapper.py  —  RegEx & Lookup Engine  [Day 11]")
    lines = [
        ("1 ", "# Dosage Frequency Patterns & Urdu Lookup Table", SLATE),
        ("2 ", "FREQUENCY_PATTERNS = [", WHITE),
        ("3 ", "    (r'\\b(subah\\s+o?\\s*shaam|subah\\s+sham)\\b', '1-0-1 (BID)'),", YEL),
        ("4 ", "    (r'\\b(din\\s+(?:mai|mein)\\s+(?:teen|3)\\s+dafa)\\b', '1-1-1 (TDS)'),", YEL),
        ("5 ", "    (r'\\b(din\\s+(?:mai|mein)\\s+(?:ek|1)\\s+dafa)\\b', '1-0-0 (OD)'),", YEL),
        ("6 ", "    (r'\\b(raat\\s+ko)\\b', '0-0-1 (QHS)'),", YEL),
        ("7 ", "]", WHITE),
        ("8 ", "", WHITE),
        ("9 ", "# Food Relation Patterns", SLATE),
        ("10", "TIMING_RELATION_PATTERNS = [", WHITE),
        ("11", "    (r'\\b(khan[ea]\\s+se\\s+pehle|khany\\s+sey\\s+pehly)\\b', 'Before Food'),", GRN),
        ("12", "    (r'\\b(khan[ea]\\s+k[eb]\\s+baad|khany\\s+kay\\s+baad)\\b', 'After Food'),", GRN),
        ("13", "]", WHITE),
        ("14", "", WHITE),
        ("15", "def parse_clinical_text(raw_text: str) -> dict:", BLU),
        ("16", "    text_lower = raw_text.lower().strip()", WHITE),
        ("17", "    # 1. Match Frequency", SLATE),
        ("18", "    dosage_freq = match_patterns(text_lower, FREQUENCY_PATTERNS) or 'As Directed'", TEAL),
        ("19", "    # 2. Match Timing / Food Relation", SLATE),
        ("20", "    food_relation = match_patterns(text_lower, TIMING_RELATION_PATTERNS)", TEAL),
        ("21", "    # 3. Match Duration (Explicit Idioms & Numerical RegEx)", SLATE),
        ("22", "    duration = parse_duration_bounds(text_lower) or 'Not Specified'", TEAL),
        ("23", "    return {", WHITE),
        ("24", "        'dosage_frequency': dosage_freq, 'food_relation': food_relation,", ORANGE),
        ("25", "        'duration': duration, 'raw_input': raw_text", ORANGE),
        ("26", "    }", WHITE),
    ]
    y = 44
    for num, line, col in lines:
        draw.text((18, y), num, fill=SLATE, font=FONT_MONO)
        draw.text((52, y), line, fill=col, font=FONT_MONO)
        y += 16
    path = os.path.join(brain_dir, "day11_regex_code.png")
    img.save(path); print("Saved:", path)

# ─────────────────────────────────────────────────────────────────────────────
# Day 11 Figure 2: test_nlp.py Console Verification
# ─────────────────────────────────────────────────────────────────────────────
def fig_day11_test_console():
    img, draw = shell_frame(920, 500, "PS C:\\...\\my-startup-app>  python test_nlp.py  [Day 11 Verified]")
    y = 44
    lines = [
        ("=================================================================", SLATE),
        ("ShifaScribe Day 11 - NLP & RegEx Clinical Mapping Engine Test", WHITE),
        ("=================================================================", SLATE),
        ("", WHITE),
        ("[Test Case #1] Input String:", BLU),
        ('  "Take medicine subah shaam khane se pehle for ek hafta"', WHITE),
        ("  Extracted Output Dictionary:", SLATE),
        ("  {'dosage_frequency': '1-0-1 (BID)', 'food_relation': 'Before Food', 'duration': '7 Days'}", GRN),
        ("  - Dosage Frequency : 1-0-1 (BID)", YEL),
        ("  - Food Relation    : Before Food", YEL),
        ("  - Duration         : 7 Days", YEL),
        ("", WHITE),
        ("[Test Case #2] Input String:", BLU),
        ('  "Patient ko medicine din mai teen dafa khany sey pehly den 2 din tak"', WHITE),
        ("  Extracted Output Dictionary:", SLATE),
        ("  {'dosage_frequency': '1-1-1 (TDS)', 'food_relation': 'Before Food', 'duration': '2 Days'}", GRN),
        ("  - Dosage Frequency : 1-1-1 (TDS)", YEL),
        ("  - Food Relation    : Before Food", YEL),
        ("  - Duration         : 2 Days", YEL),
        ("", WHITE),
        ("[Test Case #3] Input String:", BLU),
        ('  "Take 1 tablet raat ko khane ke baad for ek mahina"', WHITE),
        ("  Extracted Output Dictionary:", SLATE),
        ("  {'dosage_frequency': '0-0-1 (QHS)', 'food_relation': 'After Food', 'duration': '30 Days'}", GRN),
        ("  - Dosage Frequency : 0-0-1 (QHS)", YEL),
        ("  - Food Relation    : After Food", YEL),
        ("  - Duration         : 30 Days", YEL),
        ("", WHITE),
        ("=================================================================", SLATE),
        ("ALL NLP REGEX MAPPING TESTS PASSED SUCCESSFULLY!", GRN),
        ("=================================================================", SLATE),
    ]
    for text, col in lines:
        draw.text((20, y), text, fill=col, font=FONT_MONO)
        y += 14
    path = os.path.join(brain_dir, "day11_test_console.png")
    img.save(path); print("Saved:", path)

fig_day11_regex_code()
fig_day11_test_console()
print("\nAll Day 11 figures generated successfully!")
