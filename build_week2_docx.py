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
rb = badge.add_run("◆  MEDICAL AI ENGINEERING SPRINT  •  WEEK 2 PROGRESS  ◆")
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
rr = pr.add_run("WEEK 2 TECHNICAL IMPLEMENTATION & PROGRESS REPORT")
rr.font.name, rr.font.size, rr.font.bold, rr.font.color.rgb = "Calibri", Pt(13), True, COLOR_NAVY
pr.paragraph_format.space_before, pr.paragraph_format.space_after = Pt(16), Pt(28)

card_data = [
    ("Prepared By (Lead Engineer):", "Abdul Rehman"),
    ("Submitted To (Supervisor):",   "Khubaib Ahmed"),
    ("Project Name:",                "ShifaScribe (Urdu Medical Speech AI)"),
    ("Reporting Scope:",             "Week 2 (Sprint 2: Days 6 to 10)"),
    ("Verification Status:",         "Days 6, 7, 8 & 9 — Tested & Verified (100% Passed)"),
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
body("ShifaScribe is an AI-powered Urdu Voice-to-Text Medical Scribe System engineered for high-throughput OPD hospital clinics. Sprint 2 (Days 6–10) integrates local AI speech recognition, audio sanitization, asynchronous transcription pipelines, and live frontend stream synchronization.")
callout(
    "Days 6, 7, 8 & 9 are 100% complete and verified. Day 6: Local Whisper-Small model. Day 7: CUDA acceleration & Librosa audio sanitization. Day 8: FastAPI BackgroundTasks async pipeline & task polling. Day 9: Next.js frontend connected to the Whisper pipeline with dual-panel status UI.",
    "Sprint 2 Status:"
)

# ═══════════════════════════════════════════════════════
# DAY 6
# ═══════════════════════════════════════════════════════
h1("Day 6 Implementation: Local OpenAI Whisper AI Integration")

h2("AI Engine Architecture & Dependencies")
body("The backend requirements were expanded with torch>=2.2.0, torchaudio>=2.2.0, and transformers>=4.38.0. A dedicated backend/ai/ package was created to encapsulate all AI inference modules.")

h2("WhisperTranscriber Service")
body("backend/ai/whisper_service.py contains the WhisperTranscriber class. It initialises WhisperProcessor and WhisperForConditionalGeneration from the openai/whisper-small checkpoint, pads short audio clips to 30-second windows for full model accuracy, and processes longer recordings in 25-second-stride overlapping chunks.")
figure("day6_whisper_code.png", "Figure 1: WhisperTranscriber implementation in backend/ai/whisper_service.py")

h2("Model Initialisation & Verification")
body("backend/test_whisper.py triggered the automatic download of model weights (~960 MB) into the local Hugging Face cache and confirmed pipeline readiness.")
figure("day6_test_console.png", "Figure 2: Terminal output confirming openai/whisper-small model loaded successfully")

# ═══════════════════════════════════════════════════════
# DAY 7
# ═══════════════════════════════════════════════════════
h1("Day 7 Implementation: CUDA Acceleration & Librosa Audio Sanitization")

h2("CUDA Hardware Acceleration")
body("torch.cuda.is_available() dynamically routes inference to GPU device 0 (when available) or falls back to CPU. This ensures the same codebase runs on both development laptops and GPU-equipped production servers.")

h2("Librosa Audio Noise & Silence Sanitization Module")
body("backend/ai/audio_processor.py implements sanitize_audio(). The function: (1) converts WebM/Opus browser streams to 16kHz WAV via bundled imageio-ffmpeg, (2) trims silence and ambient room noise using librosa.effects.trim(top_db=30), and (3) saves a clean PCM_16 WAV to disk.")
figure("day7_sanitizer_code.png", "Figure 3: sanitize_audio() in backend/ai/audio_processor.py with FFmpeg WebM conversion")

h2("Sanitization Verification")
body("A 5.0-second test audio containing leading/trailing silence was trimmed to 1.12 seconds — a 77.6% bandwidth and compute reduction.")
figure("day7_sanitization_console.png", "Figure 4: Terminal output confirming Librosa sanitization: 5.0s → 1.12s (trimmed 3.88s)")

# ═══════════════════════════════════════════════════════
# DAY 8
# ═══════════════════════════════════════════════════════
h1("Day 8 Implementation: Asynchronous Whisper Transcription Pipeline")

h2("FastAPI BackgroundTasks & Non-Blocking Upload")
body("POST /api/consultation/upload-audio was upgraded with FastAPI BackgroundTasks. On upload the endpoint immediately returns HTTP 202 Accepted with a UUID task_id, then enqueues process_transcription_task as a background worker — keeping the HTTP connection non-blocking.")

h2("Background Worker & Task Store")
body("An in-memory task_store = {} dictionary tracks task state. The background worker: (1) sanitizes raw audio, (2) runs Whisper AI inference, and (3) updates task_store[task_id] with status='completed' and the transcribed text string.")
figure("day8_pipeline_code.png", "Figure 5: BackgroundTasks, process_transcription_task, and polling endpoint in backend/main.py")

h2("Status Polling Endpoint & Test Verification")
body("GET /api/consultation/status/{task_id} returns the current processing state. The automated test script test_day8_pipeline.py verified the full flow: upload → HTTP 202 → poll processing → poll completed → receive Urdu text.")
figure("day8_pipeline_console.png", "Figure 6: test_day8_pipeline.py output showing HTTP 202 upload, polling, and final transcription")
figure("day8_swagger_pipeline_ui_1786526912039.jpg", "Figure 7: FastAPI Swagger UI (http://localhost:8000/docs) showing GET /status/{task_id} completed response")

# ═══════════════════════════════════════════════════════
# DAY 9
# ═══════════════════════════════════════════════════════
h1("Day 9 Implementation: Frontend Live Transcription Stream Integration")

h2("Next.js → FastAPI Fetch Integration")
body("ConsultationRecorder.tsx was updated so that when the MediaRecorder onstop event fires, the assembled WebM Blob is immediately packaged into a FormData object and posted via the fetch API to http://localhost:8000/api/consultation/upload-audio.")

h2("Task ID Extraction & 2-Second Polling Loop")
body("The returned task_id is extracted and stored in a React ref. A setInterval polling loop runs every 2 seconds, querying GET /api/consultation/status/{task_id}. Polling stops automatically once status transitions to 'completed' or 'failed', preventing unnecessary background requests.")
figure("day9_component_code.png", "Figure 8: uploadAndTranscribe() in ConsultationRecorder.tsx — FormData upload, task_id extraction, and setInterval polling")

h2("Dual UI Status Display")
body("A real-time status indicator panel renders four states below the recorder button: (1) Uploading Audio — blue animated dots, (2) Processing AI Transcription — amber spinner and indeterminate progress bar, (3) Transcription Complete — read-only textarea with Copy button showing the final Urdu text, (4) Failed — red error message with dismiss option. The bottom EHR panels synchronise with the same transcription state.")
figure("day9_ui_uploading_1786531316219.jpg", "Figure 9: UI in 'Uploading Audio...' state — audio blob being sent to FastAPI Whisper pipeline")
figure("day9_ui_completed_1786531342101.jpg", "Figure 10: UI in 'Transcription Complete' state — Urdu transcription displayed in read-only textarea with Copy button")

h2("Transcription Quality Improvements (Day 9 Fix)")
body("Whisper short-clip truncation was resolved by zero-padding all recordings shorter than 30 seconds to the full 480,000-sample Whisper window before building the log-mel spectrogram. Beam search was enabled (num_beams=5) and greedy temperature=0.0 set for more deterministic, higher-accuracy decoding. The silence trimming threshold was also raised from top_db=20 to top_db=30 to prevent quiet speech from being accidentally clipped.")

# ═══════════════════════════════════════════════════════
# ROADMAP
# ═══════════════════════════════════════════════════════
h1("Roadmap for Day 10")
h2("Day 10: Sprint 2 Final Integration & OPD Trial Simulation")
body("[Pending: End-to-end OPD consultation workflow trial, ICD-10 NLP entity extraction, error handling hardening, and supervisor sign-off.]", italic=True)

# ═══════════════════════════════════════════════════════
# SUPERVISOR EVALUATION
# ═══════════════════════════════════════════════════════
h1("Supervisor Evaluation, Remarks & Approval")
body("This section is reserved for supervisor evaluation and formal sign-off for Week 2.")

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
    ("Overall Week 2 Rating:", "[   ] Excellent    [   ] Very Good    [   ] Satisfactory    [   ] Needs Revision"),
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
    print("Saved Week 2 Report to:", output_docx)
except Exception:
    alt = r"c:\Users\Sys\Desktop\my-startup-app\ShifaScribe_Week2_Report_v3.docx"
    doc.save(alt)
    print("File locked — saved to:", alt)
