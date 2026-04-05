# Task 1: Web Scraper with Anti-Bot Bypass

## Objective
The primary objective of this task is to build a robust scraper capable of extracting structured data from dynamic, JavaScript-rendered e-commerce websites. The application intelligently navigates anti-bot mechanisms, pagination, and dynamic DOM rendering to cleanly extract product data. The system scales to run natively on a scheduled basis, systematically storing historical statistics to enable robust price-change detection and automated reporting.

## Key Features & Solution Overview
- **Dynamic DOM Rendering**: Leverages Playwright to accurately trace JavaScript-rendered DOM trees and HTTP interception.
- **Data Engineering**: Data structures are seamlessly committed to a local SQLite database, carefully indexed with UNIQUE constraints `(sku, scraped_at)` to actively prevent duplicate inserts across scheduled runs.
- **Price Trend Correlation**: Nightly comparisons evaluate matching SKUs directly against the previous day's baseline. Non-existent historical matrices dynamically default to a baseline tracking frame.
- **Report Generation**: Automatically issues clean, comma-separated values (CSV) detailing exact product price elasticity mapping over standard time matrices.
- **Clean Architecture Principles**: Strong architectural boundary enforcement isolating web extraction drivers `(scraper/)`, persistence layers `(database/)`, and analytic business processes `(services/)`.

## Prerequisites & Dependencies
The following core libraries are integrated to power this automation:
- **Playwright**: For headless browser automation and JS rendering.
- **BeautifulSoup (bs4) & LXML**: For high-performance HTML/CSS element selection and pattern extraction.
- **SQLite3**: Standard library database handling.
- **Python 3.11+**

## Setup Instructions

1. **Install Python Requirements:**
   Ensure your Python environment is active, then install the dependencies via pip:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Ensure you include `playwright` and `beautifulsoup4` in your environment).*

2. **Install Playwright Browsers:**
   Initialize Playwright dependencies to download the necessary headless browser binaries:
   ```bash
   playwright install
   ```

3. **Execute the Application:**
   Run the orchestrator file to trigger the extraction pipeline:
   ```bash
   python main.py
   ```

## Expected Console Output
```text
[START] Scraper started — target: electronics.example.com
[INFO] Page 1/47 — 24 products extracted
[INFO] Page 2/47 — 24 products extracted
...
[INFO] Page 47/47 — 11 products extracted
[INFO] Total: 1,107 products saved to DB

=== Price Change Report ===
Sony WH-1000XM5 Headphones             | $348.00   → $279.99   | -19.5%
Samsung Galaxy S25 Ultra               | $1,299.99 → $1,199.99 | -7.7%
Logitech MX Master 3S                  | $99.99    → $109.99   | +10.0%

3 price changes detected.
[DONE] Report saved to reports/2026-02-24.csv
```
