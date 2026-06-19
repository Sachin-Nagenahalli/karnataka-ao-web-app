import os

# Base directory of the web application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Flask settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'karnataka-ao-secret-key-9f8e7d6c5b4a')

# Database path
DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'app.db')

# Secure PDF file location (not accessible directly via public URL)
PDF_PATH = os.path.join(BASE_DIR, 'data', 'handbook.pdf')

# Admin Dashboard credentials
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Admin@AO2026')
