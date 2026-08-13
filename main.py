import os
import requests
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

app = FastAPI()

# Credentials
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBUcxUHHhKvDofgbJGRBELBvGJmD4AUjYc")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8692294982:AAHG-WP8tTExOehV9Zq_o16PM46lYQ0S8e8")
AGENT_ROUTER_KEY = os.getenv("AGENT_ROUTER_KEY", "sk-ApYG7v9KnIpKytIg486ru1ph9yGnxE4JVByyL3kDgS5IQ1a8")
EXNESS_LOGIN = os.getenv("EXNESS_LOGIN", "434053437")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5899541386")

# Institutional Knowledge & Psychology Base
INSTITUTIONAL_PROMPT = """
You are an Elite Institutional AI Trading Boss trained on Al Brooks Price Action, ICT SMC Core Concepts, and Market Maker Algorithm Tracking.
Rules:
1. NEVER trade retail traps. Detect Liquidity Sweeps, Order Blocks, and Fair Value Gaps (FVG).
2. Protect capital like real money. Win-rate & risk-to-reward (minimum 1:2) is absolute priority.
3. Be professional, concise, and decisive as an AI Fund Manager.
"""

# Gemini Brain Query
def query_gemini(user_prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}"
    full_prompt = f"{INSTITUTIONAL_PROMPT}\n\nUser/Market Query: {user_prompt}"
    data = {"contents": [{"parts": [{"text": full_prompt}]}]}
    try:
        res = requests.post(url, json=data, timeout=12)
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return "Boss, system analysis error. Re-evaluating market safety protocol."

# Telegram Direct Chat Handler
async def handle_telegram_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    chat_id = str(update.effective_chat.id)
    
    # Only respond to authorized Boss
    if chat_id == TELEGRAM_CHAT_ID:
        response = query_gemini(user_msg)
        await update.message.reply_text(f"🧠 **AI Main Boss Response:**\n\n{response}")

# Telegram Bot Initializer
tg_app = Application.builder().token(TELEGRAM_TOKEN).build()
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_telegram_chat))

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(tg_app.initialize())
    asyncio.create_task(tg_app.start())
    asyncio.create_task(tg_app.updater.start_polling())

@app.get("/")
def home():
    return {"status": "Super-Intelligent 3-Boss AI Trading Engine Online 24/7"}

@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        data = await request.json()
    except:
        data = {"signal": "Market Scan Alert"}
        
    signal_str = str(data)
    ai_analysis = query_gemini(f"Analyze this signal for institutional validity: {signal_str}")
    
    # Send Report to Boss Telegram
    msg = f"⚡ **New Market Signal Evaluated**\n\n**Signal:** {signal_str}\n\n**AI Boss Decision:**\n{ai_analysis}\n\n**Exness Account:** {EXNESS_LOGIN}"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
    
    return {"status": "Evaluated", "analysis": ai_analysis}
