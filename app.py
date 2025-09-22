from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import json
import logging
import openai

# Flask App
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Load menu from JSON
with open("menu.json", "r", encoding="utf-8") as f:
    MENU = json.load(f)

# OpenAI API Key (replace with your own key)
openai.api_key = "YOUR_OPENAI_API_KEY"

# Twilio credentials (replace with your own)
TWILIO_ACCOUNT_SID = "YOUR_TWILIO_SID"
TWILIO_AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"   # Twilio sandbox WhatsApp number

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def get_ai_response(query: str) -> str:
    """Generate AI-based FAQ response using GPT."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "You are a helpful assistant for Technik Nest, a software development company. Keep answers short, friendly, and professional."},
                {"role": "user", "content": query}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        logging.error(f"AI error: {e}")
        return "⚠️ Sorry, I couldn’t process that right now. Please try again later."

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """Handle incoming WhatsApp messages with menu + AI fallback."""
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "unknown")
    logging.info(f"Incoming WhatsApp message from {sender}: {incoming_msg}")

    resp = MessagingResponse()
    msg = resp.message()

    try:
        if incoming_msg == "1":
            msg.body(MENU["services"])
        elif incoming_msg == "2":
            msg.body(MENU["about_us"])
        elif incoming_msg == "3":
            msg.body(MENU["portfolio"])
        elif incoming_msg == "0":
            msg.body(MENU["main_menu"])
        else:
            # AI fallback for free-text queries
            msg.body(get_ai_response(incoming_msg))
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        msg.body("⚠️ Something went wrong. Please try again later.")

    return str(resp)


if __name__ == "__main__":
    logging.info("🚀 Starting Technik Nest WhatsApp Bot with AI + Dynamic Menu...")
    app.run(host="0.0.0.0", port=5000, debug=True)


