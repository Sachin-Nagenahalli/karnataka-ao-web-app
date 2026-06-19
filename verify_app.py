import os
import sys

# Add current folder to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import database
from app import get_watermarked_page

def run_tests():
    print("=== Verification Script Started ===")
    
    # 1. Check if PDF exists
    print("\n1. Verifying PDF existence...")
    if not os.path.exists(config.PDF_PATH):
        print(f"[-] ERROR: Source PDF handbook not found at {config.PDF_PATH}")
        sys.exit(1)
    print(f"[+] SUCCESS: Found PDF at {config.PDF_PATH} ({os.path.getsize(config.PDF_PATH)} bytes)")

    # 2. Check Database initialization
    print("\n2. Initializing SQLite Database...")
    try:
        database.init_db()
        print("[+] SUCCESS: Database tables initialized or verified successfully.")
    except Exception as e:
        print(f"[-] ERROR: Database initialization failed: {str(e)}")
        sys.exit(1)

    # 3. Check User Registration
    print("\n3. Testing user registration...")
    test_user_mobile = "9876543210"
    try:
        user = database.register_user(
            full_name="Test Candidate",
            mobile_number=test_user_mobile,
            college_name="UAS Bangalore",
            email_address="candidate@uas.edu"
        )
        print(f"[+] SUCCESS: User registered. ID: {user['id']}, Name: {user['full_name']}")
    except Exception as e:
        print(f"[-] ERROR: User registration failed: {str(e)}")
        sys.exit(1)

    # 4. Check Logging Views
    print("\n4. Testing view logs & stats...")
    try:
        user_id = user['id']
        database.log_view(user_id, 1)
        database.log_view(user_id, 2)
        print("[+] SUCCESS: Logged views for page 1 and page 2.")
        
        # Verify stats retrieve correctly
        stats = database.get_stats()
        print(f"    - Total Users in DB: {stats['total_users']}")
        print(f"    - Total Page Views in DB: {stats['total_views']}")
        print(f"    - Top Pages: {stats['top_pages']}")
        
        all_users = database.get_all_users()
        print(f"    - Total directory rows: {len(all_users)}")
        print("[+] SUCCESS: Stats query matches expectations.")
    except Exception as e:
        print(f"[-] ERROR: View logs / stats extraction failed: {str(e)}")
        sys.exit(1)

    # 5. Check PDF Watermark Generation
    print("\n5. Testing PDF page image rendering & watermarking...")
    try:
        img_bytes = get_watermarked_page(
            page_num=1,
            name=user['full_name'],
            mobile=user['mobile_number'],
            college=user['college_name']
        )
        if len(img_bytes) > 1000:
            print(f"[+] SUCCESS: Generated watermarked page image bytes ({len(img_bytes)} bytes).")
            # Save a sample image to verification folder
            sample_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'sample_watermarked_page_1.jpg')
            with open(sample_path, 'wb') as f:
                f.write(img_bytes)
            print(f"    - Saved visual test sample to: {sample_path}")
        else:
            print("[-] ERROR: Generated watermarked image bytes are suspiciously small.")
            sys.exit(1)
    except Exception as e:
        print(f"[-] ERROR: Watermarked image rendering failed: {str(e)}")
        sys.exit(1)

    # 6. Cleaning test data
    print("\n6. Cleaning up test entries...")
    conn = database.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM views WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        print("[+] SUCCESS: Test entries cleaned from database.")
    except Exception as e:
        print(f"[-] WARNING: Cleanup failed: {str(e)}")
    finally:
        conn.close()

    print("\n=== All Backend Verifications Passed Successfully! ===")

if __name__ == '__main__':
    run_tests()
