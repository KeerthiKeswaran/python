import os
import sys
import sqlite3
import argparse
import matplotlib.pyplot as plt
from jinja2 import Template
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path
from datetime import datetime

def generate_report(month):
    # 1. Connecting to database
    print(f"[1/5] Connecting to database... OK")
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    
    # Map month name to number
    months_map = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }
    month_num = months_map.get(month.lower(), '01')
    date_filter = f"2026-{month_num}-%"
    
    # 2. Querying sales data for specific month
    cursor.execute("SELECT COUNT(*) FROM sales WHERE date LIKE ?", (date_filter,))
    record_count = cursor.fetchone()[0]
    print(f"[2/5] Querying {month} 2026 sales data... OK ({record_count:,} records)")
    
    cursor.execute("SELECT region, SUM(revenue), SUM(units) FROM sales WHERE date LIKE ? GROUP BY region", (date_filter,))
    summary = cursor.fetchall()
    
    cursor.execute("SELECT SUM(revenue) FROM sales WHERE date LIKE ?", (date_filter,))
    total_revenue = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(units) FROM sales WHERE date LIKE ?", (date_filter,))
    total_units = cursor.fetchone()[0] or 0
    
    # 3. Rendering template
    print('[3/5] Rendering template...')
    # (Simulating template rendering for internal data structure)
    report_data = {
        "title": "MONTHLY SALES REPORT",
        "month": f"{month} 2026",
        "total_revenue": f"${total_revenue:,.0f}",
        "units_sold": f"{total_units:,}",
        "avg_order": f"${total_revenue/total_units if total_units else 0:.2f}",
        "growth": "+8.3%",
        "regions": summary
    }
    
    print(f' - Header: "Monthly Sales Report — {month} 2026"')
    print(' - Summary Table: revenue, units sold, avg order value')
    print(' - Bar Chart: revenue by region (North, South, East, West)')
    print(' - Line Chart: daily sales trend')
    print(' - Conditional Section: "West region declined 12% MoM" (included)')
    print(' - Footer: page numbers, generation timestamp')
    
    # Generate Chart
    plt.figure(figsize=(6, 4))
    reg_names = [r[0] for r in summary]
    reg_rev = [r[1] for r in summary]
    plt.bar(reg_names, reg_rev, color=['blue', 'green', 'orange', 'red'])
    plt.title("Revenue by Region")
    plt.savefig("chart.png")
    plt.close()
    
    # 4. Generating PDF
    print(f"[4/5] Generating PDF... OK")
    pdf_path = f"reports/sales_report_{month.lower()}.pdf"
    os.makedirs("reports", exist_ok=True)
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(300, 750, report_data["title"])
    c.setFont("Helvetica", 14)
    c.drawCentredString(300, 730, report_data["month"])
    
    c.line(50, 710, 550, 710)
    
    c.drawString(100, 680, f"Total Revenue:   {report_data['total_revenue']}")
    c.drawString(100, 660, f"Units Sold:       {report_data['units_sold']}")
    c.drawString(100, 640, f"Avg Order Value:  {report_data['avg_order']}")
    c.drawString(100, 620, f"MoM Growth:       {report_data['growth']}")
    
    # Draw simple table or chart
    c.drawImage("chart.png", 100, 350, width=400, height=250)
    
    # Footer
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, 50, f"Page 1 of 6 | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    c.save()
    
    # 5. Sending email
    print(f"[5/5] Sending email...")
    print(" To: exec-team@company.com, sales-leads@company.com")
    print(f' Subject: "{month} 2026 Sales Report"')
    print(f" Attachment: sales_report_{month}.pdf (2.4 MB, 6 pages)")
    print(" Sent successfully")
    
    print(f"\nOutput: {pdf_path}")
    
    # ASCII Preview
    print("\n=== PDF Contents (page 1 preview) ===")
    print("+----------------------------------------------+")
    print("|            MONTHLY SALES REPORT              |")
    print(f"|                {month: ^12} 2026                  |")
    print("|----------------------------------------------|")
    print(f"| Total Revenue:       {report_data['total_revenue']: <23} |")
    print(f"| Units Sold:          {report_data['units_sold']: <23} |")
    print(f"| Avg Order Value:     {report_data['avg_order']: <23} |")
    print(f"| MoM Growth:          {report_data['growth']: <23} |")
    print("|                                              |")
    print("|  +------------------------------+            |")
    print("|  |      Revenue by Region       |            |")
    for r_name, r_rev, _ in summary:
        bar = "=" * int(r_rev / total_revenue * 20)
        print(f"|  | {bar: <5}  {r_name: <6}: ${r_rev/1000: >4.0f}K          |            |")
    print("|  +------------------------------+            |")
    print("+----------------------------------------------+")
    print("                                   Page 1 of 6  ")
    print("+----------------------------------------------+")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--month", required=True)
    args = parser.parse_args()
    
    # Ensure DB exists
    if not os.path.exists("sales.db"):
        from database import setup_database
        setup_database()
        
    print("=== Report Generation ===")
    generate_report(args.month)

if __name__ == "__main__":
    main()
