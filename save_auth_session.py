from playwright.sync_api import sync_playwright
import os
import argparse

from dotenv import load_dotenv
load_dotenv()

# Non-sensitive defaults can still use env vars
LOGIN_URL = os.getenv("LOGIN_URL")
POST_LOGIN_URL = os.getenv("POST_LOGIN_URL")
STORAGE_STATE_PATH = "auth_storage.json"

# Login selectors with defaults
USERNAME_SELECTOR = os.getenv("USERNAME_SELECTOR", "input[name='email']")
PASSWORD_SELECTOR = os.getenv("PASSWORD_SELECTOR", "input[name='password']")
SUBMIT_SELECTOR = os.getenv("SUBMIT_SELECTOR", "input[type='submit']")

ENV_HEADLESS = os.getenv("HEADLESS", "True").lower() in ("1", "true", "yes")


def save_auth(username, password, headless=ENV_HEADLESS):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        print("Logging in...")
        page.goto(LOGIN_URL)
        page.fill(USERNAME_SELECTOR, username)
        page.fill(PASSWORD_SELECTOR, password)
        page.click(SUBMIT_SELECTOR)

        page.wait_for_url(POST_LOGIN_URL + "*", timeout=10000)
        context.storage_state(path=STORAGE_STATE_PATH)
        print(f"✅ Auth session saved to: {STORAGE_STATE_PATH}")
        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Save authentication session for a website')
    parser.add_argument('--username', help='Username/email for login (overrides USERNAME env var)')
    parser.add_argument('--password', help='Password for login (overrides PASSWORD env var)')
    parser.add_argument('--headless', type=str, choices=['true', 'false'], help="Override headless mode (true/false)")

    args = parser.parse_args()

    headless_flag = ENV_HEADLESS if args.headless is None else args.headless.lower() == "true"

    # Get credentials from args or environment variables
    username = args.username or os.getenv("USERNAME")
    password = args.password or os.getenv("PASSWORD")

    if not username or not password:
        parser.error("Username and password must be provided either via command line arguments or environment variables")

    save_auth(username, password, headless=headless_flag)
