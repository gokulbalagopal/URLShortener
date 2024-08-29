import sqlite3
import os

# Get the path to the SQLite database 
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'url_shortener.db')

conn = sqlite3.connect(db_path)

cur = conn.cursor()

cur.execute("SELECT * FROM url_mapping")

rows = cur.fetchall()

if rows:
    col_count = len(rows[0])

    headers = ["ID", "Long URL", "Short URL", "Created At", "Expires In (sec)"]
    print(" | ".join(f"{header:<25}" for header in headers[:col_count]))
    print("-" * (27 * col_count))

    for row in rows:
        print(" | ".join(f"{str(item):<25}" for item in row))
else:
    print("No data found in the url_mapping table.")

conn.close()
