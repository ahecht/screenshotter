import argparse
import os
import re
import csv
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Load config from .env
load_dotenv()

LOGIN_URL = os.getenv("LOGIN_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
POST_LOGIN_URL = os.getenv("POST_LOGIN_URL")
URLS_FILE = "urls.txt"
BASE_OUTPUT_DIR = "runs"

ENV_HEADLESS = os.getenv("HEADLESS", "True").lower() in ("1", "true", "yes")


def slugify_url(url):
    # Drop protocol and www
    url = re.sub(r'^https?://(www\.)?', '', url)
    return re.sub(r'\W+', '_', url.strip('/')).strip('_')


def read_urls(file_path, limit=None):
    with open(file_path, "r") as f:
        urls = [line.strip() for line in f if line.strip()]
    return urls[:limit] if limit else urls


def create_run_output_dir():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = os.path.join(BASE_OUTPUT_DIR, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir, os.path.join(output_dir, f"log_{timestamp}.csv")


def write_log_entry(log_writer, url, status, detail):
    log_writer.writerow({
        "url": url,
        "status": status,
        "detail": detail
    })


def run(limit=None, headless=ENV_HEADLESS):
    urls = read_urls(URLS_FILE, limit=limit)
    output_dir, log_path = create_run_output_dir()

    with open(log_path, mode="w", newline="") as log_file:
        fieldnames = ["url", "status", "detail"]
        log_writer = csv.DictWriter(log_file, fieldnames=fieldnames)
        log_writer.writeheader()

        with sync_playwright() as p:
            print(f"Launching browser (headless={headless})...")
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(storage_state="auth_storage.json")
            page = context.new_page()

            print("✅ Using stored session, ready to capture pages.")

            # STEP 2: Visit and capture each URL
            for url in urls:
                print(f"Visiting: {url}")
                try:
                    page.goto(url, wait_until="networkidle", timeout=15000)
                    # Detect redirect to login page
                    if "signin" in page.url.lower():
                        raise Exception("Redirected to login – stored session likely expired.")
                    filename_base = slugify_url(url)
                    screenshot_file = os.path.join(output_dir, filename_base + ".png")
                    page.screenshot(path=screenshot_file, full_page=True)
                    print(f"Saved screenshot: {screenshot_file}")
                    write_log_entry(log_writer, url, "success", screenshot_file)
                except Exception as e:
                    print(f"Failed to process {url}: {e}")
                    write_log_entry(log_writer, url, "fail", str(e))

            browser.close()

    print(f"\n📁 Run output saved to: {output_dir}")
    print(f"📄 Log file: {log_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture full-page screenshots from a list of URLs")
    parser.add_argument('--limit', type=int, help="Limit the number of URLs to process")
    parser.add_argument('--headless', type=str, choices=['true', 'false'], help="Override headless mode (true/false)")
    args = parser.parse_args()

    headless_flag = ENV_HEADLESS if args.headless is None else args.headless.lower() == "true"

    run(limit=args.limit, headless=headless_flag)
