import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

# Credentials
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBUcxUHHhKvDofgbJGRBELBvGJmD4AUjYc")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8692294982:AAHG-WP8tTExOehV9Zq_o16PM46lYQ0S8e8")
AGENT_ROUTER_KEY = os.getenv("AGENT_ROUTER_KEY", "sk-ApYG7v9KnIpKytIg486ru1ph9yGnxE4JVByyL3kDgS5IQ1a8")
EXNESS_LOGIN = os.getenv("EXNESS_LOGIN", "434053437")

@app.get("/")
def home():
    return {"status": "3-Boss AI Trading Engine Running Live 24/7"}

@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        data = await request.json()
    except:
        data = {"signal": "Trading Signal Triggered"}
        
    return {"status": "Signal Received", "data": data}
