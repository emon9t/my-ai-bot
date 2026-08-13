import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

# Credentials
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBUcxUHHhKvDofgbJGRBELBvGJmD4AUjYc")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8692294982:AAHG-WP8tTExOehV9Zq_o16PM46lYQ0S8e8")
EXNESS_LOGIN = os.getenv("EXNESS_LOGIN", "434053437")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5899541386")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://my-ai-trader-m32l.onrender.com")

INSTITUTIONAL_PROMPT = """
You are the Elite Institutional AI Trading Boss trained on Al Brooks Price Action, ICT SMC Core Concepts, and Market Maker Systems.
Answer directly as an AI Fund Manager using Order Blocks, Liquidity Sweeps, FVG, and Retail Traps. Keep answers smart, professional, and helpful.
"""

def query_gemini(user_prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    full_prompt = f"{INSTITUTIONAL_PROMPT}\n\nUser Question: {user_prompt}"
    data = {
        "contents": [{"parts": [{"text": full_prompt}]}]
    }
    
    try:
        res = requests.post(url, json=data, timeout=15)
        res_json = res.json()
        
        # Extract Text Safely
        if "candidates" in res_json and len(res_json["candidates"]) > 0:
            candidate = res_json["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                return candidate["content"]["parts"][0]["text"]
                
        if "error" in res_json:
            return f"⚠️ Gemini API Error: {res_json['error'].get('message', 'API Quota/Key issue')}"
            
        return "Boss, market structure clear. Waiting for high probability setup."
    except Exception as e:
        return f"⚠️ Connection Error: {str(e)}"

def send_telegram_msg(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=8)
    except:
        pass

@app.on_event("startup")
def setup_telegram_webhook():
    webhook_url = f"{RENDER_URL}/telegram-webhook"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}"
    try:
        requests.get(url, timeout=5)
    except:
        pass

@app.get("/")
def home():
    return {"status": "AI Boss Engine Fully Active"}

@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            user_msg = data["message"]["text"]
            
            ai_reply = query_gemini(user_msg)
            send_telegram_msg(chat_id, f"🧠 **AI Main Boss:**\n\n{ai_reply}")
    except Exception as e:
        pass
    return {"status": "ok"}

@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        data = await request.json()
    except:
        data = {"signal": "Manual Signal"}
        
    signal_str = str(data)
    ai_analysis = query_gemini(f"Analyze signal: {signal_str}")
    
    msg = f"⚡ **Trading Signal Evaluated**\n\n**Data:** {signal_str}\n\n**AI Boss Decision:**\n{ai_analysis}\n\n**Account:** {EXNESS_LOGIN}"
    send_telegram_msg(TELEGRAM_CHAT_ID, msg)
    
    return {"status": "Success", "analysis": ai_analysis}
