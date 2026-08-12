import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

brain_dir = r"C:\Users\Sys\.gemini\antigravity\brain\751ee7c4-1911-4d79-bb63-adfdecba8bcc"
output_docx = r"c:\Users\Sys\Desktop\my-startup-app\ShifaScribe_Week3_Report.docx"

doc = docx.Document()

for section in doc.sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

COLOR_NAVY    = RGBColor(15, 23, 42)
COLOR_TEAL    = RGBColor(13, 148, 136)
COLOR_EMERALD = RGBColor(5, 150, 105)
COLOR_GRAY    = RGBColor(100, 116, 139)
COLOR_DARK    = RGBColor(30, 41, 59)

def set_bg(cell, hex_color):
    tcPr = cell._element.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>'))

def h1(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = "Calibri", Pt(18), True, COLOR_NAVY
    p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(18), Pt(8)

def h2(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = "Calibri", Pt(13), True, COLOR_TEAL
    p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(12), Pt(5)

def body(text, italic=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.name, r.font.size, r.font.color.rgb, r.font.italic = "Calibri", Pt(11), COLOR_DARK, italic
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15

def callout(text, label=""):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent, p.paragraph_format.right_indent = Inches(0.4), Inches(0.4)
    p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(6), Pt(8)
    if label:
        rl = p.add_run(label + " ")
        rl.font.name, rl.font.size, rl.font.bold, rl.font.color.rgb = "Calibri", Pt(11), True, COLOR_EMERALD
    rt = p.add_run(text)
    rt.font.name, rt.font.size, rt.font.italic, rt.font.color.rgb = "Calibri", Pt(10.5), True, COLOR_DARK

def figure(filename, caption, width=5.8):
    path = os.path.join(brain_dir, filename)
    if not os.path.exists(path):
        print(f"WARNING: missing figure {filename}")
        return
    pi = doc.add_paragraph()
    pi.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pi.paragraph_format.space_before, pi.paragraph_format.space_after = Pt(10), Pt(3)
    pi.add_run().add_picture(path, width=Inches(width))
    pc = doc.add_paragraph()
    pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pc.paragraph_format.space_after = Pt(10)
    rc = pc.add_run(caption)
    rc.font.name, rc.font.size, rc.font.italic, rc.font.color.rgb = "Calibri", Pt(9.5), True, COLOR_GRAY

# ═══════════════════════════════════════════════════════
# TITLE PAGE
# ═══════════════════════════════════════════════════════
badge = doc.add_paragraph()
badge.alignment = WD_ALIGN_PARAGRAPH.CENTER
rb = badge.add_run("◆  MEDICAL AI ENGINEERING SPRINT  •  WEEK 3 PROGRESS  ◆")
rb.font.name, rb.font.size, rb.font.bold, rb.font.color.rgb = "Calibri", Pt(10), True, COLOR_EMERALD
badge.paragraph_format.space_before, badge.paragraph_format.space_after = Pt(10), Pt(18)

pt = doc.add_paragraph()
pt.alignment = WD_ALIGN_PARAGRAPH.CENTER
rt = pt.add_run("ShifaScribe")
rt.font.name, rt.font.size, rt.font.bold, rt.font.color.rgb = "Calibri", Pt(36), True, COLOR_NAVY
pt.paragraph_format.space_after = Pt(4)

ps = doc.add_paragraph()
ps.alignment = WD_ALIGN_PARAGRAPH.CENTER
rs = ps.add_run("AI Urdu Voice-to-Text Medical Scribe System")
rs.font.name, rs.font.size, rs.font.bold, rs.font.color.rgb = "Calibri", Pt(18), True, COLOR_TEAL
ps.paragraph_format.space_after = Pt(22)

pd = doc.add_paragraph()
pd.alignment = WD_ALIGN_PARAGRAPH.CENTER
pd.add_run("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━").font.color.rgb = COLOR_EMERALD

pr = doc.add_paragraph()
pr.alignment = WD_ALIGN_PARAGRAPH.CENTER
rr = pr.add_run("WEEK 3 TECHNICAL IMPLEMENTATION & PROGRESS REPORT")
rr.font.name, rr.font.size, rr.font.bold, rr.font.color.rgb = "Calibri", Pt(13), True, COLOR_NAVY
pr.paragraph_format.space_before, pr.paragraph_format.space_after = Pt(16), Pt(28)

card_data = [
    ("Prepared By (Lead Engineer):", "Abdul Rehman"),
    ("Submitted To (Supervisor):",   "Khubaib Ahmed"),
    ("Project Name:",                "ShifaScribe (Urdu Medical Speech AI)"),
    ("Reporting Scope:",             "Week 3 (Sprint 3: Days 11 to 15)"),
    ("Verification Status:",         "Day 11 — Tested & Verified (100% Passed)"),
    ("Submission Date:",             "August 12, 2026"),
]
tc = doc.add_table(rows=6, cols=2)
tc.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, (lbl, val) in enumerate(card_data):
    row = tc.rows[i]
    c1, c2 = row.cells[0], row.cells[1]
    c1.width, c2.width = Inches(2.6), Inches(3.7)
    if i % 2 == 0:
        set_bg(c1, "F1F5F9"); set_bg(c2, "F1F5F9")
    r1 = c1.paragraphs[0].add_run(lbl)
    r1.font.name, r1.font.size, r1.font.bold, r1.font.color.rgb = "Calibri", Pt(10.5), True, COLOR_NAVY
    r2 = c2.paragraphs[0].add_run(val)
    r2.font.name, r2.font.size, r2.font.color.rgb = "Calibri", Pt(10.5), COLOR_EMERALD if i < 2 else COLOR_DARK
    r2.font.bold = i < 2

doc.add_page_break()

# ═══════════════════════════════════════════════════════
# EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════
h1("Executive Summary")
body("Sprint 3 (Days 11–15) focuses on Natural Language Processing (NLP), clinical data extraction, ICD-10 medical entity mapping, and automated EHR JSON note generation. Day 11 establishes the foundational RegEx mapping engine and colloquial Urdu-to-Medical conversion lookup tables.")
callout(
    "Day 11 is 100% complete and verified. Built backend/nlp/regex_mapper.py with RegEx pattern matching and entity lookup tables mapping colloquial Urdu idioms ('subah shaam', 'din mai teen dafa', 'khane se pehle', 'ek hafta') to clean medical directives ('1-0-1 (BID)', '1-1-1 (TDS)', 'Before Food', '7 Days'). Passed test verification via test_nlp.py.",
    "Sprint 3 Status:"
)

# ═══════════════════════════════════════════════════════
# DAY 11
# ═══════════════════════════════════════════════════════
h1("Day 11 Implementation: RegEx Mapping Engine & Urdu-to-Medical Conversion Lookup Tables")

h2("NLP Module Directory Architecture")
body("A dedicated backend/nlp/ package was established with an __init__.py exposing the main entrypoint parse_clinical_text(). This module decouples speech recognition from semantic medical parsing.")

h2("RegEx Pattern Rules & Conversion Lookup Tables")
body("backend/nlp/regex_mapper.py contains the entity extraction rules. The engine matches colloquial Urdu and English dictation patterns against standardized medical directives:")

bullet_data = [
    ("Dosage Frequencies:", "'subah shaam' / 'subah sham' → '1-0-1 (BID)'; 'din mai teen dafa' / '3 dafa' → '1-1-1 (TDS)'; 'din mai ek dafa' → '1-0-0 (OD)'; 'raat ko' → '0-0-1 (QHS)'."),
    ("Food & Timing Relations:", "'khane se pehle' / 'khany sey pehly' → 'Before Food'; 'khane ke baad' / 'khany kay baad' → 'After Food'."),
    ("Duration Bounds & Expressions:", "'hafta' / 'ek hafta' → '7 Days'; 'do hafta' → '14 Days'; 'do din' / '2 din' → '2 Days'; 'mahina' / 'ek mahina' → '30 Days'; plus generic RegEx numerical bound extraction for N din / N days / N weeks / N months."),
]

for title, desc in bullet_data:
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(4)
    r1 = p.add_run(title + " ")
    r1.font.name, r1.font.size, r1.font.bold, r1.font.color.rgb = "Calibri", Pt(10.5), True, COLOR_NAVY
    r2 = p.add_run(desc)
    r2.font.name, r2.font.size, r2.font.color.rgb = "Calibri", Pt(10.5), COLOR_DARK

figure("day11_regex_code.png", "Figure 1: backend/nlp/regex_mapper.py — RegEx patterns, lookup tables, and parse_clinical_text() implementation")

h2("Test Verification & Console Execution")
body("The test runner test_nlp.py was executed to verify multi-phrase extraction across multiple code-switched patient dictation sentences. The module correctly identified dosage frequencies, food relations, and durations across all test cases.")
figure("day11_test_console.png", "Figure 2: test_nlp.py output — successful verification of Urdu medical term parsing")

# ═══════════════════════════════════════════════════════
# ROADMAP
# ═══════════════════════════════════════════════════════
h1("Roadmap for Sprint 3 (Days 12–15)")

roadmap_data = [
    ("Day 12:", "NLP ICD-10 & Medical Entity Extraction Engine (extracting symptoms, diagnoses, and medications)."),
    ("Day 13:", "Clinical Schema Builder & Structured JSON Aggregator (building standardized EHR notes)."),
    ("Day 14:", "FastAPI NLP Endpoint & Frontend Dual EHR Auto-Sync (integrating NLP outputs with Next.js UI)."),
    ("Day 15:", "Sprint 3 Integration, End-to-End Clinical OPD Trial, & Final Verification."),
]
for day_title, day_desc in roadmap_data:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    r1 = p.add_run(day_title + " ")
    r1.font.name, r1.font.size, r1.font.bold, r1.font.color.rgb = "Calibri", Pt(11), True, COLOR_TEAL
    r2 = p.add_run(day_desc)
    r2.font.name, r2.font.size, r2.font.italic, r2.font.color.rgb = "Calibri", Pt(10.5), True, COLOR_DARK

# ═══════════════════════════════════════════════════════
# SUPERVISOR EVALUATION
# ═══════════════════════════════════════════════════════
h1("Supervisor Evaluation, Remarks & Approval")
body("This section is reserved for supervisor evaluation and formal sign-off for Week 3.")

te = doc.add_table(rows=5, cols=2)
te.alignment = WD_TABLE_ALIGNMENT.CENTER
hdr = te.rows[0].cells
hdr[0].width, hdr[1].width = Inches(2.2), Inches(4.1)
set_bg(hdr[0], "0F172A"); set_bg(hdr[1], "0F172A")
rh0 = hdr[0].paragraphs[0].add_run("Evaluation Field")
rh0.font.bold = True; rh0.font.color.rgb = RGBColor(255,255,255)
rh1 = hdr[1].paragraphs[0].add_run("Supervisor Assessment & Details")
rh1.font.bold = True; rh1.font.color.rgb = RGBColor(255,255,255)

rows_data = [
    ("Overall Week 3 Rating:", "[   ] Excellent    [   ] Very Good    [   ] Satisfactory    [   ] Needs Revision"),
    ("Supervisor Remarks:",    "(Please write remarks here...)\n\n\n\n"),
    ("Supervisor Signature:",  "_________________________________________\nKhubaib Ahmed"),
    ("Date of Sign-off:",      "Date: ______________, 2026   |   Status: [   ] APPROVED"),
]
for i, (lbl, val) in enumerate(rows_data, 1):
    r = te.rows[i]
    r.cells[0].width, r.cells[1].width = Inches(2.2), Inches(4.1)
    rl = r.cells[0].paragraphs[0].add_run(lbl)
    rl.font.bold = True
    rv = r.cells[1].paragraphs[0].add_run(val)
    if "remarks" in lbl.lower():
        rv.font.italic = True; rv.font.color.rgb = COLOR_GRAY

try:
    doc.save(output_docx)
    print("Saved Week 3 Report to:", output_docx)
except Exception as e:
    print("Error saving report:", e)
