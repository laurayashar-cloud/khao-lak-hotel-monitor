import json
from playwright.sync_api import sync_playwright
import requests

CHECKIN = "2026-04-01"
CHECKOUT = "2026-04-08"

HOTELS = [
    "Moracea by Khao Lak Resort",
    "La Flora Khao Lak",
    "Ramada Resort by Wyndham Khao Lak",
    "Seaview Resort Khao Lak",
    "The Sands Khao Lak by Katathani",
    "Khao Lak Bhandari Resort & Spa"
]

STATE_FILE = "hotel_state.json"

SEARCH_URL = f"https://www.expedia.com/Hotel-Search?destination=Khao%20Lak&startDate={CHECKIN}&endDate={CHECKOUT}&rooms=1&adults=2&children=1&childrenAges=3"

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def send_alert(message):
    webhook = os.environ["SLACK_WEBHOOK_URL"]
    requests.post(webhook, json={"text": message})

def check():
    send_alert("Test message from hotel monitor")
    state = load_state()
    new_state = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.goto(SEARCH_URL, timeout=60000)
        page.wait_for_timeout(8000)

        page_text = page.content().lower()

        for hotel in HOTELS:
            available = hotel.lower() in page_text

            new_state[hotel] = available

            if state.get(hotel) == False and available == True:
                send_alert(f"Availability found for {hotel}!")

        browser.close()

    save_state(new_state)

if __name__ == "__main__":
    check()
