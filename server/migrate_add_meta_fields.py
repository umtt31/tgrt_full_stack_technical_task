import sqlite3
import os

def migrate_database():
    """Add meta_keywords and meta_lang columns to the news_articles table"""
    db_path = "tgrt_full_stack_technical_task.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found. Creating new database...")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(news_articles)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'meta_keywords' not in columns:
            print("Adding meta_keywords column...")
            cursor.execute("ALTER TABLE news_articles ADD COLUMN meta_keywords TEXT")
            print("✓ meta_keywords column added")
        else:
            print("meta_keywords column already exists")
        
        if 'meta_lang' not in columns:
            print("Adding meta_lang column...")
            cursor.execute("ALTER TABLE news_articles ADD COLUMN meta_lang TEXT")
            print("✓ meta_lang column added")
        else:
            print("meta_lang column already exists")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database() 