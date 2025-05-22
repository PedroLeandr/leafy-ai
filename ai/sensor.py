# # sensor.py

# import serial
# import os
# from dotenv import load_dotenv
# import threading

# load_dotenv()

# porta = os.getenv('PORTA_SERIAL')
# baud_rate = int(os.getenv('BAUD_RATE'))

# umidadePercentagem = None
# temperatura = None
# luminosidade = None

# def ler_dados():
#     global umidadePercentagem, temperatura, luminosidade
#     arduino = serial.Serial(porta, baud_rate)
#     print("A ler dados da serial\n")
    
#     while True:
#         linha = arduino.readline().decode('utf-8').strip()
#         if linha.startswith('[') and linha.endswith(']'):
#             linha = linha[1:-1]
#             valores = linha.split(",")
#             if len(valores) == 3:
#                 try:
#                     umidadePercentagem = float(valores[0])
#                     temperatura = float(valores[1])
#                     luminosidade = float(valores[2])
#                     print(
#                         f"Umidade: {umidadePercentagem}% | "
#                         f"Temperatura: {temperatura}°C | "
#                         f"Luminosidade: {luminosidade} lux"
#                     )
#                 except ValueError:
#                     print("Erro ao converter os valores da linha:", linha)

# def get_umidade_percentagem():
#     return umidadePercentagem

# def get_temperatura():
#     return temperatura

# def get_luminosidade():
#     return luminosidade

# def iniciar_thread_sensor():
#     thread = threading.Thread(target=ler_dados, daemon=True)
#     thread.start()

# # Removida a chamada direta a iniciar_thread_sensor() daqui,
# # para evitar duplicar threads — o bot é que inicia a thread.


# --------------------------------------------------------------------------------------


import subprocess
import sys
import os
import json

# venv_python = os.path.join(os.path.dirname(sys.executable), 'python.exe')

# subprocess.run([
#     venv_python,
#     os.path.abspath(os.path.join(__file__, '..', '..', 'sim-plant', 'main.py')),
#     'LEAFY-119540',
#     '--headless'
# ])

vaseid = 'LEAFY-119540'

vase = os.path.abspath(os.path.join(__file__, '..', '..', 'sim-plant', 'states', 'LEAFY-119540.json'))

with open(vase, 'r', encoding='utf-8') as f:
    dados = json.load(f)
    humidade = dados['water']


umidadePercentagem = dados['water']

def get_umidade_percentagem():
    return umidadePercentagem

print(dados)
print(humidade)
