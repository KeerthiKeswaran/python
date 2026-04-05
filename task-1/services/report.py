import csv
import os

def generate_report(changes, filename):
    """Safely prepare directories and write the final extracted price variations straight to CSV."""
    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Product", "Old Price", "New Price", "Change %"])

        for row in changes:
            writer.writerow(row)