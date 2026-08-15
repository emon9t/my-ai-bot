import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

# 🔑 Credentials & Tokens
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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").strip()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8692294982:AAHG-WP8tTExOehV9Zq_o16PM46lYQ0S8e8").strip()

META_API_TOKEN = os.getenv("META_API_TOKEN", "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI3Y2EyYjViYWU5MWU4YWU3MWUxMzM5YWE5ZjQxNWNkYSIsImFjY2Vzc1J1bGVzIjpbeyJpZCI6InRyYWRpbmctYWNjb3VudC1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiXSwicmVzb3VyY2VzIjpbImFjY2Vzc1J1bGVzIjpbImFjY291bnQ6JFVTRVJfSUQkOmZhZjQwZTlhLTcwN2YtNDEwMy04ZDk4LTZhMjM2YjViZTNhNyJdfSx7ImlkIjoibWV0YWFwaS1yZXN0LWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiYWNvdW50OiRVU0VSX0lEJDpmYWY0MGU5YS03MDdmLTQxMDMtOGQ5OC02YTI3NmI1YmUzYTciXX0seyJpZCI6Im1ldGFhcGktcnBjLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbImFjY291bnQ6JFVTRVJfSUQkOmZhZjQwZTlhLTcwN2YtNDEwMy04ZDk4LTZhMjM2YjViZTNhNyJdfSx7ImlkIjoibWV0YWFwaS1yZWFsLXRpbWUtc3RyZWFtaW5nLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbImFjY291bnQ6JFVTRVJfSUQkOmZhZjQwZTlhLTcwN2YtNDEwMy04ZDk4LTZhMjM2YjViZTNhNyJdfSx7ImlkIjoibWV0YXN0YXRzLWFwaSIsIm1ldGhvZHMiOlsibWV0YXN0YXRzLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIl0sInJlc291cmNlcyI6WyJhY2NvdW50OiRVU0VSX0lEJDpmYWY0MGU5YS03MDdmLTQxMDMtOGQ5OC02YTI3NmI1YmUzYTciXX0seyJpZCI6InJpc2stbWFuYWdlbWVudC1hcGkiLCJtZXRob2RzIjpbInJpc2stbWFuYWdlbWVudC1hcGkicmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciJdLCJyZXNvdXJjZXMiOlsiYWNjb3VudDokVVNFUl9JRCQ6ZmFmNDBlOWEtNzA3Zi00MTAzLThkOTgtNmEyM2I1YmUzYTciXX1dLCJpZ25vcmVSYXRlTGltaXRzIjpmYWxzZSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaW1wZXJzb25hdGVkIjpmYWxzZSwicmVhbFVzZXJJZCI6IjdjYTJiNWJhZTkxZThhZTcxZTEzMzlhYTlmNDE1Y2RhIiwiaWF0IjoxNzg2NzE5NTgyfQ.NQXV5Ib3ypxkMOtwjbiWdXFN9UX33l_BK7qGpQxYUT7vlC7V1nmv5FqFFRi26ocesWo0VR2Foqp2-422gaGfQC7s7GhBMhhjiaVvgyhY03jrB55JXZRK4bwO7vG6FJtOMTeK_cSlccBedTyvLcm4cYMY8JqbjOckmYFF54rI1F_7zDftf8udh1gTjcYbiqOwjgcNXnj_5PeuDD98F1BJWiuOQtcNmU0GMkTRQ92PAHoUyUJ_w1opG8opNhW_n23Sv9R66oMjLSreLHJH1xj77D7WqoGvC2GNxSsZm7KopvGPJ-T1MbL_vSGkYrpCGd6rnLqSSFH2UDMIsQEorWXTYpCmyNMtT3SpNg-8TxZAlgfq4LzSdaCJjZyCGWXNnPOA-xJA74uNt-aGXv8IAcCJVhUV43EvGqcShNBbW3Q8Vl5GlHUWZfbcu2tazvJz26pnMWn9PFMTTjAKIsTNznGPTYUFhAaUxNf3B3dtWLUL-HJ-LJ5TgGp-wcRRLu9Fmb2RUto0-QD3RL5GGGuQ9f5mVH3I9HHTb5UVt84PVWVc36YorrQ6dEAeKpW8XUs07ZsFCfHc8aUsIeO4vEzz93a9IDhFEeDbYCCSvC4zB-K1sj91ag4TGPTFkyqWMt05P1_l4WKzHryQ_kpiFvnEKamIzWQup9L79I9mjvzlhnH4NIo").strip()
ACCOUNT_ID = os.getenv("ACCOUNT_ID", "faf40e9a-707f-4103-8d98-6a236b5be3a7").strip()

BASE_META_URL = f"https://mt-client-api-v1.agium.metaapi.cloud/users/current/accounts/{ACCOUNT_ID}"
HEADERS = {"auth-token": META_API_TOKEN, "content-type": "application/json"}

# ⚡ Exness Execution Engine (MetaAPI)
def execute_exness_trade(action, symbol, volume=0.01):
    try:
        if action == "CLOSE":
            res = requests.post(f"{BASE_META_URL}/positions/close-all", headers=HEADERS)
            return "🔴 ALL POSITIONS CLOSED."

        action_type = "ORDER_TYPE_BUY" if action == "BUY" else "ORDER_TYPE_SELL"
        payload = {"actionType": action_type, "symbol": symbol, "volume": volume}
        res = requests.post(f"{BASE_META_URL}/trade", json=payload, headers=HEADERS)
        return f"🟢 AUTO EXECUTED: {action} on {symbol} | Lot Size: {volume}"
    except Exception as e:
        return f"Execution Error: {str(e)}"

# 🧠 Section 1: Telegram AI Agent (Steve Nison + Al Brooks Rules)
def get_live_price(symbol="BTCUSDT"):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        res = requests.get(url, timeout=5).json()
        return res.get("price", "N/A")
    except Exception:
        return "N/A"

def call_groq_ai(user_input: str, live_price: str):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    system_prompt = f"""You are the Master AI Fund Manager built on:
    1. Steve Nison Japanese Candlesticks (Engulfing, Pin Bars, Doji).
    2. Al Brooks Price Action & Rejection Scalping.
    3. SMC Order Blocks & Liquidity Sweeps.
    Real-Time Crypto Price: ${live_price}. Balance: $503.89.
    Always reply strictly in BANGLISH. Never output fake prices."""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.2
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10).json()
        return res["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI Error: {str(e)}"

def send_telegram(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=5)
    except Exception:
        pass

@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            user_msg = data["message"]["text"].strip()
            btc_price = get_live_price("BTCUSDT")
            ai_reply = call_groq_ai(user_msg, btc_price)
            send_telegram(chat_id, f"🧠 **AI Price Action Boss:**\n\n{ai_reply}")
    except Exception:
        pass
    return {"status": "ok"}

# ⚡ Section 2: TradingView All-Asset Signal Receiver
@app.post("/webhook")
async def tradingview_webhook(request: Request):
    try:
        data = await request.json()
        action = data.get("action")
        symbol = data.get("symbol", "EURUSD")
        volume = float(data.get("volume", 0.01))

        # Direct Order Execution to Exness
        result = execute_exness_trade(action, symbol, volume)
        
        # Telegram Instant Alert
        send_telegram(os.getenv("CHAT_ID", "12345678"), f"🤖 **AI Auto-Trader Event:**\n\n{result}")
        return {"status": "SUCCESS", "message": result}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

@app.get("/")
def home():
    return {"status": "Emon Autonomous AI Engine Active"}
