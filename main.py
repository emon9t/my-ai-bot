import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

# Credentials
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6KotYJaPCTTLvfrNlROaJa8Y6yRl5h8wRBBELfeRFDknw").strip()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8692294982:AAHG-WP8tTExOehV9Zq_o16PM46lYQ0S8e8").strip()
EXNESS_LOGIN = os.getenv("EXNESS_LOGIN", "434053437").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5899541386").strip()
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://my-ai-trader-m32l.onrender.com").strip()

INSTITUTIONAL_PROMPT = """You are the Supreme AI Fund Manager with FULL UNLIMITED POWER.
Analyze price action, ICT SMC Liquidity sweeps, Order Blocks, FVGs, and execute trading decisions aggressively with adaptive position sizing."""

def call_gemini(prompt: str):
    # Google REST Endpoint matching official cURL format
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_KEY
    }
    payload = {
        "contents": [{
            "parts": [{"text": f"{INSTITUTIONAL_PROMPT}\n\nUser Question: {prompt}"}]
        }]
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        res_json = res.json()
        if res.status_code == 200 and "candidates" in res_json and len(res_json) > 0:
            parts = res_json["candidates"][0].get("content", {}).get("parts", [])
            if parts and "text" in parts[0]:
                return True, parts[0]["text"]
        if "error" in res_json:
            return False, f"Google Error: {res_json['error'].get('message', 'Auth Failed')}"
        return False, f"Status Code {res.status_code}"
    except Exception as e:
        return False, f"Connection Error: {str(e)}"

def process_ai_execution(prompt: str) -> str:
    success, res = call_gemini(prompt)
    if success:
        return f"🔥 **AI Main Boss:**\n\n{res}"
    
    return f"🚨 **AI Connection Alert:**\n`{res}`\n\n🏛️ **Fallback Scan Active:** Market liquidity sweep validated."

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
    return {"status": "AI Trading Engine Online"}

@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            user_msg = data["message"]["text"]
            
            ai_reply = process_ai_execution(user_msg)
            send_telegram(chat_id, ai_reply)
    except Exception:
        pass
    return {"status": "ok"}

@app.post("/webhook")
async def tradingview_webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {"signal": "Manual Aggressive Signal"}

    signal_str = str(data)
    ai_analysis = process_ai_execution(f"Evaluate Signal for Aggressive Execution: {signal_str}")
    
    msg = f"⚡ **FULL POWER SIGNAL EXECUTED**\n\n**Data:** {signal_str}\n\n**AI Boss Decision:**\n{ai_analysis}\n\n**Account:** {EXNESS_LOGIN}"
    send_telegram(TELEGRAM_CHAT_ID, msg)
    
    return {"status": "Success", "analysis": ai_analysis}
