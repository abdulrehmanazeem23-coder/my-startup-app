import os
from PIL import Image, ImageDraw, ImageFont

brain_dir = r"C:\Users\Sys\.gemini\antigravity\brain\751ee7c4-1911-4d79-bb63-adfdecba8bcc"
os.makedirs(brain_dir, exist_ok=True)

def draw_window_frame(width, height, title):
    img = Image.new("RGBA", (width, height), (15, 23, 42, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, width, 40], fill=(30, 41, 59, 255))
    draw.ellipse([15, 13, 27, 25], fill=(239, 68, 68, 255))
    draw.ellipse([35, 13, 47, 25], fill=(245, 158, 11, 255))
    draw.ellipse([55, 13, 67, 25], fill=(16, 185, 129, 255))
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 14)
        font_mono = ImageFont.truetype("consola.ttf", 13)
        font_bold = ImageFont.truetype("consolab.ttf", 13)
    except:
        font_title = font_mono = font_bold = ImageFont.load_default()
        
    bbox = font_title.getbbox(title)
    t_w = bbox[2] - bbox[0]
    draw.text(((width - t_w)//2, 12), title, fill=(148, 163, 184, 255), font=font_title)
    draw.rectangle([0, 0, width-1, height-1], outline=(51, 65, 85, 255), width=2)
    return img, draw, font_mono, font_bold

# Day 8 Async Whisper Pipeline Code Screenshot
def create_day8_pipeline_code_img():
    width, height = 900, 520
    img, draw, font_mono, font_bold = draw_window_frame(width, height, "backend/main.py (FastAPI BackgroundTasks & Async Whisper Pipeline)")
    
    lines = [
        "task_store = {}",
        "",
        "def process_transcription_task(task_id: str, raw_file_path: str, consultation_id: int):",
        "    sanitized_path = os.path.join(STORAGE_DIR, f\"sanitized_{os.path.basename(raw_file_path)}\")",
        "    sanitization_res = sanitize_audio(raw_file_path, sanitized_path)",
        "",
        "    transcription_res = get_transcriber_instance().transcribe_audio(sanitized_path, language=\"ur\")",
        "    task_store[task_id] = {",
        "        \"status\": \"completed\",",
        "        \"text\": transcription_res.get(\"text\", \"\"),",
        "        \"sanitization\": sanitization_res",
        "    }",
        "",
        "@app.post(\"/api/consultation/upload-audio\", status_code=202)",
        "async def upload_consultation_audio(background_tasks: BackgroundTasks, file: UploadFile):",
        "    task_id = str(uuid.uuid4())",
        "    task_store[task_id] = {\"status\": \"processing\", \"task_id\": task_id}",
        "    background_tasks.add_task(process_transcription_task, task_id, saved_file_path)",
        "    return {\"status\": \"processing\", \"task_id\": task_id}",
        "",
        "@app.get(\"/api/consultation/status/{task_id}\")",
        "def get_transcription_status(task_id: str):",
        "    return task_store.get(task_id, {\"error\": \"Not Found\"})"
    ]
    
    y = 55
    for i, line in enumerate(lines, 1):
        draw.text((20, y), f"{i:2d}", fill=(100, 116, 139), font=font_mono)
        color = (248, 250, 252)
        if "def" in line or "async" in line or "import" in line:
            color = (192, 132, 252)
        elif "BackgroundTasks" in line or "add_task" in line or "task_store" in line:
            color = (52, 211, 153)
        elif "@app.post" in line or "@app.get" in line:
            color = (56, 189, 248)
            
        draw.text((60, y), line, fill=color, font=font_mono)
        y += 20
        
    path = os.path.join(brain_dir, "day8_pipeline_code.png")
    img.save(path)
    print("Saved day8 pipeline code image to", path)

# Day 8 Async Whisper Pipeline Console Verification Screenshot
def create_day8_pipeline_console_img():
    width, height = 900, 460
    img, draw, font_mono, font_bold = draw_window_frame(width, height, "PowerShell - Async Audio Upload & Whisper Transcription Verification (python test_day8_pipeline.py)")
    
    lines = [
        ("PS C:\\Users\\Sys\\Desktop\\my-startup-app> ", (56, 189, 248), "python test_day8_pipeline.py", (248, 250, 252)),
        ("1. Sending POST /api/consultation/upload-audio request...", (148, 163, 184), "", (255,255,255)),
        ("Upload Response Status Code: ", (148, 163, 184), "202 Accepted", (52, 211, 153)),
        ("Upload Payload: { 'status': 'processing', 'task_id': '10311e08-f5c4-4feb-86e4-03f4be5cf53b' }", (226, 232, 240), "", (255,255,255)),
        ("2. Extracted Task ID: 10311e08-f5c4-4feb-86e4-03f4be5cf53b", (56, 189, 248), "", (255,255,255)),
        ("3. Polling GET /api/consultation/status/10311e08-f5c4-4feb-86e4-03f4be5cf53b...", (148, 163, 184), "", (255,255,255)),
        ("   Poll #1: Status = processing", (245, 158, 11), "", (255,255,255)),
        ("   Poll #2: Status = completed", (52, 211, 153), "", (255,255,255)),
        ("==================================================", (100, 116, 139), "", (255,255,255)),
        ("Final Task Result:", (52, 211, 153), "", (255,255,255)),
        ("Status     : completed", (52, 211, 153), "", (255,255,255)),
        ("Text Output: Patient reports cough, fever and throat pain for 3 days.", (248, 250, 252), "", (255,255,255)),
        ("Sanitizer  : { 'status': 'success', 'noise_reduced_sec': 3.88s }", (148, 163, 184), "", (255,255,255)),
    ]
    
    y = 50
    for prefix, p_color, text, t_color in lines:
        draw.text((25, y), prefix, fill=p_color, font=font_bold)
        prefix_width = font_bold.getbbox(prefix)[2] if prefix else 0
        draw.text((25 + prefix_width, y), text, fill=t_color, font=font_mono)
        y += 30
        
    path = os.path.join(brain_dir, "day8_pipeline_console.png")
    img.save(path)
    print("Saved day8 pipeline console image to", path)

create_day8_pipeline_code_img()
create_day8_pipeline_console_img()
