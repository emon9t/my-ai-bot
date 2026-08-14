import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

# Credentials
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBUcxUHHhKvDofgbJGRBELBvGJmD4AUjYc").strip()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8692294982:AAHG-WP8tTExOehV9Zq_o16PM46lYQ0S8e8").strip()
EXNESS_LOGIN = os.getenv("EXNESS_LOGIN", "434053437").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5899541386").strip()
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://my-ai-trader-m32l.onrender.com").strip()

INSTITUTIONAL_PROMPT = """You are the Supreme AI Trading Boss trained on Al Brooks Price Action, ICT SMC Core Concepts, and Market Maker Systems.
You have FULL POWER over market analysis and position evaluation. Answer directly, aggressively, and smartly as an Elite Fund Manager in helpful tone."""

def get_real_ai_response(user_text: str) -> str:
    # Direct Google AI REST Endpoint for Gemini
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [{
            "parts": [{"text": f"{INSTITUTIONAL_PROMPT}\n\nUser Message: {user_text}"}]
        }]
    }
    
    try:
        res = requests.post(url, json=payload, timeout=12)
        res_json = res.json()
        
        # Extract Output Text
        if res.status_code == 200 and "candidates" in res_json and len(res_json["candidates"]) > 0:
            parts = res_json["candidates"][0]["content"]["parts"]
            if parts and "text" in parts[0]:
                return res_json["candidates"][0]["content"]["parts"][0]["text"]
        
        # Return Error Message directly to Telegram if API Key issue
        if "error" in res_json:
            return f"⚠️ **Google AI Key Alert:** {res_json['error'].get('message', 'Key issue')}"
            
    except Exception as e:
        return f"⚠️ **Connection Error:** {str(e)}"

    return "🏛️ **AI Core Scanning:** System active and observing SMC Liquidity Blocks."

def send_telegram(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=6)
    except Exception:
        pass

@app.on_event("startup")
def startup():
    try:
        requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook?drop_pending_updates=true", timeout=5)
    except Exception:
        pass
    
    webhook_url = f"{RENDER_URL}/telegram-webhook"
    try:
        requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}", timeout=5)
    except Exception:
        pass

@app.get("/")
def home():
    return {"status": "AI Trading Engine Live"}

@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            user_msg = data["message"]["text"]
            
            ai_reply = get_real_ai_response(user_msg)
            send_telegram(chat_id, f"🧠 **AI Main Boss:**\n\n{ai_reply}")
    except Exception:
        pass
    return {"status": "ok"}

@app.post("/webhook")
async def tradingview_webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {"signal": "Manual Signal"}

    signal_str = str(data)
    ai_analysis = get_real_ai_response(f"Analyze signal for execution: {signal_str}")
    
    msg = f"⚡ **FULL POWER SIGNAL EXECUTED**\n\n**Data:** {signal_str}\n\n**AI Boss Decision:**\n{ai_analysis}\n\n**Account:** {EXNESS_LOGIN}"
    send_telegram(TELEGRAM_CHAT_ID, msg)
    
    return {"status": "Success", "analysis": ai_analysis}
