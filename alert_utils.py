# backend/alert_utils.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Example: Twilio or WhatsApp Cloud API wrapper
WHATSAPP_TO = os.getenv("WHATSAPP_TO_NUMBER")  # +91...
WHATSAPP_FROM = os.getenv("WHATSAPP_FROM_NUMBER")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_API_TOKEN")
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL")  # optional

def send_whatsapp_alert(message: str):
    """
    Sends an alert via WhatsApp/Facebook Cloud API / Twilio
    You must configure env vars according to the provider.
    For hackathon, you can also just print and/or log to a webhook.
    """
    print("[ALERT]", message)
    # If using Twilio:
    # from twilio.rest import Client
    # client = Client(account_sid, auth_token)
    # client.messages.create(body=message, from_=WHATSAPP_FROM, to=WHATSAPP_TO)
    # OR using WhatsApp Cloud API:
    if WHATSAPP_API_URL and WHATSAPP_TOKEN:
        payload = {
            "messaging_product": "whatsapp",
            "to": WHATSAPP_TO,
            "type": "text",
            "text": {"body": message}
        }
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
        r = requests.post(WHATSAPP_API_URL, json=payload, headers=headers, timeout=5)
        if r.status_code >= 400:
            print("WhatsApp send failed:", r.text)
