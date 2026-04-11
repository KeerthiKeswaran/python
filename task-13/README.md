# Task 13: PDF Report Generator with Templating

## Description
A sophisticated reporting system that pulls monthly sales data from a database, renders it into a customizable Jinja2 template, generates analytical charts using Matplotlib, and produces a polished multi-page PDF report. Includes a simulated email delivery system.

## Features
- **Database Integration**: Fetches structured sales data from SQLite.
- **Dynamic Charting**: Automatically generates region-wise revenue bar charts.
- **HTML/PDF Templating**: Uses `Jinja2` for flexible layouts and `ReportLab` for high-precision PDF generation.
- **Conditional Reporting**: Implements logic to detect and highlight declining regions (e.g., "West region declined").
- **Professional Layout**: Includes headers, summary tables, growth metrics, and time-stamped footers.

## How to Run
```bash
python generate_report.py --month 2026-01 --template sales_monthly
```

## Output
```text
=== Report Generation ===
$ python generate_report.py --month 2026-01 --template sales_monthly
[1/5] Connecting to database... OK
[2/5] Querying January 2026 sales data... OK (3,412 records)
[3/5] Rendering template "sales_monthly"...
 - Header: "Monthly Sales Report — January 2026"
 - Summary Table: revenue, units sold, avg order value
 - Bar Chart: revenue by region (North, South, East, West)
 - Line Chart: daily sales trend
 - Conditional Section: "West region declined 12% MoM" (included)
 - Footer: page numbers, generation timestamp
[4/5] Generating PDF... OK
[5/5] Sending email...
 To: exec-team@company.com, sales-leads@company.com
 Subject: "January 2026 Sales Report"
 Attachment: sales_report_2026-01.pdf (2.4 MB, 6 pages)
 Sent successfully

Output: reports/sales_report_2026-01.pdf

=== PDF Contents (page 1 preview) ===
┌──────────────────────────────────────────────┐
│            MONTHLY SALES REPORT              │
│                January 2026                  │
│──────────────────────────────────────────────│
│ Total Revenue:       $1,247,832              │
│ Units Sold:          3,412                   │
│ Avg Order Value:     $365.72                 │
│ MoM Growth:          +8.3%                   │
│                                              │
│  ┌──────────────────────────────┐            │
│  │      Revenue by Region       │            │
│  │ =====  North: $412K          │            │
│  │ ====   East:  $338K          │            │
│  │ ===    South: $309K          │            │
│  │ ==     West:  $189K (!)      │            │
│  └──────────────────────────────┘            │
└──────────────────────────────────────────────┘
                                   Page 1 of 6  
```
