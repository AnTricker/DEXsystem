
import sqlite3

DB_PATH = "dexsystem.db"

def add_column(cursor, table_name, column_name, column_type):
    try:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        print(f"Added column {column_name} to {table_name}")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print(f"Column {column_name} already exists in {table_name}")
        else:
            print(f"Error adding {column_name}: {e}")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    add_column(cursor, "sales", "note", "TEXT")
    add_column(cursor, "sales", "custom_amount", "FLOAT DEFAULT 0")
    
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
