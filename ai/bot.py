from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from logic import check_plant_state, answer_question
from database import get_info
from nlp_logic import extract_plant_name, interpret_intent
from config import mudar_planta, config
from dotenv import load_dotenv, set_key
import os
from sensor import iniciar_thread_sensor

load_dotenv()
TOKEN = os.getenv("TOKEN")
iniciar_thread_sensor()

def create_confirmation_buttons(plant_name):
    keyboard = [
        [InlineKeyboardButton("Sim", callback_data=f"confirm_{plant_name}")],
        [InlineKeyboardButton("Não", callback_data="cancelar")]
    ]
    return InlineKeyboardMarkup(keyboard)

def check_if_configured():
    required_keys = [
        'PLANT_NAME', 'PLANT_CIENTIFIC_NAME', 'UMIDADE_MINIMA', 'UMIDADE_MAXIMA',
        'TEMPERATURA_MINIMA', 'TEMPERATURA_MAXIMA', 'LUZ_MINIMA', 'LUZ_MAXIMA'
    ]
    for key in required_keys:
        if not os.getenv(key):
            return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_if_configured():
        await update.message.reply_text("Olá! Sou o Vaso Assistente. Qual é o nome da sua planta? 🌱")
        context.user_data["awaiting_plant"] = True
    else:
        plant_name = os.getenv("PLANT_NAME")
        context.user_data["plant"] = plant_name 
        await update.message.reply_text(f"Olá! A configuração da sua planta '{plant_name}' já está completa. Como posso te ajudar?")

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()

    if context.user_data.get("awaiting_plant"):
        plant_name = extract_plant_name(msg)

        if plant_name:
            plant_data = await get_info(plant_name)
            if plant_data:
                context.user_data["plant_candidate"] = plant_name
                context.user_data["awaiting_plant"] = False
                await update.message.reply_text(
                    f"Você quer dizer '{plant_name}'?",
                    reply_markup=create_confirmation_buttons(plant_name)
                )
            else:
                await update.message.reply_text(f"❌ Não encontrei a planta '{plant_name}' na minha base de dados MySQL. Tente novamente.")
        else:
            await update.message.reply_text("❌ Não consegui identificar o nome da planta na sua mensagem. Por favor, envie apenas o nome.")
        return

    intent = interpret_intent(msg)

    if intent == "status_planta":
        planta = context.user_data.get("plant")
        response = await check_plant_state(planta)
    elif intent in ["temperatura", "umidade", "luminosidade"]:
        response = answer_question(msg)
    else:
        response = "❓ Desculpe, não entendi sua pergunta. Pergunte algo como 'como está minha planta?' ou 'qual é a temperatura?'"

    await update.message.reply_text(response)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    callback_data = query.data

    if callback_data.startswith("confirm_"):
        plant_name = callback_data.split("confirm_")[1]
        mudar_planta(plant_name)
        context.user_data["plant"] = plant_name
        await query.edit_message_text(f"Planta '{plant_name}' configurada com sucesso! ✅")
    elif callback_data == "cancelar":
        context.user_data["awaiting_plant"] = True
        await query.edit_message_text("Ação cancelada. Por favor, diga novamente o nome da planta.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
    app.add_handler(CallbackQueryHandler(button))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    config()
    main()
