import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

# --- New Updated API Keys ---
GEMINI_KEY_1 = os.getenv("GEMINI_API_KEY_1", "AQ.Ab8RN6JQ-cqDBZexfvVxwKDEHWfGIbBaPpVvFeDKVRw2YbudhA").strip()
GEMINI_KEY_2 = os.getenv("GEMINI_API_KEY_2", "AQ.Ab8RN6Jf7B1MTdp6h0meM9r5L4d4gfszTqgQ_FNGgAK-lt12Hw").strip()
AGENT_ROUTER_KEY = os.getenv("AGENT_ROUTER_KEY", "sk-D44ijjuT36V8EbE3lzE7wPH9RypXzk0FPnRtd9zcNQ3v9RuW").strip()

# Credentials
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8692294982:AAHG-WP8tTExOehV9Zq_o16PM46lYQ0S8e8").strip()
EXNESS_LOGIN = os.getenv("EXNESS_LOGIN", "434053437").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5899541386").strip()
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://my-ai-trader-m32l.onrender.com").strip()

# FULL POWER AGGRESSIVE PROMPT
INSTITUTIONAL_PROMPT = """You are the Supreme AI Fund Manager with FULL UNLIMITED POWER.
You are NOT restricted to fixed lot sizes or conservative limits.
Analyze price action, ICT SMC Liquidity sweeps, Order Blocks, FVGs, and dynamically scale trade sizing for high-probability execution."""

def call_gemini(api_key: str, prompt: str):
    # Standard REST Endpoint for Gemini
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [{"text": f"{INSTITUTIONAL_PROMPT}\n\nUser Question: {prompt}"}]
        }]
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        res_json = res.json()
        if res.status_code == 200 and "candidates" in res_json and len(res_json["candidates"]) > 0:
            parts = res_json["candidates"][0].get("content", {}).get("parts", [])
            if parts and "text" in parts[0]:
                return True, parts[0]["text"]
        return False, f"Gemini Status {res.status_code}: {res.text}"
    except Exception as e:
        return False, f"Gemini Error: {str(e)}"

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
        return False, f"AgentRouter Status {res.status_code}: {res.text}"
    except Exception as e:
        return False, f"AgentRouter Error: {str(e)}"

def process_ai_execution(prompt: str) -> str:
    # 1. Try Gemini API Key 1
    g1_success, g1_res = call_gemini(GEMINI_KEY_1, prompt)
    if g1_success:
        return f"🔥 **AI Boss (Gemini Key 1):**\n\n{g1_res}"

    # 2. Try Gemini API Key 2
    g2_success, g2_res = call_gemini(GEMINI_KEY_2, prompt)
    if g2_success:
        return f"🔥 **AI Boss (Gemini Key 2):**\n\n{g2_res}"

    # 3. Try AgentRouter Engine
    ar_success, ar_res = call_agent_router(prompt)
    if ar_success:
        return f"⚡ **AI Boss (AgentRouter Engine):**\n\n{ar_res}"

    # 4. Detailed Diagnostic Error Output
    return f"🚨 **ALL AI ENGINES REPORTED DIAGNOSTICS:**\n\n1️⃣ **Gemini Key 1:** `{g1_res[:150]}`\n\n2️⃣ **Gemini Key 2:** `{g2_res[:150]}`\n\n3️⃣ **AgentRouter:** `{ar_res[:150]}`"

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
    return {"status": "Full Power Multi-API AI Engine Live"}

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
