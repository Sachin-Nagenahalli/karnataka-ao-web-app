import os
import io
import csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, abort
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont

import config
import database

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Ensure database is initialized on startup
with app.app_context():
    database.init_db()

def get_watermarked_page(page_num, name, mobile, college):
    """
    Loads a PDF page, renders it to an image, and overlays a diagonal
    semi-transparent watermark with candidate details.
    """
    if not os.path.exists(config.PDF_PATH):
        raise FileNotFoundError(f"Source PDF handbook not found at: {config.PDF_PATH}")

    # Open PDF
    doc = fitz.open(config.PDF_PATH)
    if page_num < 1 or page_num > doc.page_count:
        doc.close()
        raise ValueError("Invalid page number requested.")

    # Load page (0-indexed)
    page = doc.load_page(page_num - 1)
    
    # Scale matrix for high quality rendering
    zoom = 1.5
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    
    # Read to PIL Image
    img_data = pix.tobytes("png")
    image = Image.open(io.BytesIO(img_data))
    doc.close()

    # Create RGBA layer for watermark overlay
    watermark_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark_layer)

    # Watermark text payload
    watermark_text = f"{name} ({mobile}) - {college}"

    # Load system font
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf"
    ]
    font = None
    for path in font_paths:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, 28)
                break
            except IOError:
                continue

    if font is None:
        font = ImageFont.load_default()

    # Get text dimensions using getbbox (Pillow 10+ compatible)
    bbox = font.getbbox(watermark_text)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Create rotated text thumbnail image
    text_img = Image.new("RGBA", (text_w + 100, text_h + 40), (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_img)
    # Slate gray text with alpha=95 (approx 37% opacity) for high legibility across all backgrounds
    text_draw.text((50, 20), watermark_text, fill=(120, 120, 120, 95), font=font)
    
    # Rotate text block
    rotated_txt = text_img.rotate(30, expand=True, resample=Image.BICUBIC)
    rot_w, rot_h = rotated_txt.size

    # Tile watermark across the page layout
    w, h = image.size
    y_step = rot_h + 180
    x_step = rot_w + 100
    
    for y in range(-50, h + 100, y_step):
        row_index = y // y_step
        x_offset = (row_index % 2) * (x_step // 2)
        for x in range(-50, w + 100, x_step):
            watermark_layer.paste(rotated_txt, (x + x_offset, y), rotated_txt)

    # Alpha composite the watermark layer
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    combined = Image.alpha_composite(image, watermark_layer)

    # Convert back to RGB and compress as JPEG for light transfers
    final_img = combined.convert("RGB")
    out_io = io.BytesIO()
    final_img.save(out_io, format="JPEG", quality=85)
    out_io.seek(0)
    
    return out_io.getvalue()

@app.route('/')
def index():
    """Home redirect logic based on registration state."""
    if 'user_id' in session:
        return redirect(url_for('viewer'))
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles candidate registration form rendering and validation."""
    if 'user_id' in session:
        return redirect(url_for('viewer'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        mobile = request.form.get('mobile', '').strip()
        college = request.form.get('college', '').strip()
        email = request.form.get('email', '').strip()

        # Server-side validation
        clean_mobile = ''.join(c for c in mobile if c.isdigit())
        
        if len(name) < 3:
            flash("Full Name must be at least 3 characters long.", "error")
            return redirect(url_for('register'))
            
        if len(clean_mobile) != 10:
            flash("Mobile Number must contain exactly 10 digits.", "error")
            return redirect(url_for('register'))
            
        if len(college) < 4:
            flash("College/University name must be at least 4 characters long.", "error")
            return redirect(url_for('register'))

        try:
            # Save to database
            user = database.register_user(
                full_name=name,
                mobile_number=clean_mobile,
                college_name=college,
                email_address=email if email else None
            )
            
            # Setup session
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['user_mobile'] = user['mobile_number']
            session['user_college'] = user['college_name']
            
            return redirect(url_for('viewer'))
            
        except Exception as e:
            flash(f"An error occurred during registration: {str(e)}", "error")
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/viewer')
def viewer():
    """Document reader endpoint for authorized sessions."""
    if 'user_id' not in session:
        return redirect(url_for('register'))

    if not os.path.exists(config.PDF_PATH):
        return "Handbook file not found on the server. Please contact admin.", 500

    # Get page count
    doc = fitz.open(config.PDF_PATH)
    total_pages = doc.page_count
    doc.close()

    return render_template('viewer.html', total_pages=total_pages)

@app.route('/api/page/<int:page_num>')
def api_page(page_num):
    """
    Securely serves a watermarked page image.
    Requires an active registration session.
    """
    if 'user_id' not in session:
        abort(403, description="Unauthorized access. Please register first.")

    user_id = session['user_id']
    name = session['user_name']
    mobile = session['user_mobile']
    college = session['user_college']

    try:
        # Render and watermark page
        img_bytes = get_watermarked_page(page_num, name, mobile, college)
        
        # Log view event
        database.log_view(user_id, page_num)
        
        # Return image response
        response = Response(img_bytes, mimetype='image/jpeg')
        # Instruct browser to cache temporarily for performance during page flipping
        response.headers['Cache-Control'] = 'private, max-age=600'
        return response
        
    except ValueError:
        abort(404, description="Page not found.")
    except Exception as e:
        app.logger.error(f"Error serving page {page_num}: {str(e)}")
        abort(500, description="Internal server error occurred.")

@app.route('/logout')
def logout():
    """Logs the user out and clears the session."""
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_mobile', None)
    session.pop('user_college', None)
    return redirect(url_for('register'))

# ----------------------------------------------------------------
# Admin Section
# ----------------------------------------------------------------

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Admin login and reporting dashboard."""
    error = None
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == config.ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('admin'))
        else:
            error = "Invalid admin password."

    is_admin = session.get('is_admin', False)
    
    if is_admin:
        users = database.get_all_users()
        stats = database.get_stats()
        return render_template('admin.html', is_admin=True, users=users, stats=stats)
        
    return render_template('admin.html', is_admin=False, error=error)

@app.route('/admin/export')
def admin_export():
    """Exports registered user details to CSV format."""
    if not session.get('is_admin', False):
        abort(403, description="Access denied.")

    users = database.get_all_users()
    
    # Generate CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'ID', 'Candidate Name', 'Mobile Number', 'College/University Name', 
        'Email Address', 'Registration Date', 'Total Page Views', 'Last Active'
    ])
    
    for u in users:
        writer.writerow([
            u['id'],
            u['full_name'],
            u['mobile_number'],
            u['college_name'],
            u['email_address'] or '',
            u['registration_date'],
            u['total_page_views'],
            u['last_active'] or ''
        ])
    
    csv_data = output.getvalue()
    response = Response(csv_data, mimetype='text/csv')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    response.headers['Content-Disposition'] = f'attachment; filename=karnataka_ao_users_{timestamp}.csv'
    return response

@app.route('/admin/logout')
def admin_logout():
    """Logs the admin out of the session."""
    session.pop('is_admin', None)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    # Initialize DB (safety check)
    database.init_db()
    # Run server locally
    app.run(host='127.0.0.1', port=5000, debug=True)
