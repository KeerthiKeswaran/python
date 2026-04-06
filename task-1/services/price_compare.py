from database.db import cursor

def get_price_changes(today, yesterday):
    """Compare prices via SQL JOIN. Falls back to generating a baseline dataset if past data is missing."""
    cursor.execute("SELECT COUNT(*) FROM products WHERE scraped_at = ?", (yesterday,))
    if cursor.fetchone()[0] == 0:
        print("[INFO] No previous day data available. Generating baseline report with today's data.")
        cursor.execute("SELECT name, price FROM products WHERE scraped_at = ?", (today,))
        
        changes = []
        for name, price in cursor.fetchall():
            changes.append((name, price, price, 0.0))
        return changes

    print(f"[DEBUG] Comparing prices -> Target Date: {today} | Reference Date: {yesterday}")
    
    cursor.execute("""
    SELECT t.name, y.price, t.price
    FROM products t
    JOIN products y
    ON t.sku = y.sku
    WHERE t.scraped_at = ? AND y.scraped_at = ?
    """, (today, yesterday))

    rows = cursor.fetchall()
    print(f"[DEBUG] Found {len(rows)} matching products across dates")

    changes = []
    count_changes = 0

    for name, old, new in rows:
        if old != new:
            change = ((new - old) / old) * 100
            changes.append((name, old, new, round(change, 2)))
            count_changes += 1

    return changes, count_changes