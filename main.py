import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

# Environment Credentials
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBUcxUHHhKvDofgbJGRBELBvGJmD4AUjYc").strip()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8692294982:AAHG-WP8tTExOehV9Zq_o16PM46lYQ0S8e8").strip()
AGENT_ROUTER_KEY = os.getenv("AGENT_ROUTER_KEY", "sk-ApYG7v9KnIpKytIg486ru1ph9yGnxE4JVByyL3kDgS5IQ1a8").strip()
EXNESS_LOGIN = os.getenv("EXNESS_LOGIN", "434053437").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5899541386").strip()
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://my-ai-trader-m32l.onrender.com").strip()

# FULL POWER SYSTEM PROMPT
INSTITUTIONAL_PROMPT = """You are the Supreme AI Fund Manager with FULL CONTROL.
You are NOT restricted to fixed 0.01 lot sizes. You analyze market structure, liquidity sweeps, order blocks, and scale position sizes (dynamic aggressive sizing) for maximum profitability.
Be decisive, aggressive yet institutional, and authoritative as the Main Boss."""

def call_agent_router(prompt: str):
    url = "https://agentrouter.org/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AGENT_ROUTER_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": INSTITUTIONAL_PROMPT},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if "choices" in data and len(data["choices"]) > 0:
                return True, data["choices"][0]["message"]["content"]
            return False, f"AgentRouter 200 OK but empty payload: {res.text}"
        return False, f"AgentRouter HTTP {res.status_code}: {res.text}"
    except Exception as e:
        return False, f"AgentRouter Connection Error: {str(e)}"

def call_gemini(prompt: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": f"{INSTITUTIONAL_PROMPT}\n\nUser: {prompt}"}]}]}
    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                return True, data["candidates"][0]["content"]["parts"][0]["text"]
            return False, f"Gemini 200 OK but empty candidates: {res.text}"
        return False, f"Gemini HTTP {res.status_code}: {res.text}"
    except Exception as e:
        return False, f"Gemini Connection Error: {str(e)}"

def process_ai_execution(prompt: str) -> str:
    # 1. Try AgentRouter (Official)
    ar_success, ar_result = call_agent_router(prompt)
    if ar_success:
        return f"🔥 **AI Boss (AgentRouter Engine):**\n\n{ar_result}"
        
    # 2. Try Gemini Backup
    g_success, g_result = call_gemini(prompt)
    if g_success:
        return f"⚡ **AI Boss (Gemini Engine):**\n\n{g_result}"
        
    # 3. Direct Diagnostics Sent to Telegram if Both Fail
    return f"🚨 **AI CONNECTIVITY ERROR DIAGNOSTICS** 🚨\n\n1️⃣ **AgentRouter Failure:**\n`{ar_result}`\n\n2️⃣ **Gemini Failure:**\n`{g_result}`\n\n💡 *Action Needed:* Check key validity or account balance for AgentRouter/Gemini."

def send_telegram(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=6)
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
    return {"status": "Full Power AI Engine Online"}

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
    ai_analysis = process_ai_execution(f"Evaluate Signal for Immediate Aggressive Execution: {signal_str}")
    
    msg = f"⚡ **FULL POWER SIGNAL EXECUTED**\n\n**Data:** {signal_str}\n\n**AI Boss Decision:**\n{ai_analysis}\n\n**Account:** {EXNESS_LOGIN}"
    send_telegram(TELEGRAM_CHAT_ID, msg)
    
    return {"status": "Success", "analysis": ai_analysis}
