import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# --- কনফিগারেশন ---
GEMINI_API_KEY = "আপনার_জেমিmini_এপিআই_কী"
TELEGRAM_BOT_TOKEN = "আপনার_টেলিগ্রাম_বট_টোকেন"

# Gemini সেটিংস
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# ইউজারদের চ্যাট হিস্ট্রি রাখার জন্য ডিকশনারি
chat_sessions = {}

# লগিং সেটআপ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# /start কমান্ড হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # নতুন চ্যাট সেশন শুরু করা
    chat_sessions[user_id] = model.start_chat(history=[])
    await update.message.reply_text("হ্যালো! আমি আপনার উন্নত এআই অ্যাসিস্ট্যান্ট। আমি আপনার আগের কথা মনে রাখতে পারি। কি সাহায্য করতে পারি?")

# মেসেজ হ্যান্ডলার
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    # যদি ইউজারের কোনো সেশন না থাকে, তবে নতুন সেশন তৈরি করা
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])

    try:
        # টাইপিং স্ট্যাটাস দেখানো (ইউজার বুঝবে বট কাজ করছে)
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # চ্যাট সেশন থেকে উত্তর জেনারেট করা (এটি হিস্ট্রি মেইনটেইন করে)
        response = chat_sessions[user_id].send_message(user_text)
        
        # উত্তর পাঠানো
        await update.message.reply_text(response.text)
        
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("দুঃখিত, বর্তমানে সার্ভারে সমস্যা হচ্ছে। একটু পরে আবার চেষ্টা করুন।")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # কমান্ড এবং মেসেজ হ্যান্ডলার যুক্ত করা
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("বট সফলভাবে চালু হয়েছে...")
    application.run_polling()