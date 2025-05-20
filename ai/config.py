from dotenv import load_dotenv, set_key
import os
import mysql.connector

# Caminho para o arquivo .env
env_path = '.env'

def config():
    # Verifica se o arquivo .env existe
    if not os.path.exists(env_path):
        # Se não existir, cria um novo arquivo .env
        with open(env_path, 'w') as f:
            f.write("# Configurações do bot\n")
            f.write("TOKEN=\n")
            f.write("DB_HOST=\n")
            f.write("DB_USER=\n")
            f.write("DB_PASSWORD=\n")
            f.write("DB_NAME=\n")
            f.write("PORTA_SERIAL=\n")
            f.write("BAUD_RATE=\n")
            f.write("PLANT_NAME=\n")
            f.write("PLANT_CIENTIFIC_NAME=\n")
            f.write("UMIDADE_MINIMA=\n")
            f.write("UMIDADE_MAXIMA=\n")
            f.write("TEMPERATURA_MINIMA=\n")
            f.write("TEMPERATURA_MAXIMA=\n")
            f.write("LUZ_MINIMA=\n")
            f.write("LUZ_MAXIMA=\n")

    print(".env criado com sucesso (se não existia).")

def mudar_planta(plant_name):
    # Conectar ao banco de dados MySQL
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='000000',
        database='Leafy'
    )
    
    cursor = conn.cursor()

    # Buscar todas as informações da planta, exceto o id
    cursor.execute('''
        SELECT nome, nome_cientifico, umidade_minima, umidade_maxima, temperatura_minima, temperatura_maxima, luz_minima, luz_maxima
        FROM plantas WHERE nome = %s
    ''', (plant_name,))
    
    result = cursor.fetchone()
    
    if result:
        plant_name = result[0]  # Nome da planta
        plant_cientific_name = result[1]  # Nome científico
        umidade_minima = result[2]  # Umidade mínima
        umidade_maxima = result[3]  # Umidade máxima
        temperatura_minima = result[4]  # Temperatura mínima
        temperatura_maxima = result[5]  # Temperatura máxima
        luz_minima = result[6]  # Luz mínima
        luz_maxima = result[7]  # Luz máxima
        
        # Atualizar o arquivo .env com todas as informações da planta
        set_key(env_path, 'PLANT_NAME', plant_name)
        set_key(env_path, 'PLANT_CIENTIFIC_NAME', plant_cientific_name)
        set_key(env_path, 'UMIDADE_MINIMA', str(umidade_minima))
        set_key(env_path, 'UMIDADE_MAXIMA', str(umidade_maxima))
        set_key(env_path, 'TEMPERATURA_MINIMA', str(temperatura_minima))
        set_key(env_path, 'TEMPERATURA_MAXIMA', str(temperatura_maxima))
        set_key(env_path, 'LUZ_MINIMA', str(luz_minima))
        set_key(env_path, 'LUZ_MAXIMA', str(luz_maxima))
        
        print(f"Informações da planta '{plant_name}' foram atualizadas no .env")
    else:
        print(f"Planta '{plant_name}' não encontrada na base de dados.")
    
    # Fechar a conexão com o banco de dados
    conn.close()

# Configurações iniciais (criação do .env, caso não exista)
config()

