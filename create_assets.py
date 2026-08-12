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

# Day 6 Whisper AI Service Code Screenshot
def create_day6_whisper_img():
    width, height = 900, 520
    img, draw, font_mono, font_bold = draw_window_frame(width, height, "backend/ai/whisper_service.py (Hugging Face OpenAI Whisper-Small Pipeline)")
    
    lines = [
        "import os, torch",
        "from transformers import pipeline",
        "",
        "class WhisperTranscriber:",
        "    def __init__(self, model_name: str = \"openai/whisper-small\"):",
        "        self.model_name = model_name",
        "        self.device = \"cuda:0\" if torch.cuda.is_available() else \"cpu\"",
        "        print(f\"[ShifaScribe AI] Loading Whisper '{model_name}' on '{self.device}'...\")",
        "",
        "        self.pipe = pipeline(",
        "            \"automatic-speech-recognition\",",
        "            model=self.model_name,",
        "            device=self.device,",
        "            chunk_length_s=30",
        "        )",
        "",
        "    def transcribe_audio(self, file_path: str, language: str = \"ur\") -> dict:",
        "        result = self.pipe(file_path, generate_kwargs={\"task\": \"transcribe\", \"language\": language})",
        "        return {\"status\": \"success\", \"text\": result.get(\"text\", \"\").strip()}"
    ]
    
    y = 55
    for i, line in enumerate(lines, 1):
        draw.text((20, y), f"{i:2d}", fill=(100, 116, 139), font=font_mono)
        color = (248, 250, 252)
        if "class" in line or "def" in line or "from" in line or "import" in line:
            color = (192, 132, 252)
        elif "pipeline" in line or "openai/whisper-small" in line:
            color = (52, 211, 153)
        elif "transcribe_audio" in line or "generate_kwargs" in line:
            color = (56, 189, 248)
            
        draw.text((60, y), line, fill=color, font=font_mono)
        y += 22
        
    path = os.path.join(brain_dir, "day6_whisper_code.png")
    img.save(path)
    print("Saved day6 whisper image to", path)

create_day6_whisper_img()
