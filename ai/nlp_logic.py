import spacy
from fuzzywuzzy import fuzz
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

npl = spacy.load("pt_core_news_sm")

PLANT_NAMES = ["rosa", "cacto", "bambu", "violeta", "lirio", "couve-galega"]

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
    for token in doc:
        logging.debug(f"Token: '{token.text}', lema: '{token.lemma_}'")
        if token.lemma_ in ["estado", "status", "como", "bem", "saúde", "condição", "planta"]:
            logging.info("Intenção interpretada: status_planta")
            return "status_planta"
        elif token.lemma_ in ["umidade", "úmido", "seco", "água", "molhada"]:
            logging.info("Intenção interpretada: umidade")
            return "umidade"
    logging.info("Intenção interpretada: desconhecido")
    return "desconhecido"
