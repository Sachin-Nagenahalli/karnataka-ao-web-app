import os
import sys
from PIL import Image, ImageDraw, ImageFont

# Set up paths
QR_CODE_PATH = "/Users/a2251/.gemini/antigravity/brain/86bf5d45-a18b-46b0-a9a4-f3a820f404b8/media__1781860411436.png"
OUTPUT_DIR = "/Users/a2251/.gemini/antigravity/scratch/karnataka_ao_web_app/data"
OUTPUT_POSTER_PATH = os.path.join(OUTPUT_DIR, "karnataka_ao_handbook_poster.png")
ARTIFACT_POSTER_PATH = "/Users/a2251/.gemini/antigravity/brain/86bf5d45-a18b-46b0-a9a4-f3a820f404b8/karnataka_ao_handbook_poster.png"

def create_poster():
    # Poster Size (High-Res 1200 x 1700, matches A4 aspect ratio)
    width = 1200
    height = 1700
    
    # 1. Create canvas with deep forest green gradient background
    image = Image.new("RGBA", (width, height), (11, 26, 19, 255))
    draw = ImageDraw.Draw(image)
    
    # Draw a subtle gradient from top to bottom
    for y in range(height):
        ratio = y / height
        r = int(9 * (1 - ratio) + 12 * ratio)
        g = int(24 * (1 - ratio) + 16 * ratio)
        b = int(16 * (1 - ratio) + 24 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        
    # 2. Colors & Design elements
    GOLD = (212, 175, 55, 255) # Premium Gold
    LIGHT_GOLD = (255, 215, 0, 255)
    WHITE = (255, 255, 255, 255)
    LIGHT_GREEN = (162, 222, 208, 255)
    DARK_GREEN = (11, 26, 19, 255)
    GRAY = (100, 110, 105, 255)
    
    # Solid Box Background (Slightly lighter forest green for contrast against gradient)
    BOX_BG = (18, 42, 31, 255)
    
    # Draw Gold Border
    border_offset = 25
    draw.rectangle(
        [(border_offset, border_offset), (width - border_offset, height - border_offset)],
        outline=GOLD, width=3
    )
    # Inner thin border
    draw.rectangle(
        [(border_offset + 10, border_offset + 10), (width - border_offset - 10, height - border_offset - 10)],
        outline=GOLD, width=1
    )
    
    # Load fonts
    font_path = "/System/Library/Fonts/Helvetica.ttc"
    if not os.path.exists(font_path):
        font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
        
    font_url = ImageFont.truetype(font_path, 18)
    font_small = ImageFont.truetype(font_path, 20)
    font_medium = ImageFont.truetype(font_path, 25)
    font_large = ImageFont.truetype(font_path, 40)
    font_xlarge = ImageFont.truetype(font_path, 60)
    font_title = ImageFont.truetype(font_path, 72)
    font_italic = ImageFont.truetype(font_path, 24)
    
    # Helper to draw centered text
    def draw_centered_text(text, y, font, color):
        bbox = font.getbbox(text)
        text_w = bbox[2] - bbox[0]
        x = (width - text_w) // 2
        draw.text((x, y), text, fill=color, font=font)
        
    # Helper to draw a custom checkmark
    def draw_checkmark(x, y, size=24, color=LIGHT_GOLD):
        draw.line([(x, y + size//2), (x + size//3, y + size), (x + size, y)], fill=color, width=4)

    # 3. Draw Header Section
    draw_centered_text("KARNATAKA AO / AAO EXAM PREPARATION", 80, font_small, GOLD)
    draw_centered_text("KARNATAKA AO EXAM", 130, font_xlarge, GOLD)
    draw_centered_text("LAST-MINUTE HANDBOOK", 210, font_title, WHITE)
    draw_centered_text("Based on 10 Years Previous Year Question Analysis", 310, font_italic, LIGHT_GREEN)
    
    # Draw a gold separator line
    draw.line([(width//2 - 200, 370), (width//2 + 200, 370)], fill=GOLD, width=2)
    
    # 4. Content Columns Layout
    col_y_start = 420
    col_width = 510
    col_height = 490
    
    # Left Column (Main Features)
    left_x = 75
    draw.rounded_rectangle(
        [(left_x, col_y_start), (left_x + col_width, col_y_start + col_height)],
        radius=12, fill=BOX_BG, outline=GOLD, width=1
    )
    # Left Column Title
    draw.text((left_x + 30, col_y_start + 25), "MAIN FEATURES", fill=GOLD, font=font_large)
    
    features = [
        "10 Years PYQ Analysis",
        "Most Repeated Questions",
        "High-Yield Topics",
        "Expected Questions",
        "Karnataka Agriculture Special",
        "Chapter-Wise Revision Notes",
        "One-Liners & Important Facts",
        "Exam-Oriented Quick Revision"
    ]
    for i, feat in enumerate(features):
        item_y = col_y_start + 90 + (i * 46)
        draw_checkmark(left_x + 35, item_y + 4, size=18)
        draw.text((left_x + 70, item_y), feat, fill=WHITE, font=font_medium)
        
    # Right Column (Access Features)
    right_x = 615
    draw.rounded_rectangle(
        [(right_x, col_y_start), (right_x + col_width, col_y_start + col_height)],
        radius=12, fill=BOX_BG, outline=GOLD, width=1
    )
    # Right Column Title
    draw.text((right_x + 30, col_y_start + 25), "ACCESS SYSTEM", fill=GOLD, font=font_large)
    
    access_feats = [
        "Secure Online Reader Only",
        "View Only (No Download)",
        "Copy & Print Disabled",
        "Personalized Watermarks",
        "Prevents Screenshot Sharing",
        "Mobile & Tablet Friendly"
    ]
    for i, feat in enumerate(access_feats):
        item_y = col_y_start + 90 + (i * 50)
        draw_checkmark(right_x + 35, item_y + 4, size=18)
        draw.text((right_x + 70, item_y), feat, fill=WHITE, font=font_medium)
        
    # 5. How to Access Timeline (Step Cards)
    step_y = 960
    draw_centered_text("HOW TO ACCESS THE HANDBOOK", step_y, font_large, GOLD)
    
    steps = [
        ("1. Register", "Scan the QR code"),
        ("2. Submit Details", "Name, Mobile & College"),
        ("3. Instant Approval", "Authorized access"),
        ("4. Read Handbook", "Online with watermark")
    ]
    step_width = 240
    step_gap = 25
    step_start_x = (width - (4 * step_width + 3 * step_gap)) // 2
    
    for i, (title, desc) in enumerate(steps):
        s_x = step_start_x + (i * (step_width + step_gap))
        # Step card rectangle
        draw.rounded_rectangle(
            [(s_x, step_y + 60), (s_x + step_width, step_y + 175)],
            radius=8, fill=BOX_BG, outline=GOLD, width=1
        )
        
        # Center step title
        bbox_t = font_small.getbbox(title)
        x_t = s_x + (step_width - (bbox_t[2] - bbox_t[0])) // 2
        draw.text((x_t, step_y + 80), title, fill=LIGHT_GOLD, font=font_small)
        
        # Center step desc (wrapped into two lines if needed, or slightly smaller font)
        bbox_d = font_url.getbbox(desc)
        x_d = s_x + (step_width - (bbox_d[2] - bbox_d[0])) // 2
        draw.text((x_d, step_y + 120), desc, fill=WHITE, font=font_url)

    # 6. Bottom Registration Box (White Container with QR Code)
    qr_box_y = 1180
    qr_box_width = 950 # Widened to fit text
    qr_box_height = 430
    qr_box_x = (width - qr_box_width) // 2
    
    draw.rounded_rectangle(
        [(qr_box_x, qr_box_y), (qr_box_x + qr_box_width, qr_box_y + qr_box_height)],
        radius=16, fill=WHITE
    )
    
    # Expose QR Code Image
    if not os.path.exists(QR_CODE_PATH):
        raise FileNotFoundError(f"Source QR Code not found at {QR_CODE_PATH}")
        
    qr_image = Image.open(QR_CODE_PATH)
    qr_size = 320 # Increased slightly
    qr_resized = qr_image.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
    
    # Paste QR Code on the white container box
    qr_paste_x = qr_box_x + 50
    qr_paste_y = qr_box_y + (qr_box_height - qr_size) // 2
    image.paste(qr_resized, (qr_paste_x, qr_paste_y))
    
    # Draw registration details on the right inside the white box
    text_start_x = qr_paste_x + qr_size + 40
    draw.text((text_start_x, qr_box_y + 60), "SCAN TO REGISTER", fill=DARK_GREEN, font=font_large)
    draw.text((text_start_x, qr_box_y + 120), "Scan the QR code with your mobile camera", fill=DARK_GREEN, font=font_small)
    draw.text((text_start_x, qr_box_y + 150), "or visit the website URL below to unlock:", fill=DARK_GREEN, font=font_small)
    
    # Registration Link (Use font_small or custom size to fit exactly)
    url_text = "https://karnataka-ao-web-app.onrender.com/register"
    draw.text((text_start_x, qr_box_y + 200), url_text, fill=DARK_GREEN, font=font_small)
    
    # Security note
    draw.text((text_start_x, qr_box_y + 260), "Secure Platform: No download/print allowed.", fill=GOLD, font=font_url)
    draw.text((text_start_x, qr_box_y + 290), "Every page watermarked with candidate name & mobile.", fill=GRAY, font=font_url)
    
    # Save the output image
    os.makedirs(os.path.dirname(OUTPUT_POSTER_PATH), exist_ok=True)
    
    # Save in high quality
    final_poster = image.convert("RGB")
    final_poster.save(OUTPUT_POSTER_PATH, "PNG", dpi=(300, 300))
    final_poster.save(ARTIFACT_POSTER_PATH, "PNG", dpi=(300, 300))
    print(f"Poster created successfully at: {OUTPUT_POSTER_PATH}")
    print(f"Artifact copy saved to: {ARTIFACT_POSTER_PATH}")

if __name__ == "__main__":
    create_poster()
