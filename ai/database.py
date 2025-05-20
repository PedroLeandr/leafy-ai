import mysql.connector
import os
from dotenv import load_dotenv

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Acessar as variáveis de ambiente do .env
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')


# Conectar à base de dados MySQL local
conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

# Criar um cursor para executar comandos SQL
cursor = conn.cursor()

# Função para buscar informações sobre uma planta
async def get_info(plant_name):
    cursor.execute(''' 
        SELECT * FROM plantas WHERE nome = %s;
    ''', (plant_name,))
    
    result = cursor.fetchall()
    
    # Fechar a conexão e o cursor após a consulta
    conn.commit()
    
    # Retorna os resultados encontrados
    return result

