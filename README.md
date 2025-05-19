# Screenshotter

A Python tool for capturing full-page screenshots from a list of URLs using Playwright. Supports session persistence for capturing URLs that require authentication.

## Features

- Captures full-page screenshots of multiple URLs
- Supports authenticated sessions
- Generates organized output with timestamps
- Creates detailed logs of the screenshot process
- Configurable headless mode
- URL limit option for testing

## Prerequisites

- Python 3.13 or higher
- Playwright browser dependencies

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd screenshotter
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. Install dependencies (choose one method):

Using pip:
```bash
pip install -e .
```

Or using uv (faster):
```bash
uv sync
```

4. Install Playwright browsers:
```bash
playwright install
```

## Configuration

For non-authenticated use, you don't need any variables.
You can set `HEADLESS` in a `.env` file if you like, or you can pass it as a parameter.

```env
HEADLESS=True  # or False for visible browser
```

### Authentication Setup

If you need to access authenticated pages, you'll need to set up your authentication session first:

1. Configure your login details in the `.env` file:
```env
LOGIN_URL=<your-login-url>
USERNAME=<your-username>
PASSWORD=<your-password>
POST_LOGIN_URL=<url-to-visit-after-login>
USERNAME_SELECTOR=<selector-for-username-field>  # Optional, defaults to "input[name='email']"
PASSWORD_SELECTOR=<selector-for-password-field>  # Optional, defaults to "input[name='password']"
SUBMIT_SELECTOR=<selector-for-submit-button>     # Optional, defaults to "input[type='submit']"
```

2. Run the authentication script to save your session:
```bash
python save_auth_session.py
```

This will:
- Open a visible browser window
- Log in using your credentials
- Save the authenticated session to `auth_storage.json`
- The main script will automatically use this saved session for subsequent runs

Note: If your session expires, you'll need to run `save_auth_session.py` again to create a new session.

## Usage

1. Prepare your URLs:
   - Add the URLs you want to screenshot to `urls.txt`, one per line

2. Run the script:
```bash
python screenshotter.py
```

### Command Line Options

- `--limit N`: Process only the first N URLs
- `--headless true|false`: Override headless mode
- `--urlfile PATH`: Specify a custom URL file path (default: urls.txt)

## Output

The script creates a new directory under `runs/` with the following structure:
```
runs/
└── YYYY-MM-DD_HHMMSS/
    ├── log_YYYY-MM-DD_HHMMSS.csv
    └── screenshots/
        ├── url1.png
        ├── url2.png
        └── ...
```

The log file contains:
- URL
- Status (success/fail)
- Details (screenshot path or error message)
