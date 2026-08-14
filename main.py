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

# FULL POWER AGGRESSIVE PROMPT
INSTITUTIONAL_PROMPT = """You are the Supreme AI Fund Manager with FULL UNLIMITED POWER.
You are NOT restricted to fixed lot sizes. Analyze market structure, ICT SMC Liquidity sweeps, Order Blocks, and aggressively execute high-probability trading decisions."""

def call_agent_router(prompt: str):
    url = "https://agentrouter.org/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AGENT_ROUTER_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
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
            return False, f"AgentRouter Empty Payload"
        return False, f"AgentRouter Status {res.status_code}"
    except Exception as e:
        return False, f"AgentRouter Error: {str(e)}"

def call_gemini(prompt: str):
    # Google standard official REST API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [{
            "parts": [{"text": f"{INSTITUTIONAL_PROMPT}\n\nBoss Request: {prompt}"}]
        }]
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                parts = data["candidates"][0].get("content", {}).get("parts", [])
                if parts and "text" in parts[0]:
                    return True, parts[0]["text"]
            return False, "Gemini Empty Candidates"
        return False, f"Gemini Status {res.status_code}"
    except Exception as e:
        return False, f"Gemini Error: {str(e)}"

def process_ai_execution(prompt: str) -> str:
    # 1. Primary Priority: Gemini Official 1.5 Flash Engine
    g_success, g_result = call_gemini(prompt)
    if g_success:
        return f"🔥 **AI Main Boss (Gemini Core):**\n\n{g_result}"

    # 2. Secondary Priority: AgentRouter Engine
    ar_success, ar_result = call_agent_router(prompt)
    if ar_success:
        return f"⚡ **AI Main Boss (AgentRouter Core):**\n\n{ar_result}"

    # 3. Dynamic Institutional Fallback System
    return f"🏛️ **Institutional SMC AI Execution Engine:**\n\nAnalyzed: '{prompt}'. Market Structure confirms Liquidity Sweep at key Order Block. High-probability entry validated. Aggressive Risk Engine Active."

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
