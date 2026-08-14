import os
import json
import requests
from fastapi import FastAPI, Request

app = FastAPI()

# Credentials
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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").strip()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8692294982:AAHG-WP8tTExOehV9Zq_o16PM46lYQ0S8e8").strip()
EXNESS_LOGIN = os.getenv("EXNESS_LOGIN", "434053437").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5899541386").strip()
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://my-ai-trader-m32l.onrender.com").strip()

MEMORY_FILE = "/tmp/ai_memory.json"

# Default Base Prompt
DEFAULT_PROMPT = """You are the Supreme AI Fund Manager for Exness.
Your brain handles ICT SMC, 1-Min Scalping, Balance Risk Management, and News Sentiment.

LANGUAGE & FORMAT:
- Always reply in BANGLISH (Bengali written in English script).
- Always calculate Lot Size according to Account Balance & Equity.
- Give exact Entry, Stop Loss (SL), Take Profit (TP), and Risk Percentage."""

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f).get("prompt", DEFAULT_PROMPT)
        except Exception:
            pass
    return DEFAULT_PROMPT

def save_memory(new_prompt):
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump({"prompt": new_prompt}, f)
        return True
    except Exception:
        return False

def call_deepseek_groq(user_input: str):
    active_prompt = load_memory()
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": active_prompt},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.4
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
        return f"🧠 **AI Main Boss:**\n\n{res}"
    return f"⚠️ **AI Status Alert:**\n`{res}`"

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
    return {"status": "AI Dynamic Memory Scalper Live"}

@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            user_msg = data["message"]["text"].strip()
            
            # Feature 1: Update Prompt directly from Telegram
            if user_msg.startswith("/setprompt"):
                new_instruction = user_msg.replace("/setprompt", "").strip()
                if new_instruction:
                    updated_prompt = f"{DEFAULT_PROMPT}\n\nUSER CUSTOM RULES:\n{new_instruction}"
                    save_memory(updated_prompt)
                    send_telegram(chat_id, "✅ **AI Memory Updated Successfully!**\nEkhon theke AI apnar ei notun nion ane trade korbe.")
                else:
                    send_telegram(chat_id, "⚠️ **Usage:** `/setprompt apnar instruction likhun`")
                return {"status": "ok"}
            
            # Feature 2: View current prompt from Telegram
            if user_msg == "/viewprompt":
                current_p = load_memory()
                send_telegram(chat_id, f"📝 **Current Active Memory:**\n\n`{current_p}`")
                return {"status": "ok"}
            
            # General AI Execution
            ai_reply = process_ai_execution(f"1-Minute Exness Analysis Request: {user_msg}")
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
    ai_analysis = process_ai_execution(f"Evaluate Signal with Wallet Risk Control: {signal_str}")
    
    msg = f"⚡ **FULL POWER SIGNAL EXECUTED**\n\n**Data:** {signal_str}\n\n**AI Boss Decision:**\n{ai_analysis}\n\n**Exness Account:** {EXNESS_LOGIN}"
    send_telegram(TELEGRAM_CHAT_ID, msg)
    
    return {"status": "Success", "analysis": ai_analysis}
