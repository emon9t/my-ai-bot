import os
import base64
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# -------------------------------------------------------------
# ১. আপনার বট ও এপিআই ক্রেডেনশিয়ালস (সরাসরি যুক্ত করা হয়েছে)
# -------------------------------------------------------------
TELEGRAM_BOT_TOKEN = "8692294982:AAHG-WP8tTExOehV9Zq_o16PM46lYQ0S8e8"
AGENTROUTER_KEY = "sk-DYmGoreRhkZPpUknFlhNXUVDINRKwvMNY8aAM6lbSXy4nn5H"

# Agent Router API ক্লায়েন্ট সেটআপ
client = OpenAI(
    api_key=AGENTROUTER_KEY,
    base_url="https://agentrouter.org/v1"
)

# এআই অ্যাসিস্ট্যান্টের ক্যান্ডেলস্টিক ও ট্রেডিং রুলস প্রম্পট
SYSTEM_PROMPT = """
আপনি একজন অত্যন্ত দক্ষ ও অভিজ্ঞ টেকনিক্যাল এনালাইসিস এবং ক্রিপ্টো ট্রেডিং এআই অ্যাসিস্ট্যান্ট।

আপনার মূল কাজ ও নিয়মাবলী:
১. টেলিগ্রাম ব্যবহারকারীর সাথে সবসময় সাবলীল ও বন্ধুভাবাপন্ন বাংলায় কথা বলবেন।
২. চার্টের ছবি (Screenshot) পেলে ক্যান্ডেলস্টিক বইয়ের নিয়ম মেনে হাই-কোয়ালিটি অ্যানালাইসিস করবেন।
৩. ছবি থেকে Hammer, Bullish/Bearish Engulfing, Doji, Morning Star, Shooting Star ইত্যাদি ক্যান্ডেলস্টিক প্যাটার্ন সনাক্ত করবেন।
৪. সাপোর্ট-রেজিস্ট্যান্স এবং মার্কেট ট্রেন্ড বিশ্লেষণ করে পরের ক্যান্ডেল Bullish নাকি Bearish হওয়ার সম্ভাবনা বেশি, তা গাণিতিক ও টেকনিক্যাল যুক্তি দিয়ে বুঝিয়ে দেবেন।
৫. ব্যবহারকারী যেকোনো প্রশ্ন করলে প্রফেশনাল ও সহজ ভাষায় উত্তর দেবেন।
"""

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# -------------------------------------------------------------
# ২. টেলিগ্রাম বট হ্যান্ডলারসমূহ
# -------------------------------------------------------------

# /start কমান্ড
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "হ্যালো এমোন ভাই! 👋\n\n"
        "আমি আপনার ২৪/৭ টেলিগ্রাম এআই ট্রেডিং অ্যাসিস্ট্যান্ট।\n"
        "• যেকোনো প্রশ্ন লিখে মেসেজ দিতে পারেন।\n"
        "• চার্টের স্ক্রিনশট পাঠালে আমি ক্যান্ডেলস্টিক প্যাটার্ন ও ট্রেন্ড অ্যানালাইসিস করে পরের ক্যান্ডেলের প্রেডিকশন দেব।"
    )
    await update.message.reply_text(welcome_msg)

# সাধারণ টেক্সট মেসেজ হ্যান্ডলার
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ]
        )
        reply_text = response.choices[0].message.content
        await update.message.reply_text(reply_text)
    except Exception as e:
        await update.message.reply_text(f"দুঃখিত এমোন ভাই, এআই প্রসেস করতে সমস্যা হয়েছে: {str(e)}")

# ফটো / চার্ট এনালাইসিস হ্যান্ডলার (Vision AI)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("🔍 চার্ট বিশ্লেষণ করা হচ্ছে, ক্যান্ডেলস্টিক প্যাটার্ন চেক করা হচ্ছে...")
    
    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        base64_image = base64.b64encode(photo_bytes).decode('utf-8')

        caption = update.message.caption or "এই চার্টটি ক্যান্ডেলস্টিক প্যাটার্ন, সাপোর্ট-রেজিস্ট্যান্স ও ট্রেন্ড অনুযায়ী বিস্তারিত অ্যানালাইসিস করে পরের ক্যান্ডেলের সম্ভাবনা জানান।"

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": caption},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        
        reply_text = response.choices[0].message.content
        await status_msg.edit_text(reply_text)
        
    except Exception as e:
        await status_msg.edit_text(f"ছবি এনালাইসিস করতে সমস্যা হয়েছে: {str(e)}")

# -------------------------------------------------------------
# ৩. মেইন ফাংশন
# -------------------------------------------------------------
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("AI Telegram Bot Successfully Started!")
    app.run_polling()

if __name__ == "__main__":
    main()
