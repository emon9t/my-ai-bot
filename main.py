import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

# Credentials
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBUcxUHHhKvDofgbJGRBELBvGJmD4AUjYc")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8692294982:AAHG-WP8tTExOehV9Zq_o16PM46lYQ0S8e8")
AGENT_ROUTER_KEY = os.getenv("AGENT_ROUTER_KEY", "sk-ApYG7v9KnIpKytIg486ru1ph9yGnxE4JVByyL3kDgS5IQ1a8")
EXNESS_LOGIN = os.getenv("EXNESS_LOGIN", "434053437")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5899541386")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://my-ai-trader-m32l.onrender.com")

INSTITUTIONAL_PROMPT = """
You are the Elite Institutional AI Trading Boss trained on Al Brooks Price Action, ICT SMC Core Concepts, and Market Maker Systems.
Answer directly as an AI Fund Manager using Order Blocks, Liquidity Sweeps, FVG, and Retail Traps. Keep answers smart, professional, and concise.
"""

def ask_ai(prompt: str) -> str:
    # 1. Primary: Try OpenRouter Agent Router (GPT-4o-mini / GPT-4o)
    if AGENT_ROUTER_KEY:
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {AGENT_ROUTER_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": INSTITUTIONAL_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            }
            res = requests.post(url, headers=headers, json=payload, timeout=10)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
        except Exception:
            pass

    # 2. Fallback: Try Gemini Models
    models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    for model in models_to_try:
        try:
            g_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
            g_payload = {"contents": [{"parts": [{"text": f"{INSTITUTIONAL_PROMPT}\n\nUser: {prompt}"}]}]}
            res = requests.post(g_url, json=g_payload, timeout=8)
            if res.status_code == 200:
                data = res.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            continue

    return "Boss, AI core engine active and scanning market structures 24/7."

def send_telegram(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=6)
    except Exception:
        pass

@app.on_event("startup")
def startup():
    # Flush old stuck webhooks and clear pending update conflicts
    try:
        requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook?drop_pending_updates=true", timeout=5)
    except Exception:
        pass
    
    # Establish fresh clean webhook connection
    webhook_url = f"{RENDER_URL}/telegram-webhook"
    try:
        requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}", timeout=5)
    except Exception:
        pass

@app.get("/")
def home():
    return {"status": "100% Unbreakable AI Trading Engine Live"}

@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            user_msg = data["message"]["text"]
            
            ai_reply = ask_ai(user_msg)
            send_telegram(chat_id, f"🧠 **AI Main Boss:**\n\n{ai_reply}")
    except Exception:
        pass
    return {"status": "ok"}

@app.post("/webhook")
async def tradingview_webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {"signal": "Manual Signal Scan"}

    signal_str = str(data)
    ai_analysis = ask_ai(f"Analyze signal: {signal_str}")
    
    msg = f"⚡ **Trading Signal Evaluated**\n\n**Data:** {signal_str}\n\n**AI Boss Decision:**\n{ai_analysis}\n\n**Account:** {EXNESS_LOGIN}"
    send_telegram(TELEGRAM_CHAT_ID, msg)
    
    return {"status": "Success", "analysis": ai_analysis}
