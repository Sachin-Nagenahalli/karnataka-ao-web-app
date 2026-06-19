import sqlite3
import os
from datetime import datetime
from config import DATABASE_PATH

# Check for PostgreSQL environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')
IS_POSTGRES = DATABASE_URL is not None

if IS_POSTGRES:
    import psycopg2
    import psycopg2.extras
    # Render databases sometimes start with postgres:// instead of postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_db_connection():
    """Establishes a connection to the database (PostgreSQL or SQLite)."""
    if IS_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
        return conn
    else:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    """Initializes the database schema."""
    if not IS_POSTGRES:
        # Ensure data directory exists for SQLite
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if IS_POSTGRES:
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                full_name TEXT NOT NULL,
                mobile_number TEXT NOT NULL UNIQUE,
                college_name TEXT NOT NULL,
                email_address TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create views table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS views (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                page_number INTEGER,
                action_type TEXT NOT NULL, -- 'register', 'viewer_load', 'page_view'
                viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Create feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Create settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        
        # Insert default settings if not exist
        cursor.execute("INSERT INTO settings (key, value) VALUES ('portal_active', 'true') ON CONFLICT (key) DO NOTHING")
    else:
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                mobile_number TEXT NOT NULL UNIQUE,
                college_name TEXT NOT NULL,
                email_address TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create views table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                page_number INTEGER,
                action_type TEXT NOT NULL, -- 'register', 'viewer_load', 'page_view'
                viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Create feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Create settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        
        # Insert default settings if not exist
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('portal_active', 'true')")
        
    conn.commit()
    conn.close()

def register_user(full_name, mobile_number, college_name, email_address=None):
    """
    Registers a new user or returns existing user details if mobile number is already registered.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user already exists by mobile number
        if IS_POSTGRES:
            cursor.execute("SELECT * FROM users WHERE mobile_number = %s", (mobile_number.strip(),))
        else:
            cursor.execute("SELECT * FROM users WHERE mobile_number = ?", (mobile_number.strip(),))
        existing_user = cursor.fetchone()
        
        if existing_user:
            user_id = existing_user['id']
            # Log login / return event
            if IS_POSTGRES:
                cursor.execute(
                    "INSERT INTO views (user_id, action_type, page_number) VALUES (%s, %s, %s)",
                    (user_id, 'viewer_load', 0)
                )
            else:
                cursor.execute(
                    "INSERT INTO views (user_id, action_type, page_number) VALUES (?, ?, ?)",
                    (user_id, 'viewer_load', 0)
                )
            conn.commit()
            return dict(existing_user)
        
        # Insert new user
        if IS_POSTGRES:
            cursor.execute('''
                INSERT INTO users (full_name, mobile_number, college_name, email_address)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            ''', (full_name.strip(), mobile_number.strip(), college_name.strip(), email_address.strip() if email_address else None))
            user_id = cursor.fetchone()['id']
        else:
            cursor.execute('''
                INSERT INTO users (full_name, mobile_number, college_name, email_address)
                VALUES (?, ?, ?, ?)
            ''', (full_name.strip(), mobile_number.strip(), college_name.strip(), email_address.strip() if email_address else None))
            user_id = cursor.lastrowid
        
        # Log registration action
        if IS_POSTGRES:
            cursor.execute(
                "INSERT INTO views (user_id, action_type, page_number) VALUES (%s, %s, %s)",
                (user_id, 'register', 0)
            )
        else:
            cursor.execute(
                "INSERT INTO views (user_id, action_type, page_number) VALUES (?, ?, ?)",
                (user_id, 'register', 0)
            )
        
        conn.commit()
        
        # Fetch the newly created user
        if IS_POSTGRES:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        else:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        new_user = cursor.fetchone()
        return dict(new_user)
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def log_view(user_id, page_number):
    """Logs a page view event."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if IS_POSTGRES:
            cursor.execute(
                "INSERT INTO views (user_id, action_type, page_number) VALUES (%s, %s, %s)",
                (user_id, 'page_view', page_number)
            )
        else:
            cursor.execute(
                "INSERT INTO views (user_id, action_type, page_number) VALUES (?, ?, ?)",
                (user_id, 'page_view', page_number)
            )
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()

def get_all_users():
    """Retrieves all registered users with their last view activity and total view counts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            u.id, 
            u.full_name, 
            u.mobile_number, 
            u.college_name, 
            u.email_address, 
            u.registration_date,
            COUNT(CASE WHEN v.action_type = 'page_view' THEN 1 END) as total_page_views,
            MAX(v.viewed_at) as last_active
        FROM users u
        LEFT JOIN views v ON u.id = v.user_id
        GROUP BY u.id
        ORDER BY u.registration_date DESC
    '''
    
    cursor.execute(query)
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

def get_stats():
    """Gathers overall metrics and statistics for the dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # 1. Total Registered Users
    cursor.execute("SELECT COUNT(*) as cnt FROM users")
    stats['total_users'] = cursor.fetchone()['cnt']
    
    # 2. Total Page Views
    cursor.execute("SELECT COUNT(*) as cnt FROM views WHERE action_type = 'page_view'")
    stats['total_views'] = cursor.fetchone()['cnt']
    
    # 3. Registration Over Time (Daily)
    if IS_POSTGRES:
        cursor.execute('''
            SELECT CAST(registration_date AS DATE) as reg_date, COUNT(*) as count 
            FROM users 
            GROUP BY reg_date 
            ORDER BY reg_date ASC
            LIMIT 30
        ''')
    else:
        cursor.execute('''
            SELECT DATE(registration_date) as reg_date, COUNT(*) as count 
            FROM users 
            GROUP BY reg_date 
            ORDER BY reg_date ASC
            LIMIT 30
        ''')
        
    daily_regs = []
    for row in cursor.fetchall():
        r_dict = dict(row)
        # Standardize date object to YYYY-MM-DD string
        if r_dict['reg_date'] is not None and not isinstance(r_dict['reg_date'], str):
            r_dict['reg_date'] = r_dict['reg_date'].strftime('%Y-%m-%d')
        daily_regs.append(r_dict)
    stats['daily_registrations'] = daily_regs
    
    # 4. Top Viewed Pages
    cursor.execute('''
        SELECT page_number, COUNT(*) as count 
        FROM views 
        WHERE action_type = 'page_view' 
        GROUP BY page_number 
        ORDER BY count DESC 
        LIMIT 5
    ''')
    stats['top_pages'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return stats

def submit_feedback(user_id, message):
    """Submits candidate feedback to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if IS_POSTGRES:
            cursor.execute(
                "INSERT INTO feedback (user_id, message) VALUES (%s, %s)",
                (user_id, message.strip())
            )
        else:
            cursor.execute(
                "INSERT INTO feedback (user_id, message) VALUES (?, ?)",
                (user_id, message.strip())
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_all_feedback():
    """Retrieves all feedback rows with user details."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
        SELECT 
            f.id, 
            f.message, 
            f.submitted_at, 
            u.full_name, 
            u.mobile_number, 
            u.college_name
        FROM feedback f
        JOIN users u ON f.user_id = u.id
        ORDER BY f.submitted_at DESC
    '''
    cursor.execute(query)
    feedback_list = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return feedback_list

def set_setting(key, value):
    """Sets a system setting value."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if IS_POSTGRES:
            cursor.execute(
                "INSERT INTO settings (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
                (key, str(value))
            )
        else:
            cursor.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, str(value))
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def is_portal_active():
    """Checks if candidate access to the handbook is active."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT value FROM settings WHERE key = 'portal_active'")
        row = cursor.fetchone()
        if row:
            return row['value'].lower() == 'true'
        return True
    except Exception:
        return True
    finally:
        conn.close()
