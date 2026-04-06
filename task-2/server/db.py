import sqlite3

conn = sqlite3.connect(".chat.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    user TEXT,
    room TEXT,
    message TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()


def save_message(user, room, message):
    cursor.execute(
        "INSERT INTO messages (user, room, message) VALUES (?, ?, ?)",
        (user, room, message)
    )
    conn.commit()

def get_last_messages(room, limit=50):
    cursor.execute(
        "SELECT user, message, timestamp FROM messages WHERE room = ? ORDER BY timestamp DESC LIMIT ?",
        (room, limit)
    )
    rows = cursor.fetchall()
    return [{"user": row[0], "message": row[1], "timestamp": row[2]} for row in reversed(rows)]