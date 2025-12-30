import sqlite3
import os

DB_PATH = 'data/quickpoll.db'

def migrate_db():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # Check if column exists
        c.execute("PRAGMA table_info(responses)")
        columns = [info[1] for info in c.fetchall()]
        
        if 'demographic_data' not in columns:
            print("Adding 'demographic_data' column to 'responses' table...")
            c.execute("ALTER TABLE responses ADD COLUMN demographic_data TEXT")
            print("'demographic_data' added.")
            
        if 'user_agent' not in columns:
            print("Adding 'user_agent' column to 'responses' table...")
            c.execute("ALTER TABLE responses ADD COLUMN user_agent TEXT")
            print("'user_agent' added.")

        if 'location_data' not in columns:
            print("Adding 'location_data' column to 'responses' table...")
            c.execute("ALTER TABLE responses ADD COLUMN location_data TEXT")
            print("'location_data' added.")
            
        conn.commit()
        print("Migration check complete.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
