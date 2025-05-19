from playwright.sync_api import sync_playwright
import os

from dotenv import load_dotenv
load_dotenv()

LOGIN_URL = os.getenv("LOGIN_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
POST_LOGIN_URL = os.getenv("POST_LOGIN_URL")
STORAGE_STATE_PATH = "auth_storage.json"

# Login selectors
USERNAME_SELECTOR = os.getenv("USERNAME_SELECTOR", "input[name='email']")
PASSWORD_SELECTOR = os.getenv("PASSWORD_SELECTOR", "input[name='password']")
SUBMIT_SELECTOR = os.getenv("SUBMIT_SELECTOR", "input[type='submit']")


def save_auth():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Force visible for login debugging
        context = browser.new_context()
        page = context.new_page()

        print("Logging in...")
        page.goto(LOGIN_URL)
        page.fill(USERNAME_SELECTOR, USERNAME)
        page.fill(PASSWORD_SELECTOR, PASSWORD)
        page.click(SUBMIT_SELECTOR)

        page.wait_for_url(POST_LOGIN_URL + "*", timeout=10000)
        context.storage_state(path=STORAGE_STATE_PATH)
        print(f"✅ Auth session saved to: {STORAGE_STATE_PATH}")
        browser.close()


if __name__ == "__main__":
    save_auth()
