import logging
from nlp_logic import interpret_intent
from sensor import get_umidade_percentagem
from database import get_info, check_owner_vases, get_internal_user_id

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

async def check_plant_state(plant_name):
    if not plant_name:
        return "❌ Nenhuma planta foi definida ainda. Use /start para configurar sua planta."

    try:
        plant = await get_info(plant_name)
    except Exception as e:
        logging.error(f"Erro ao buscar dados da planta '{plant_name}': {e}")
        return "❌ Ocorreu um erro ao acessar os dados da planta."

    if not plant:
        return "❌ Dados da planta não encontrados."

    try:
        if isinstance(plant, dict):
            min_humidity = plant.get('umidMin')
            max_humidity = plant.get('umidMax')
            name = plant.get('name')
        else:
            # Caso seja lista/tupla com dados
            row = plant[0]
            min_humidity = row[2]
            max_humidity = row[3]
            name = row[1]
    except Exception as e:
        logging.error(f"Erro ao interpretar dados da planta: {e}")
        return "❌ Dados da planta estão incompletos ou mal formatados."

    umid = get_umidade_percentagem()
    if umid is None:
        return "❌ Não foi possível obter o valor de umidade do sensor."

    if umid < min_humidity:
        umid_status = "🔻 Baixa"
    elif umid > max_humidity:
        umid_status = "🔺 Alta"
    else:
        umid_status = "✅ Ideal"

    status = [
        f"🌿 **Planta:** {name}",
        f"💧 Umidade: {umid}% (Ideal: {min_humidity}–{max_humidity}%) {umid_status}"
    ]
    return "\n".join(status)

def list_user_vases(telegram_id):
    if not telegram_id:
        return "❌ Telegram ID inválido ou não fornecido."

    internal_id = get_internal_user_id(telegram_id)
    if internal_id is None:
        return "❌ Usuário não encontrado."

    vasos = check_owner_vases(internal_id)
    if not vasos:
        return "❌ Você não tem vasos cadastrados."

    return "🌱 Seus vasos:\n" + "\n".join(vasos)

def answer_question(question: str, telegram_id: str = None) -> str:
    category = interpret_intent(question)

    handlers = {
        "umidade": lambda: (
            f"💧 Umidade atual: {get_umidade_percentagem()}%"
            if get_umidade_percentagem() is not None
            else "❌ Não foi possível obter a umidade."
        ),
        "mostrar_vasos": lambda: list_user_vases(telegram_id) if telegram_id else "❌ Telegram ID necessário para mostrar vasos."
        # Aqui dá pra expandir pra outras categorias
    }

    handler = handlers.get(category)
    if handler:
        try:
            return handler()
        except Exception as e:
            logging.error(f"Erro no handler da categoria '{category}': {e}")
            return "❌ Ocorreu um erro ao processar sua solicitação."

    return (
        "❓ Desculpe, não entendi sua pergunta. "
        "Tente algo como: 'qual a temperatura?', 'está muito seco?', ou 'como está a luz?'."
    )
