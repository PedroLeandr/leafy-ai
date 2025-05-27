import spacy
from fuzzywuzzy import fuzz
import logging
from database import load_all_plant_names

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

npl = spacy.load("pt_core_news_sm")

PLANT_NAMES = load_all_plant_names()

def get_closest_match(word, valid_words):
    best_match = None
    highest_score = 0
    logging.debug(f"Buscando correspondência para: '{word}'")
    for valid_word in valid_words:
        score = fuzz.ratio(word, valid_word)
        logging.debug(f"Comparando com '{valid_word}', score: {score}")
        if score > highest_score:
            highest_score = score
            best_match = valid_word
    if highest_score > 70:
        logging.debug(f"Melhor correspondência: '{best_match}' com score {highest_score}")
        return best_match
    else:
        logging.debug(f"Nenhuma correspondência boa para '{word}' (score máximo {highest_score})")
        return None

def extract_plant_name(text: str):
    text = text.lower()
    plants = [word.lower() for word in PLANT_NAMES]
    words = text.split()
    logging.debug(f"Extraindo nome da planta do texto: '{text}'")
    for word in words:
        match = get_closest_match(word, plants)
        if match:
            logging.info(f"Nome da planta identificado: '{match}'")
            return match
    logging.info("Nenhuma planta identificada.")
    return None

def interpret_intent(question: str) -> str:
    question = question.lower()
    doc = npl(question)
    logging.debug(f"Interpretando intenção da pergunta: '{question}'")

    lemmas = {token.lemma_ for token in doc}
    logging.debug(f"Lemas encontrados: {lemmas}")

    if lemmas & {"estado", "status", "como", "bem", "saúde", "condição", "planta", "vai", "tá", "está", "anda"}:
        logging.info("Intenção interpretada: status_planta")
        return "status_planta"

    if lemmas & {"umidade", "úmido", "seco", "água", "molhado", "molhada", "regado", "rega"}:
        logging.info("Intenção interpretada: umidade")
        return "umidade"

    if lemmas & {"temperatura", "quente", "frio", "calor", "clima", "ambiente"}:
        logging.info("Intenção interpretada: temperatura")
        return "temperatura"

    if lemmas & {"luz", "luminosidade", "claro", "escuro", "iluminação"}:
        logging.info("Intenção interpretada: luminosidade")
        return "luminosidade"

    if lemmas & {"vaso", "vasos", "meus", "mostrar", "lista", "ver", "plantas"}:
        logging.info("Intenção interpretada: mostrar_vasos")
        return "mostrar_vasos"

    if lemmas & {"nome", "chamar", "identificar", "conhece"} and "planta" in question:
        logging.info("Intenção interpretada: identificar_planta")
        return "identificar_planta"

    if lemmas & {"adicionar", "novo", "criar", "registrar"} and "vaso" in question:
        logging.info("Intenção interpretada: adicionar_vaso")
        return "adicionar_vaso"

    logging.info("Intenção interpretada: desconhecido")
    return "desconhecido"

