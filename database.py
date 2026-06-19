import sqlite3
import os
from datetime import datetime
from config import DATABASE_PATH

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
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
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
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
        cursor.execute("SELECT * FROM users WHERE mobile_number = ?", (mobile_number,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            user_id = existing_user['id']
            # Log login / return event
            cursor.execute(
                "INSERT INTO views (user_id, action_type, page_number) VALUES (?, ?, ?)",
                (user_id, 'viewer_load', 0)
            )
            conn.commit()
            return dict(existing_user)
        
        # Insert new user
        cursor.execute('''
            INSERT INTO users (full_name, mobile_number, college_name, email_address)
            VALUES (?, ?, ?, ?)
        ''', (full_name.strip(), mobile_number.strip(), college_name.strip(), email_address.strip() if email_address else None))
        
        user_id = cursor.lastrowid
        
        # Log registration action
        cursor.execute(
            "INSERT INTO views (user_id, action_type, page_number) VALUES (?, ?, ?)",
            (user_id, 'register', 0)
        )
        
        conn.commit()
        
        # Fetch the newly created user
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        new_user = cursor.fetchone()
        return dict(new_user)
        
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def log_view(user_id, page_number):
    """Logs a page view event."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO views (user_id, action_type, page_number) VALUES (?, ?, ?)",
            (user_id, 'page_view', page_number)
        )
        conn.commit()
    except sqlite3.Error:
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
    cursor.execute("SELECT COUNT(*) FROM users")
    stats['total_users'] = cursor.fetchone()[0]
    
    # 2. Total Page Views
    cursor.execute("SELECT COUNT(*) FROM views WHERE action_type = 'page_view'")
    stats['total_views'] = cursor.fetchone()[0]
    
    # 3. Registration Over Time (Daily)
    cursor.execute('''
        SELECT DATE(registration_date) as reg_date, COUNT(*) as count 
        FROM users 
        GROUP BY reg_date 
        ORDER BY reg_date ASC
        LIMIT 30
    ''')
    stats['daily_registrations'] = [dict(row) for row in cursor.fetchall()]
    
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
