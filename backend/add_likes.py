import sqlite3

try:
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            user_id INTEGER,
            artwork_id INTEGER,
            PRIMARY KEY (user_id, artwork_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(artwork_id) REFERENCES artworks(id)
        )
    ''')
    conn.commit()
    print("Added likes table successfully.")
except sqlite3.OperationalError as e:
    print(f"OperationalError: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
