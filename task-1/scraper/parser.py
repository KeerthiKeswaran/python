from bs4 import BeautifulSoup
from database.models import Product

def parse_products(html):
    """Parse product listings from raw HTML, safely extracting names, numeric prices, and SKUs."""
    soup = BeautifulSoup(html, "lxml")
    products = []

    items = soup.select("div[data-component-type='s-search-result']")

    for item in items:
        try:
            sku = item.get("data-asin")
            if not sku:
                continue

            name = item.select_one("h2 span").text.strip()

            price_whole = item.select_one(".a-price-whole")
            price_fraction = item.select_one(".a-price-fraction")

            if not price_whole:
                continue

            whole_str = price_whole.text.replace(",", "").strip()
            if whole_str.endswith("."):
                whole_str = whole_str.rstrip(".")

            fract_str = price_fraction.text.replace(",", "").strip() if price_fraction else "00"

            price = float(whole_str + "." + fract_str)

            products.append(Product(name, price, sku))

        except Exception:
            continue

    return products