import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import whisper
import subprocess
from openinterpreter import interpreter

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"  # Get this from @BotFather
ALLOWED_USER_ID = 123456789  # Replace with your Telegram ID (safety latch)

# --- INITIALIZE LOCAL AI ---
print(">>> LOADING WHISPER MODEL (EARS)...")
audio_model = whisper.load_model("base") # Runs on GPU if available

# Initialize OpenInterpreter
print(">>> INITIALIZING OPENINTERPRETER (BRAIN)...")
interpreter.llm.model = "local"  # Using local model
interpreter.llm.temperature = 0.0  # More deterministic responses
interpreter.computer.import_computer_api = True  # Allow system commands

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🔊 Tour Manager Online. Ready for input.")

# --- VOICE NOTE HANDLER ---
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ALLOWED_USER_ID: 
        return

    # 1. Download Voice File
    new_file = await context.bot.get_file(update.message.voice.file_id)
    file_path = "voice_input.ogg"
    await new_file.download_to_drive(file_path)

    # 2. Transcribe (Speech to Text)
    result = audio_model.transcribe(file_path)
    transcribed_text = result["text"]
    
    await update.message.reply_text(f"🎤 Heard: {transcribed_text}")
    
    # 3. PROCESS WITH OPENINTERPRETER
    try:
        response = interpreter.chat(transcribed_text)
        # Format the response for Telegram
        if isinstance(response, list):
            response_text = str(response[-1].get('content', 'Processing completed'))
        else:
            response_text = str(response)
        
        # Ensure response is under Telegram's character limit
        if len(response_text) > 4096:
            response_text = response_text[:4093] + "..."
            
        await update.message.reply_text(f"🤖 Response: {response_text}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error processing voice command: {str(e)}")

# --- TEXT HANDLER ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ALLOWED_USER_ID: 
        return

    incoming_text = update.message.text
    
    try:
        response = interpreter.chat(incoming_text)
        # Format the response for Telegram
        if isinstance(response, list):
            response_text = str(response[-1].get('content', 'Processing completed'))
        else:
            response_text = str(response)
        
        # Ensure response is under Telegram's character limit
        if len(response_text) > 4096:
            response_text = response_text[:4093] + "..."
            
        await update.message.reply_text(response_text)
    except Exception as e:
        await update.message.reply_text(f"❌ Error processing text command: {str(e)}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    
    print(">>> TOUR MANAGER LISTENING...")
    application.run_polling()