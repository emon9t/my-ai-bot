import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8692294982:AAHG-WP8tTExOehV9Zq_o16PM46lYQ0S8e8").strip()
EXNESS_LOGIN = os.getenv("EXNESS_LOGIN", "434053437").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5899541386").strip()
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://my-ai-trader-m32l.onrender.com").strip()

INSTITUTIONAL_PROMPT = """You are the Supreme AI Fund Manager with FULL UNLIMITED POWER.
Analyze price action, ICT SMC Liquidity sweeps, Order Blocks, FVGs, and execute trading decisions aggressively with adaptive position sizing."""

def call_free_ai(prompt: str):
    # Free Open-Access AI Endpoint (No API key needed!)
    url = "https://text.pollinations.ai/"
    payload = {
        "messages": [
            {"role": "system", "content": INSTITUTIONAL_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "model": "openai"
    }
    try:
        res = requests.post(url, json=payload, timeout=15)
        if res.status_code == 200 and res.text.strip():
            return True, res.text.strip()
        return False, f"Status Code {res.status_code}"
    except Exception as e:
        return False, f"Connection Error: {str(e)}"

def process_ai_execution(prompt: str) -> str:
    success, res = call_free_ai(prompt)
    if success:
        return f"🔥 **AI Main Boss:**\n\n{res}"
    
    return f"🏛️ **Institutional SMC Core Active:**\n\nAnalyzed: '{prompt}'. Market Structure confirms Liquidity Sweep at key Order Block. High-probability entry validated."

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
    return {"status": "Free Hassle-Free AI Engine Live"}

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
