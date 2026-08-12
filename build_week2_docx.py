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
    ("Current Status:", "Days 6, 7 & 8 Complete • Active Development"),
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
    "ShifaScribe is an AI-powered Urdu Voice-to-Text Medical Scribe System engineered specifically for high-throughput OPD (Outpatient Department) hospital clinics. Following Sprint 1 (which established the Next.js frontend UI, HTML5 16kHz audio capture, FastAPI backend, and database persistence), Sprint 2 focuses on integrating local artificial intelligence speech recognition, audio sanitization, asynchronous transcription pipelines, clinical NLP entity extraction, and live stream synchronization."
)

add_callout(
    "Week 2 Progress: Days 6, 7 & 8 are 100% complete. Day 6 initialized local OpenAI Whisper-Small speech recognition. Day 7 added CUDA GPU acceleration logic and constructed the Librosa audio sanitization module. Day 8 wired the asynchronous speech-to-text pipeline using FastAPI BackgroundTasks and implemented task status polling via GET /api/consultation/status/{task_id}.",
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
    "Inside backend/ai/whisper_service.py, a dedicated WhisperTranscriber class was constructed. It initializes the open-source openai/whisper-small model using Hugging Face's automatic-speech-recognition pipeline, processing audio streams in 30-second chunk windows."
)

add_image_figure("day6_whisper_code.png", "Figure 1: Code Implementation Screenshot of WhisperTranscriber in backend/ai/whisper_service.py")

add_heading_2("Model Cache Initialization & Verification Test Output")
add_body(
    "A test verification script (backend/test_whisper.py) was executed to instantiate WhisperTranscriber and trigger the automatic download of the openai/whisper-small model weights (~960 MB) into the local Hugging Face cache (~/.cache/huggingface/hub). On execution, the test passed with 100% success."
)

add_image_figure("day6_test_console.png", "Figure 2: Verified Terminal Output Screenshot showing OpenAI Whisper-Small Local Model Initialization & Pipeline Readiness ([SUCCESS] OpenAI Whisper-Small model loaded successfully!)")

# ==================== DAY 7 IMPLEMENTATION ====================
add_heading_1("Day 7 Implementation: CUDA Acceleration & Librosa Audio Sanitization")

add_heading_2("CUDA Hardware Acceleration Logic")
add_body(
    "On Day 7, the WhisperTranscriber service was upgraded with dynamic hardware detection using torch.cuda.is_available(). When a CUDA-compatible GPU (e.g. NVIDIA RTX/Tesla) is present, the pipeline maps to GPU device 0 for accelerated tensor processing, while providing automatic CPU fallback when GPU hardware is unavailable."
)

add_heading_2("Librosa Audio Noise & Silence Sanitization Module")
add_body(
    "To prevent ambient hospital OPD clinic background noises (HVAC fan hum, footsteps, door clicks) and dead silence from degrading speech-to-text accuracy or wasting compute cycles, a dedicated sanitization module was constructed in backend/ai/audio_processor.py. The sanitize_audio(input_path, output_path, top_db=20) function uses librosa.load(sr=16000), applies librosa.effects.trim(top_db=20), and saves the cleaned audio array back to disk using soundfile."
)

add_image_figure("day7_sanitizer_code.png", "Figure 3: Code Implementation Screenshot of sanitize_audio in backend/ai/audio_processor.py")

add_heading_2("Sanitization Verification & Performance Metrics Test Output")
add_body(
    "A test script (backend/test_sanitization.py) was executed passing a 5.0-second raw test audio stream containing leading/trailing room silence and noise. The Librosa sanitization module successfully trimmed 3.88 seconds of silence/noise, yielding a clean 1.12-second audio file (77.6% bandwidth & processing reduction)."
)

add_image_figure("day7_sanitization_console.png", "Figure 4: Verified Terminal Output Screenshot showing Librosa Audio Sanitization Test ([SUCCESS] Audio Sanitization Test Passed! Original: 5.0s, Sanitized: 1.12s, Trimmed: 3.88s)")

# ==================== DAY 8 IMPLEMENTATION ====================
add_heading_1("Day 8 Implementation: Asynchronous Whisper Transcription Pipeline")

add_heading_2("FastAPI BackgroundTasks & Non-Blocking Audio Upload")
add_body(
    "On Day 8, the backend upload endpoint POST /api/consultation/upload-audio was upgraded to integrate FastAPI's BackgroundTasks framework. When an OPD consultation audio file is uploaded, the backend immediately generates a unique UUID task_id, records initial metadata, enqueues a background transcription worker, and returns HTTP 202 Accepted ({'status': 'processing', 'task_id': task_id}) without blocking the client HTTP connection."
)

add_heading_2("Task Store Tracking & Background Worker Logic")
add_body(
    "An in-memory tracking dictionary task_store = {} was implemented alongside a dedicated background worker function process_transcription_task. The background worker automatically: (1) sanitizes raw uploaded audio using Librosa, (2) feeds cleaned 16kHz audio arrays to the local Whisper AI engine for Urdu speech-to-text transcription, and (3) updates task_store[task_id] with status='completed', raw transcription text, and sanitization metrics."
)

add_image_figure("day8_pipeline_code.png", "Figure 5: Code Implementation Screenshot of BackgroundTasks & Whisper Pipeline in backend/main.py")

add_heading_2("Status Polling Endpoint (GET /api/consultation/status/{task_id}) & Test Verification")
add_body(
    "A polling endpoint GET /api/consultation/status/{task_id} was implemented to allow frontend clients to query transcription progress. An automated test script (test_day8_pipeline.py) verified the complete workflow: uploading audio (HTTP 202), extracting task_id, polling status ('processing' -> 'completed'), and retrieving the final transcribed clinical text."
)

add_image_figure("day8_pipeline_console.png", "Figure 6: Verified Terminal Output Screenshot showing Async Upload (HTTP 202), Task ID Polling, and Final Transcribed Text Output")
add_image_figure("day8_swagger_pipeline_ui_1786526912039.jpg", "Figure 7: Interactive FastAPI Swagger OpenAPI Polling UI (http://localhost:8000/docs) displaying GET /status/{task_id} Completed Response")

# ==================== SEQUENTIAL ROADMAP FOR DAYS 9 - 10 ====================
add_heading_1("Sequential Roadmap for Days 9 to 10")

add_heading_2("Day 9 Roadmap: Frontend Live Transcription Stream Integration")
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

# Save Document safely
try:
    doc.save(output_docx)
    print("Successfully updated Week 2 Word report at:", output_docx)
except Exception:
    alt_path = r"c:\Users\Sys\Desktop\my-startup-app\ShifaScribe_Week2_Report_v2.docx"
    doc.save(alt_path)
    print("Main file locked by Microsoft Word. Saved updated report to:", alt_path)
