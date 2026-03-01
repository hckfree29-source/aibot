import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# --- আপনার দেওয়া তথ্য ---
GEMINI_API_KEY = "AIzaSyAALKbEd-CZ27khIDZJihDr1BrlhG-QSuM"
TELEGRAM_BOT_TOKEN = "8649911515:AAFTvgxNkLVHThj2vyDn9HtkSYfHzKBbUEQ"

# Gemini কনফিগারেশন
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# ইউজারদের চ্যাট হিস্ট্রি রাখার জন্য ডিকশনারি
chat_sessions = {}

# লগিং সেটআপ (ত্রুটি চেক করার জন্য)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# /start কমান্ড হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_sessions[user_id] = model.start_chat(history=[])
    await update.message.reply_text("স্বাগতম! আমি আপনার জেমিনি এআই বট। এখন আপনি আমার সাথে চ্যাট করতে পারেন।")

# মেসেজ হ্যান্ডলার (যেখানে আসল কাজ হবে)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    # যদি ইউজারের কোনো আগের সেশন না থাকে
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])

    try:
        # টেলিগ্রামে 'Typing...' স্ট্যাটাস দেখানো
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Gemini থেকে উত্তর আনা
        response = chat_sessions[user_id].send_message(user_text)
        
        # উত্তরটি টেলিগ্রামে পাঠানো
        await update.message.reply_text(response.text)
        
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("দুঃখিত, এপিআই কি বা সার্ভারে কোনো সমস্যা হয়েছে।")

if __name__ == '__main__':
    # টেলিগ্রাম বট অ্যাপ্লিকেশন তৈরি
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # হ্যান্ডলারগুলো যুক্ত করা
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("বটটি সফলভাবে রান হয়েছে... এখন টেলিগ্রামে মেসেজ দিয়ে পরীক্ষা করুন।")
    application.run_polling()


