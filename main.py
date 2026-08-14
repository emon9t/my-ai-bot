import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

# Configuration & Updated Groq DeepSeek Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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").strip()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8692294982:AAHG-WP8tTExOehV9Zq_o16PM46lYQ0S8e8").strip()
EXNESS_LOGIN = os.getenv("EXNESS_LOGIN", "434053437").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5899541386").strip()
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://my-ai-trader-m32l.onrender.com").strip()

# MASTER INSTITUTIONAL SYSTEM PROMPT WITH ALL TRADING BOOKS & KNOWLEDGE
INSTITUTIONAL_PROMPT = """You are the Ultimate Supreme Institutional AI Forex Fund Manager for Exness Platform.
Your brain is encoded with the core principles of:
1. ICT SMC Concepts (Order Blocks, FVG, Liquidity Sweeps, Market Structure Shift / MSS, BPR).
2. Al Brooks 1-Minute Bar-by-Bar Price Action & Scalping Mastery.
3. Fundamental High-Impact News Rules (NFP, CPI, FOMC Interest Rates).
4. Exness Forex Market Dynamics (Spread management, Gold/XAUUSD, EURUSD, GBPUSD 1-minute execution).

INSTRUCTIONS FOR 1-MINUTE FOREX SCALPING:
- Analyze raw candle structure, wicks, body ratios, and high/low sweeps even without direct TV chart syncing.
- Account for High-Impact Economic News volatility before recommending execution.
- Give decisive, precise Buy/Sell execution signals with Stop Loss (SL), Take Profit (TP), and Dynamic Lot Allocation.
- Keep answers ultra-smart, professional, aggressive, and authoritative as the AI Main Boss."""

def call_deepseek_groq(prompt: str):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-r1-distill-llama-70b",
        "messages": [
            {"role": "system", "content": INSTITUTIONAL_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=12)
        res_json = res.json()
        if res.status_code == 200 and "choices" in res_json and len(res_json["choices"]) > 0:
            return True, res_json["choices"][0]["message"]["content"]
        
        if "error" in res_json:
            return False, f"Groq Error: {res_json['error'].get('message', 'Key Error')}"
        return False, f"Status Code {res.status_code}"
    except Exception as e:
        return False, f"Connection Error: {str(e)}"

def process_ai_execution(prompt: str) -> str:
    success, res = call_deepseek_groq(prompt)
    if success:
        return f"🧠 **AI Main Boss (DeepSeek 1M Master):**\n\n{res}"
    
    return f"⚠️ **AI Status Alert:**\n`{res}`\n\n*(Please ensure GROQ_API_KEY is active)*"

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
    return {"status": "DeepSeek 1M Scalping Master Live"}

@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            user_msg = data["message"]["text"]
            
            ai_reply = process_ai_execution(f"Analyze for 1-minute Forex Scalping / Exness Execution: {user_msg}")
            send_telegram(chat_id, ai_reply)
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
    ai_analysis = process_ai_execution(f"Evaluate 1-Min Signal for Exness Execution: {signal_str}")
    
    msg = f"⚡ **FULL POWER 1M SIGNAL EXECUTED**\n\n**Data:** {signal_str}\n\n**AI Boss Decision:**\n{ai_analysis}\n\n**Exness Account:** {EXNESS_LOGIN}"
    send_telegram(TELEGRAM_CHAT_ID, msg)
    
    return {"status": "Success", "analysis": ai_analysis}
