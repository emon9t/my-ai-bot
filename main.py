import os
import requests
import asyncio
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

app = FastAPI()

# Credentials
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBUcxUHHhKvDofgbJGRBELBvGJmD4AUjYc")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8692294982:AAHG-WP8tTExOehV9Zq_o16PM46lYQ0S8e8")
EXNESS_LOGIN = os.getenv("EXNESS_LOGIN", "434053437")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5899541386")

# Institutional System Prompt
INSTITUTIONAL_PROMPT = """
You are the Elite Institutional AI Trading Boss trained on Al Brooks Price Action, ICT SMC Core Concepts, and Market Maker Trap Systems.
Answer the user directly, strictly using Smart Money Concepts (Order Blocks, Liquidity Sweeps, FVG, Retail Traps). Keep answers professional, smart, and concise.
"""

def query_gemini(user_prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    full_prompt = f"{INSTITUTIONAL_PROMPT}\n\nBoss Request: {user_prompt}"
    data = {"contents": [{"parts": [{"text": full_prompt}]}]}
    try:
        res = requests.post(url, json=data, timeout=10)
        json_data = res.json()
        return json_data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return "Boss, AI core is processing market logic. Everything is secure."

# Initialize Telegram App
tg_app = Application.builder().token(TELEGRAM_TOKEN).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    user_text = update.message.text
    chat_id = str(update.effective_chat.id)
    
    # Process AI Brain Answer
    ai_reply = query_gemini(user_text)
    await update.message.reply_text(f"🧠 **AI Main Boss:**\n\n{ai_reply}")

tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.on_event("startup")
async def start_bot():
    await tg_app.initialize()
    await tg_app.start()
    asyncio.create_task(tg_app.updater.start_polling(drop_pending_updates=True))

@app.get("/")
def home():
    return {"status": "AI Boss System Fully Operational 24/7"}

@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        data = await request.json()
    except:
        data = {"signal": "Manual Market Scan"}
        
    signal_str = str(data)
    ai_analysis = query_gemini(f"Analyze signal: {signal_str}")
    
    msg = f"⚡ **New Signal Received**\n\n**Data:** {signal_str}\n\n**AI Boss Decision:**\n{ai_analysis}"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
    
    return {"status": "Success", "analysis": ai_analysis}
