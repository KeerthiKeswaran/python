import sqlite3
import random

def setup_database():
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS sales")
    cursor.execute("""
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region TEXT,
            units INTEGER,
            revenue REAL,
            date TEXT
        )
    """)
    
    regions = ["North", "East", "South", "West"]
    
    # Seed 3,000 records for January 2026
    data = []
    for _ in range(3000):
        region = random.choice(regions)
        units = random.randint(1, 10)
        revenue = units * random.uniform(50.0, 500.0)
        date = f"2026-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        data.append((region, units, revenue, date))
    
    cursor.executemany("INSERT INTO sales (region, units, revenue, date) VALUES (?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()
