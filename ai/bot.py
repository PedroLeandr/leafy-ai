import random
import logging
from sensor import tocar_audio, get_umidade_percentagem, iniciar_thread_sensor
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from logic import check_plant_state, answer_question
from nlp_logic import interpret_intent, extract_plant_name
from database import (
    check_if_user_exist, insert_user, user_name,
    get_internal_user_id,
    get_info,
    check_owner_vases, insert_vase, insert_vase_owner
)

TOKEN = "7614900129:AAGzSUsWyWfa972YtF80ueibs61dwvmhPuU"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

def get_vase_info(vase_id, get_umidade_func):
    from database import con
    cursor = con.cursor()
    cursor.execute(
        "SELECT p.name, p.umidade_min, p.umidade_max FROM plants p "
        "JOIN vases ON vases.plant_name = p.name "
        "WHERE vases.id = %s", (vase_id,)
    )
    plant = cursor.fetchone()

    if not plant:
        return f"🪴 Vaso ID: {vase_id}\n❌ Nenhuma planta associada a este vaso."

    plant_name, min_hum, max_hum = plant
    umid = get_umidade_func()
    if umid is None:
        umid_status = "❌ Não foi possível obter umidade."
    elif umid < min_hum:
        umid_status = "🔻 Umidade baixa"
    elif umid > max_hum:
        umid_status = "🔺 Umidade alta"
    else:
        umid_status = "✅ Umidade ideal"

    info_text = (
        f"🪴 Vaso ID: {vase_id}\n"
        f"🌿 Planta: {plant_name}\n"
        f"💧 Umidade atual: {umid}% ({umid_status})\n"
        f"(Ideal: {min_hum}% - {max_hum}%)"
    )
    return info_text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    logger.debug(f"/start por {telegram_id}")
    internal_id = check_if_user_exist(telegram_id)
    if internal_id:
        logger.debug(f"Usuário já existente: {internal_id}")
        await update.message.reply_text(f"Olá! Você já está cadastrado {user_name}. Como posso te ajudar?")
    else:
        context.user_data["awaiting_name"] = True
        context.user_data["user_id"] = telegram_id
        logger.debug(f"Novo usuário: {telegram_id}")
        await update.message.reply_text("Olá! Você é novo aqui. Qual é o seu nome?")

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()
    logger.debug(f"Mensagem recebida: {msg}")
    if context.user_data.get("awaiting_name"):
        telegram_id = context.user_data.get("user_id")
        name = msg
        internal_id = insert_user(telegram_id, name)
        logger.debug(f"Usuário inserido: {name}, ID: {internal_id}")
        context.user_data.pop("awaiting_name")
        await update.message.reply_text(f"Bem-vindo, {name}! Como posso ajudar?")
        return

    if context.user_data.get("awaiting_plant"):
        plant = extract_plant_name(msg)
        logger.debug(f"Nome da planta extraído: {plant}")
        if plant:
            data = await get_info(plant)
            logger.debug(f"Dados da planta encontrados: {bool(data)}")
            if data:
                context.user_data["plant_candidate"] = plant
                context.user_data["awaiting_plant"] = False
                kb = [[InlineKeyboardButton("Sim", callback_data=f"confirm_{plant}")], [InlineKeyboardButton("Não", callback_data="cancelar")]]
                await update.message.reply_text(f"Você quer dizer '{plant}'?", reply_markup=InlineKeyboardMarkup(kb))
            else:
                await update.message.reply_text(f"❌ Planta '{plant}' não encontrada.")
        else:
            await update.message.reply_text("❌ Envie apenas o nome da planta.")
        return

    intent = interpret_intent(msg)
    logger.debug(f"Intenção interpretada: {intent}")
    if intent == "status_planta":
        res = await check_plant_state(context.user_data.get("plant"))
    elif intent in ["temperatura", "umidade", "luminosidade"]:
        res = answer_question(msg)
    else:
        res = "❓ Não entendi."
    await update.message.reply_text(res)

async def vasos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    logger.debug(f"/vasos por {telegram_id}")
    internal_id = get_internal_user_id(telegram_id)
    vases = check_owner_vases(internal_id)
    logger.debug(f"Vasos encontrados: {vases}")
    kb = [[InlineKeyboardButton(str(v), callback_data=f"vase_{v}")] for v in vases]
    kb.append([InlineKeyboardButton("➕ Adicionar novo vaso", callback_data="add_vase")])
    await update.message.reply_text("🪴 Seus vasos:", reply_markup=InlineKeyboardMarkup(kb))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data
    telegram_id = q.from_user.id
    logger.debug(f"Botão clicado: {d} por {telegram_id}")
    internal_id = get_internal_user_id(telegram_id)

    if d.startswith("confirm_"):
        p = d.split("confirm_")[1]
        context.user_data["plant"] = p
        logger.debug(f"Planta confirmada: {p}")
        await q.edit_message_text(f"Planta '{p}' configurada! ✅")

    elif d == "cancelar":
        context.user_data["awaiting_plant"] = True
        logger.debug("Confirmação de planta cancelada.")
        await q.edit_message_text("Diga o nome da planta.")

    elif d.startswith("vase_"):
        vid = d.split("vase_")[1]
        logger.debug(f"Vaso selecionado: {vid}")
        info_text = get_vase_info(vid, get_umidade_percentagem)
        await q.edit_message_text(info_text)

    elif d == "add_vase":
        nid = insert_vase()
        insert_vase_owner(nid, internal_id)
        logger.debug(f"Novo vaso inserido: {nid}")
        vases = check_owner_vases(internal_id)
        kb = [[InlineKeyboardButton(str(v), callback_data=f"vase_{v}")] for v in vases]
        kb.append([InlineKeyboardButton("➕ Adicionar novo vaso", callback_data="add_vase")])
        await q.edit_message_text(f"✅ Novo vaso: {nid}\n\n🪴 Seus vasos:", reply_markup=InlineKeyboardMarkup(kb))

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("📷 Foto recebida!")
    frases = [
        "📸 Eu sei que sou bonita.",
        "😳 Já estou a corar...",
        "🌿 Estou a ficar murcha de vergonha!",
        "✨ Essa luz realça as minhas folhas!",
        "😎 Planta fotogênica? Sempre!",
        "💧 Eu mereço um filtro também, né?",
        "📷 Cuidado, estou tímida!"
    ]
    tocar_audio()
    await update.message.reply_text(random.choice(frases))

def main():
    iniciar_thread_sensor()
    logger.info("Bot iniciado...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("vasos", vasos))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
