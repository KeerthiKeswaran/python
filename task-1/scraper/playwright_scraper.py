import random
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from config.settings import USER_AGENTS, MAX_RETRIES, DELAY


def scrape_page(url):
    retries = 0

    while retries < MAX_RETRIES:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=False, 
                    args=[
                        "--disable-blink-features=AutomationControlled"
                    ]
                )
                context = browser.new_context(
                    user_agent=random.choice(USER_AGENTS),
                    viewport={"width": 1280, "height": 800},
                    locale="en-US"
                )
                page = context.new_page()
                stealth = Stealth()
                stealth.apply_stealth_sync(page) 
                print(f"[INFO] Visiting: {url}")
                page.goto(url, timeout=60000)
                page.wait_for_selector("div[data-component-type='s-search-result']", timeout=15000)
                time.sleep(random.uniform(DELAY, DELAY + 3))
                html = page.content()
                browser.close()
                return html

        except Exception as e:
            retries += 1
            wait_time = retries * 2
            print(f"[WARN] Retry {retries}/{MAX_RETRIES} — {e}")
            time.sleep(wait_time)

    print("[ERROR] Failed after retries")
    return None