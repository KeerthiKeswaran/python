from scraper.playwright_scraper import scrape_page
from scraper.parser import parse_products
from database.db import init_db, insert_products
from services.price_compare import get_price_changes
from services.report import generate_report
from config.settings import BASE_URL
from datetime import datetime, timedelta

def run():
    init_db()
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    all_products = []

    total_pages = 3  # keep low for Amazon safety

    print(f"[START] Scraper started — target: {BASE_URL}")

    for i in range(1, total_pages + 1):
        url = BASE_URL.format(i)

        print(f"[INFO] Page {i}/{total_pages} — Fetching...")

        html = scrape_page(url)

        if not html:
            print(f"[ERROR] Page {i} failed — skipping")
            continue

        # Detect block / captcha
        if "captcha" in html.lower():
            print(f"[BLOCKED] CAPTCHA detected on page {i}")
            continue

        products = parse_products(html)

        print(f"[INFO] Page {i}/{total_pages} — {len(products)} products extracted")

        all_products.extend(products)

    # Save to DB
    insert_products(all_products, str(today))

    print(f"[INFO] Total: {len(all_products)} products saved to DB")

    # Compare prices
    changes = get_price_changes(str(today), str(yesterday))

    # Generate report
    report_file = f"reports/{today}.csv"
    generate_report(changes, report_file)

    print("\n=== Price Change Report ===")
    actual_changes_count = 0
    for name, old, new, change in changes:
        if old != new:
            actual_changes_count += 1
        print(f"{name[:40]} | {old} → {new} | {change}%")

    print(f"\n{actual_changes_count} price changes detected.")
    print(f"[DONE] Report saved to {report_file}")


if __name__ == "__main__":
    run()