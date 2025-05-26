import random
import logging
import mysql.connector

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0000",
    database="leafy"
)
cursor = con.cursor()

user_name = ""

def check_if_user_exist(telegram_id):
    logging.debug(f"Checando existência do user com telegram_id={telegram_id}")
    cursor.execute('SELECT id, name FROM users WHERE telegramId = %s', (telegram_id,))
    row = cursor.fetchone()
    if row:
        global user_name
        user_name = row[1]
        logging.debug(f"Usuário encontrado: id={row[0]}, nome={user_name}")
        return row[0]
    logging.debug("Usuário não encontrado.")
    return None

def insert_user(telegram_id, name):
    logging.debug(f"Inserindo usuário telegram_id={telegram_id}, nome={name}")
    cursor.execute('INSERT INTO users (telegramId, name) VALUES (%s, %s)', (telegram_id, name))
    con.commit()
    inserted_id = cursor.lastrowid
    logging.debug(f"Usuário inserido com id={inserted_id}")
    return inserted_id

def get_internal_user_id(telegram_id):
    logging.debug(f"Obtendo internal user id para telegram_id={telegram_id}")
    cursor.execute('SELECT id FROM users WHERE telegramId = %s', (telegram_id,))
    row = cursor.fetchone()
    if row:
        logging.debug(f"ID interno do usuário: {row[0]}")
        return row[0]
    logging.debug("ID interno não encontrado.")
    return None

def insert_vase():
    uuid = f"LEAFY-{random.randint(0, 999999):06d}"
    logging.debug(f"Inserindo vaso com id={uuid}")
    cursor.execute('INSERT INTO vases (id) VALUES (%s)', (uuid,))
    con.commit()
    return uuid

def check_owner_vases(internal_user_id):
    logging.debug(f"Checando vasos do usuário interno id={internal_user_id}")
    cursor.execute('SELECT vaseId FROM vases_users WHERE userId = %s', (internal_user_id,))
    rows = cursor.fetchall()
    vase_list = [row[0] for row in rows] if rows else []
    logging.debug(f"Vasos encontrados: {vase_list}")
    return vase_list

def insert_vase_owner(vase_id, internal_user_id):
    logging.debug(f"Associando vaso {vase_id} ao usuário {internal_user_id}")
    cursor.execute('INSERT INTO vases_users (vaseId, userId) VALUES (%s, %s)', (vase_id, internal_user_id))
    con.commit()
    return vase_id

def get_info(plant_name):
    logging.debug(f"Buscando informações para planta '{plant_name}'")
    cursor.execute('SELECT * FROM plants WHERE name = %s', (plant_name,))
    row = cursor.fetchone()
    if not row:
        logging.warning(f"Nenhuma informação encontrada para planta '{plant_name}'")
        return None
    cols = [d[0] for d in cursor.description]
    info = dict(zip(cols, row))
    logging.debug(f"Informação da planta: {info}")
    return info

def get_vase_info(vase_id, get_umidade_percentagem):
    logging.debug(f"Buscando info do vaso {vase_id}")
    query = """
        SELECT p.name, p.umidMin, p.umidMax,
               p.tempMin, p.tempMax, p.lumMin, p.lumMax
        FROM plants p
        JOIN vases_plants vp ON p.id = vp.plant_id
        WHERE vp.vase_id = %s
    """
    cursor.execute(query, (vase_id,))
    planta = cursor.fetchone()

    if not planta:
        logging.warning(f"Nenhuma planta associada ao vaso {vase_id}")
        return f"❌ Nenhuma planta associada ao vaso {vase_id}."

    (nome, umid_min, umid_max, temp_min, temp_max, luz_min, luz_max) = planta

    umidade = get_umidade_percentagem()
    if umidade is None:
        umidade = "Desconhecido"
        status_umidade = "❌"
    else:
        status_umidade = "✅"
        if umidade < umid_min:
            status_umidade = "🔻 Baixa"
        elif umidade > umid_max:
            status_umidade = "🔺 Alta"

    resposta = (
        f"🌿 Vaso ID: {vase_id}\n"
        f"💧 Umidade atual: {umidade}% (Ideal: {umid_min}–{umid_max}%) {status_umidade}\n"
    )

    logging.debug(f"Info do vaso montada: {resposta.replace(chr(10), ' | ')}")
    return resposta
