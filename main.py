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
Answer directly as an AI Fund Manager using Order Blocks, Liquidity Sweeps, FVG, and Retail Traps. Keep answers smart, professional, and helpful.
"""

def query_gemini(user_prompt):
    full_prompt = f"{INSTITUTIONAL_PROMPT}\n\nUser Question: {user_prompt}"
    data = {"contents": [{"parts": [{"text": full_prompt}]}]}
    
    # 1. Try Gemini Models
    models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_KEY}"
        try:
            res = requests.post(url, json=data, timeout=8)
            res_json = res.json()
            if "candidates" in res_json and len(res_json["candidates"]) > 0:
                parts = res_json["candidates"][0].get("content", {}).get("parts", [])
                if parts and "text" in parts[0]:
                    return parts[0]["text"]
        except Exception:
            continue

    # 2. Fallback to Agent Router (OpenRouter GPT-4o) if Gemini fails
    try:
        router_url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {AGENT_ROUTER_KEY}",
            "Content-Type": "application/json"
        }
        router_data = {
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "system", "content": INSTITUTIONAL_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        }
        res = requests.post(router_url, headers=headers, json=router_data, timeout=10)
        res_json = res.json()
        if "choices" in res_json and len(res_json["choices"]) > 0:
            return res_json["choices"][0]["message"]["content"]
    except Exception:
        pass

    return "Boss, market structure clear. AI systems active & scanning 24/7."

def send_telegram_msg(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=8)
    except Exception:
        pass

@app.on_event("startup")
def setup_telegram_webhook():
    webhook_url = f"{RENDER_URL}/telegram-webhook"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}"
    try:
        requests.get(url, timeout=5)
    except Exception:
        pass

@app.get("/")
def home():
    return {"status": "AI Boss Engine Fully Active with Multi-Agent Fallback"}

@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            user_msg = data["message"]["text"]
            
            ai_reply = query_gemini(user_msg)
            send_telegram_msg(chat_id, f"🧠 **AI Main Boss:**\n\n{ai_reply}")
    except Exception:
        pass
    return {"status": "ok"}

@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {"signal": "Manual Signal Scan"}
        
    signal_str = str(data)
    ai_analysis = query_gemini(f"Analyze signal: {signal_str}")
    
    msg = f"⚡ **Trading Signal Evaluated**\n\n**Data:** {signal_str}\n\n**AI Boss Decision:**\n{ai_analysis}\n\n**Account:** {EXNESS_LOGIN}"
    send_telegram_msg(TELEGRAM_CHAT_ID, msg)
    
    return {"status": "Success", "analysis": ai_analysis}
