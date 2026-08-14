import sqlite3

try:
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    cursor.execute('ALTER TABLE artworks ADD COLUMN owner_id INTEGER REFERENCES users(id)')
    conn.commit()
    print("Added owner_id column successfully.")
except sqlite3.OperationalError as e:
    print(f"OperationalError: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
