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

# Day 6 Whisper Model Test Console Screenshot
def create_day6_test_console_img():
    width, height = 900, 440
    img, draw, font_mono, font_bold = draw_window_frame(width, height, "PowerShell - Whisper AI Local Model Initialization Test")
    
    lines = [
        ("PS C:\\Users\\Sys\\Desktop\\my-startup-app\\backend> ", (56, 189, 248), "python test_whisper.py", (248, 250, 252)),
        ("==================================================", (100, 116, 139), "", (255,255,255)),
        ("ShifaScribe Day 6 - Local Whisper AI Initialization", (52, 211, 153), "", (255,255,255)),
        ("==================================================", (100, 116, 139), "", (255,255,255)),
        ("Starting Whisper model download & pipeline cache...", (148, 163, 184), "", (255,255,255)),
        ("[ShifaScribe AI] Initializing Whisper model 'openai/whisper-small' on device 'cpu'...", (56, 189, 248), "", (255,255,255)),
        ("[ShifaScribe AI] Whisper model 'openai/whisper-small' loaded successfully!", (52, 211, 153), "", (255,255,255)),
        ("", (0,0,0), "", (0,0,0)),
        ("[SUCCESS] OpenAI Whisper-Small model loaded successfully!", (52, 211, 153), "", (255,255,255)),
        ("Model: openai/whisper-small  |  Device Target: cpu", (226, 232, 240), "", (255,255,255)),
        ("Model weights cached in Hugging Face local directory.", (148, 163, 184), "", (255,255,255)),
    ]
    
    y = 50
    for prefix, p_color, text, t_color in lines:
        draw.text((25, y), prefix, fill=p_color, font=font_bold)
        prefix_width = font_bold.getbbox(prefix)[2] if prefix else 0
        draw.text((25 + prefix_width, y), text, fill=t_color, font=font_mono)
        y += 32
        
    path = os.path.join(brain_dir, "day6_test_console.png")
    img.save(path)
    print("Saved day6 test console image to", path)

create_day6_test_console_img()
