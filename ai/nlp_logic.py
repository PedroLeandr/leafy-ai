import spacy
from fuzzywuzzy import fuzz

npl = spacy.load("pt_core_news_sm")

PLANT_NAMES = ["rosa", "cacto", "bambu", "violeta", "lirio", "couve-galega"]

def get_closest_match(word, valid_words):
    best_match = None
    highest_score = 0
    for valid_word in valid_words:
        score = fuzz.ratio(word, valid_word)
        if score > highest_score:
            highest_score = score
            best_match = valid_word
    return best_match if highest_score > 70 else None

def extract_plant_name(text: str):
    text = text.lower()

    plants = [word.lower() for word in PLANT_NAMES]

    words = text.split()

    for word in words:
        match = get_closest_match(word, plants)
        if match:
            return match
    return None



def interpret_intent(question: str) -> str:
    question = question.lower()
    doc = npl(question)

    for token in doc:
        if token.lemma_ in ["estado", "status", "como", "bem", "saúde", "condição", "planta"]:
            return "status_planta"
        elif token.lemma_ in ["temperatura", "calor", "quente"]:
            return "temperatura"
        elif token.lemma_ in ["umidade", "úmido", "seco", "água", "molhada"]:
            return "umidade"
        elif token.lemma_ in ["luz", "iluminação", "claro", "brilho"]:
            return "luminosidade"
    
    return "desconhecido"


