import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

brain_dir = r"C:\Users\Sys\.gemini\antigravity\brain\751ee7c4-1911-4d79-bb63-adfdecba8bcc"
output_docx = r"c:\Users\Sys\Desktop\my-startup-app\ShifaScribe_Week2_Report.docx"

doc = docx.Document()

# Page Setup - Normal Margins (1 inch)
for section in doc.sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

# Colors
COLOR_NAVY = RGBColor(15, 23, 42)      # #0F172A
COLOR_TEAL = RGBColor(13, 148, 136)    # #0D9488
COLOR_EMERALD = RGBColor(5, 150, 105)  # #059669
COLOR_GRAY = RGBColor(100, 116, 139)   # #64748B
COLOR_DARK = RGBColor(30, 41, 59)      # #1E293B

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def add_title(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = COLOR_NAVY
    p.paragraph_format.space_before = Pt(40)
    p.paragraph_format.space_after = Pt(8)
    return p

def add_subtitle(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = COLOR_TEAL
    p.paragraph_format.space_after = Pt(24)
    return p

def add_heading_1(text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(18)
    run.font.bold = True
    run.font.color.rgb = COLOR_NAVY
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(8)
    return p

def add_heading_2(text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = COLOR_TEAL
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    return p

def add_body(text, bold=False, italic=False):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(11)
    run.font.color.rgb = COLOR_DARK
    run.font.bold = bold
    run.font.italic = italic
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    return p

def add_callout(text, bold_title=""):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.4)
    p.paragraph_format.right_indent = Inches(0.4)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(8)
    
    if bold_title:
        r_title = p.add_run(bold_title + " ")
        r_title.font.name = 'Calibri'
        r_title.font.size = Pt(11)
        r_title.font.bold = True
        r_title.font.color.rgb = COLOR_EMERALD
        
    r_text = p.add_run(text)
    r_text.font.name = 'Calibri'
    r_text.font.size = Pt(10.5)
    r_text.font.italic = True
    r_text.font.color.rgb = COLOR_DARK
    return p

def add_image_figure(img_filename, caption_text, width_inches=5.8):
    path = os.path.join(brain_dir, img_filename)
    if os.path.exists(path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(12)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(path, width=Inches(width_inches))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(12)
        r_cap = p_cap.add_run(caption_text)
        r_cap.font.name = 'Calibri'
        r_cap.font.size = Pt(9.5)
        r_cap.font.italic = True
        r_cap.font.color.rgb = COLOR_GRAY

# ==================== 1. ENHANCED TITLE PAGE ====================
p_top_badge = doc.add_paragraph()
p_top_badge.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_badge = p_top_badge.add_run("◆ MEDICAL AI ENGINEERING SPRINT • WEEK 2 PROGRESS ◆")
r_badge.font.name = 'Calibri'
r_badge.font.size = Pt(10)
r_badge.font.bold = True
r_badge.font.color.rgb = COLOR_EMERALD
p_top_badge.paragraph_format.space_before = Pt(10)
p_top_badge.paragraph_format.space_after = Pt(20)

p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_title = p_title.add_run("ShifaScribe")
r_title.font.name = 'Calibri'
r_title.font.size = Pt(36)
r_title.font.bold = True
r_title.font.color.rgb = COLOR_NAVY
p_title.paragraph_format.space_after = Pt(4)

p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_sub = p_sub.add_run("AI Urdu Voice-to-Text Medical Scribe System")
r_sub.font.name = 'Calibri'
r_sub.font.size = Pt(18)
r_sub.font.bold = True
r_sub.font.color.rgb = COLOR_TEAL
p_sub.paragraph_format.space_after = Pt(24)

p_div = doc.add_paragraph()
p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_div = p_div.add_run("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
r_div.font.color.rgb = COLOR_EMERALD
r_div.font.bold = True

p_rep = doc.add_paragraph()
p_rep.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_rep = p_rep.add_run("WEEK 2 TECHNICAL IMPLEMENTATION & PROGRESS REPORT")
r_rep.font.name = 'Calibri'
r_rep.font.size = Pt(13)
r_rep.font.bold = True
r_rep.font.color.rgb = COLOR_NAVY
p_rep.paragraph_format.space_before = Pt(18)
p_rep.paragraph_format.space_after = Pt(32)

t_card = doc.add_table(rows=6, cols=2)
t_card.alignment = WD_TABLE_ALIGNMENT.CENTER
t_card.autofit = False

card_data = [
    ("Prepared By (Lead Engineer):", "Abdul Rehman"),
    ("Submitted To (Supervisor):", "Khubaib Ahmed"),
    ("Project Name:", "ShifaScribe (Urdu Medical Speech AI)"),
    ("Reporting Scope:", "Week 2 (Sprint 2: Days 6 to 10)"),
    ("Current Status:", "Day 6 Complete • Active Development"),
    ("Submission Date:", "August 12, 2026"),
]

for i, (label, val) in enumerate(card_data):
    row = t_card.rows[i]
    c1, c2 = row.cells[0], row.cells[1]
    c1.width = Inches(2.6)
    c2.width = Inches(3.7)
    
    if i % 2 == 0:
        set_cell_background(c1, "F1F5F9")
        set_cell_background(c2, "F1F5F9")
        
    p1 = c1.paragraphs[0]
    r1 = p1.add_run(label)
    r1.font.name = 'Calibri'
    r1.font.size = Pt(10.5)
    r1.font.bold = True
    r1.font.color.rgb = COLOR_NAVY
    
    p2 = c2.paragraphs[0]
    r2 = p2.add_run(val)
    r2.font.name = 'Calibri'
    r2.font.size = Pt(10.5)
    r2.font.bold = (i in [0, 1])
    r2.font.color.rgb = COLOR_EMERALD if (i in [0, 1]) else COLOR_DARK

doc.add_page_break()

# ==================== EXECUTIVE SUMMARY ====================
add_heading_1("Executive Summary")

add_body(
    "ShifaScribe is an AI-powered Urdu Voice-to-Text Medical Scribe System engineered specifically for high-throughput OPD (Outpatient Department) hospital clinics. Following the successful completion of Sprint 1 (which established the Next.js frontend UI, HTML5 16kHz audio capture, FastAPI backend, and database persistence), Sprint 2 focuses on integrating local artificial intelligence speech recognition, Urdu language transcription, clinical NLP entity extraction, and live stream synchronization."
)

add_callout(
    "Week 2 Progress: Day 6 is complete. The PyTorch and Hugging Face transformers speech recognition framework has been integrated into backend/ai/whisper_service.py, initializing the local openai/whisper-small model pipeline for Urdu speech-to-text inference.",
    "Sprint 2 Milestone Status:"
)

# ==================== DAY 6 IMPLEMENTATION ====================
add_heading_1("Day 6 Implementation: Local OpenAI Whisper AI Integration")

add_heading_2("AI Engine Architecture & Dependencies")
add_body(
    "On Day 6, the Python backend was upgraded with deep learning speech recognition capabilities. The backend requirements (backend/requirements.txt) were expanded to include torch>=2.2.0, torchaudio>=2.2.0, and transformers>=4.38.0. A dedicated package backend/ai/ was established to encapsulate AI inference modules."
)

add_heading_2("WhisperTranscriber Service Implementation")
add_body(
    "Inside backend/ai/whisper_service.py, a dedicated WhisperTranscriber class was constructed. It initializes the open-source openai/whisper-small model using Hugging Face's automatic-speech-recognition pipeline. The service detects CUDA hardware acceleration automatically, defaulting to CPU execution when GPU acceleration is unavailable, and processes audio streams in 30-second chunk windows."
)

add_image_figure("day6_whisper_code.png", "Figure 1: Code Implementation Screenshot of WhisperTranscriber in backend/ai/whisper_service.py")

add_heading_2("Model Cache Initialization & Verification")
add_body(
    "A test verification script (backend/test_whisper.py) was created to instantiate WhisperTranscriber and trigger the automatic download of the openai/whisper-small model weights (~960 MB) into the local Hugging Face cache (~/.cache/huggingface/hub). On execution, the service verified clean model initialization and pipeline readiness."
)

add_image_figure("day6_test_console.png", "Figure 2: Terminal Output Screenshot verifying OpenAI Whisper-Small Local Model Initialization & Pipeline Readiness")

# ==================== SEQUENTIAL ROADMAP FOR DAYS 7 - 10 ====================
add_heading_1("Sequential Roadmap for Days 7 to 10")

add_heading_2("Day 7 Roadmap: Audio File Ingestion & Whisper Inference Stream")
add_body("[Pending Day 7 Implementation: Connecting uploaded OPD consultation WebM audio files to the WhisperTranscriber service for automated speech-to-text transcription.]", italic=True)

add_heading_2("Day 8 Roadmap: Medical Urdu NLP & ICD-10 Entity Extraction")
add_body("[Pending Day 8 Implementation: Parsing raw transcribed Urdu/English speech into structured clinical JSON entities: Symptoms, Clinical History, Assessment, and ICD-10 codes.]", italic=True)

add_heading_2("Day 9 Roadmap: Live Frontend Transcription & EHR Sync")
add_body("[Pending Day 9 Implementation: Connecting the Next.js Doctor Consult Screen UI to receive real-time transcription buffers and update EHR preview cards.]", italic=True)

add_heading_2("Day 10 Roadmap: Sprint 2 Final Integration & OPD Trial Simulation")
add_body("[Pending Day 10 Implementation: End-to-end OPD consultation workflow trial, error handling, performance benchmark, and supervisor sign-off.]", italic=True)

# ==================== SUPERVISOR EVALUATION & REMARKS ====================
add_heading_1("Supervisor Evaluation, Remarks & Approval")

add_body(
    "This section is reserved for supervisor evaluation, comments, and formal sign-off for the Week 2 Technical Progress of ShifaScribe."
)

t_eval = doc.add_table(rows=5, cols=2)
t_eval.alignment = WD_TABLE_ALIGNMENT.CENTER
t_eval.autofit = False

hdr_cells = t_eval.rows[0].cells
hdr_cells[0].width = Inches(2.2)
hdr_cells[1].width = Inches(4.1)
set_cell_background(hdr_cells[0], "0F172A")
set_cell_background(hdr_cells[1], "0F172A")

p_h0 = hdr_cells[0].paragraphs[0]
r_h0 = p_h0.add_run("Evaluation Field")
r_h0.font.bold = True
r_h0.font.color.rgb = RGBColor(255, 255, 255)

p_h1 = hdr_cells[1].paragraphs[0]
r_h1 = p_h1.add_run("Supervisor Assessment & Details")
r_h1.font.bold = True
r_h1.font.color.rgb = RGBColor(255, 255, 255)

# Row 1: Rating
r1 = t_eval.rows[1]
r1.cells[0].width = Inches(2.2)
r1.cells[1].width = Inches(4.1)
p_r1_lbl = r1.cells[0].paragraphs[0].add_run("Overall Week 2 Rating:")
p_r1_lbl.font.bold = True
p_r1_val = r1.cells[1].paragraphs[0].add_run("[   ] Excellent    [   ] Very Good    [   ] Satisfactory    [   ] Needs Revision")

# Row 2: Remarks Box
r2 = t_eval.rows[2]
r2.cells[0].width = Inches(2.2)
r2.cells[1].width = Inches(4.1)
p_r2_lbl = r2.cells[0].paragraphs[0].add_run("Supervisor Remarks & Feedback:")
p_r2_lbl.font.bold = True

p_r2_val = r2.cells[1].paragraphs[0]
p_r2_val.paragraph_format.space_after = Pt(40)
r_rem = p_r2_val.add_run("(Please write supervisor remarks and evaluation notes here...)\n\n\n\n")
r_rem.font.italic = True
r_rem.font.color.rgb = COLOR_GRAY

# Row 3: Signature
r3 = t_eval.rows[3]
r3.cells[0].width = Inches(2.2)
r3.cells[1].width = Inches(4.1)
p_r3_lbl = r3.cells[0].paragraphs[0].add_run("Supervisor Signature:")
p_r3_lbl.font.bold = True
p_r3_val = r3.cells[1].paragraphs[0].add_run("_________________________________________\nKhubaib Ahmed")

# Row 4: Date & Approval
r4 = t_eval.rows[4]
r4.cells[0].width = Inches(2.2)
r4.cells[1].width = Inches(4.1)
p_r4_lbl = r4.cells[0].paragraphs[0].add_run("Date of Sign-off & Status:")
p_r4_lbl.font.bold = True
p_r4_val = r4.cells[1].paragraphs[0].add_run("Date: ______________, 2026   |   Status: [   ] APPROVED FOR NEXT PHASE")

# Save Document
doc.save(output_docx)
print("Successfully generated Week 2 Word report with unnumbered headings at:", output_docx)
