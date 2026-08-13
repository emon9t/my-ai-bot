import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

# Credentials
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBUcxUHHhKvDofgbJGRBELBvGJmD4AUjYc").strip()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8692294982:AAHG-WP8tTExOehV9Zq_o16PM46lYQ0S8e8").strip()
AGENT_ROUTER_KEY = os.getenv("AGENT_ROUTER_KEY", "sk-ApYG7v9KnIpKytIg486ru1ph9yGnxE4JVByyL3kDgS5IQ1a8").strip()
EXNESS_LOGIN = os.getenv("EXNESS_LOGIN", "434053437").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5899541386").strip()
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://my-ai-trader-m32l.onrender.com").strip()

INSTITUTIONAL_PROMPT = """You are the Elite Institutional AI Trading Boss trained on Al Brooks Price Action, ICT SMC Core Concepts, and Market Maker Systems.
Answer directly as an AI Fund Manager using Order Blocks, Liquidity Sweeps, FVG, and Retail Traps. Keep answers smart, professional, and concise."""

def query_openrouter(prompt: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AGENT_ROUTER_KEY}",
        "HTTP-Referer": RENDER_URL,
        "X-Title": "AI Trading Engine",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": INSTITUTIONAL_PROMPT},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=12)
        res_data = res.json()
        
        if res.status_code == 200 and "choices" in res_data and len(res_data["choices"]) > 0:
            return res_data["choices"][0]["message"]["content"]
        else:
            err_msg = res_data.get("error", {}).get("message", str(res_data))
            return f"ERR_OR [{res.status_code}]: {err_msg}"
    except Exception as e:
        return f"ERR_OR_CONN: {str(e)}"

def query_gemini(prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": f"{INSTITUTIONAL_PROMPT}\n\nUser Question: {prompt}"}]}]}
    try:
        res = requests.post(url, json=payload, timeout=10)
        res_data = res.json()
        if res.status_code == 200 and "candidates" in res_data and len(res_data["candidates"]) > 0:
            return res_data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            err_msg = res_data.get("error", {}).get("message", "Gemini Failed")
            return f"ERR_GEMINI: {err_msg}"
    except Exception as e:
        return f"ERR_GEMINI_CONN: {str(e)}"

def ask_ai_boss(prompt: str) -> str:
    # 1. Primary Priority: OpenRouter (Agent Router Paid API)
    or_response = query_openrouter(prompt)
    if not or_response.startswith("ERR_OR"):
        return or_response
        
    # 2. Backup Priority: Gemini API
    gemini_response = query_gemini(prompt)
    if not gemini_response.startswith("ERR_GEMINI"):
        return f"**(Fallback Gemini Active)**\n\n{gemini_response}"
        
    # 3. Diagnostic Report if both fail
    return f"⚠️ **API Diagnostic Alert:**\n\n• **OpenRouter Status:** {or_response}\n• **Gemini Status:** {gemini_response}"

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
    return {"status": "AI Boss OpenRouter Engine Online 24/7"}

@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            user_msg = data["message"]["text"]
            
            ai_reply = ask_ai_boss(user_msg)
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
    ai_analysis = ask_ai_boss(f"Analyze signal: {signal_str}")
    
    msg = f"⚡ **Trading Signal Evaluated**\n\n**Data:** {signal_str}\n\n**AI Boss Decision:**\n{ai_analysis}\n\n**Account:** {EXNESS_LOGIN}"
    send_telegram(TELEGRAM_CHAT_ID, msg)
    
    return {"status": "Success", "analysis": ai_analysis}
