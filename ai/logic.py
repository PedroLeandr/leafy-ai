import os
# from dotenv import load_dotenv
from nlp_logic import interpret_intent
from sensor import get_umidade_percentagem
from database import get_info


async def check_plant_state(plant_name=None):
    # DEBUG: entrada da função
   

    if plant_name is None:
        return "❌ Nenhuma planta foi definida ainda. Por favor, use /start para definir sua planta."
    
    # Obter dados da base
    plant = await get_info(plant_name)
    # DEBUG: conteúdo retornado de get_info
    if not plant or not isinstance(plant, (list, tuple)) or len(plant) == 0:
       
        return "❌ Dados da planta não foram encontrados corretamente na base de dados."

    row = plant[0]
    # DEBUG: verificar estrutura da linha
   

    # Espera-se agora 9 campos: id, nome, nome_cientifico, umidade_min, umidade_max, temp_min, temp_max, luz_min, luz_max
    if len(row) < 9:
        
        return "❌ Dados da planta não foram encontrados corretamente na base de dados."

    # Desempacotar valores
    (_id, Plant_Name, Scientific_Name,
     Min_Humidity, Max_Humidity,
     Min_Temperature, Max_Temperature,
     Min_Light, Max_Light) = row[:9]

    status = [f"🌿 **Planta:** {Plant_Name}"]

    umid = get_umidade_percentagem()
    if umid is None:
        return "❌ Não foi possível obter o valor de umidade do sensor."
    if umid < Min_Humidity:
        umid_status = "🔻 Baixa"
    elif umid > Max_Humidity:
        umid_status = "🔺 Alta"
    else:
        umid_status = "✅"
    status.append(f"💧 Umidade: {umid}% (Ideal: {Min_Humidity}–{Max_Humidity}%) {umid_status}")

    return "\n".join(status)


def answer_question(question: str) -> str:

    category = interpret_intent(question)
    umid = get_umidade_percentagem()

    if category == "umidade":
        if umid is None:
            return "❌ Não foi possível obter a umidade."
        return f"💧 Umidade atual: {umid}%"
    else:
        return (
            "❓ Desculpe, não entendi sua pergunta. "
            "Tente algo como: 'qual a temperatura?', 'está muito seco?', ou 'como está a luz?'."
        )
