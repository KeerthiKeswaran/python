import sqlite3

# Initialize the global SQLite connection and cursor
conn = sqlite3.connect("products.db")
cursor = conn.cursor()

def init_db():
    """Create the core products table with UNIQUE constraint to prevent duplicate day-inserts."""
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        price REAL,
        sku TEXT,
        scraped_at TEXT,
        UNIQUE(sku, scraped_at)
    )
    """)
    conn.commit()

def insert_products(products, date):
    """Insert product records securely, ignoring any duplicates for the same SKU & date."""
    for p in products:
        cursor.execute("""
        INSERT OR IGNORE INTO products (name, price, sku, scraped_at)
        VALUES (?, ?, ?, ?)
        """, (p.name, p.price, p.sku, date))
    conn.commit()