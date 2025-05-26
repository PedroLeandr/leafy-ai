import serial
import time
import threading
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

porta = "COM3"
baud_rate = 9600
umidadePercentagem = None

try:
    arduino = serial.Serial(porta, baud_rate)
    time.sleep(2)
    logging.info(f"Porta serial {porta} aberta com sucesso.")
except serial.SerialException as e:
    logging.error(f"Erro ao abrir a porta serial: {e}")
    arduino = None

def mapear_para_percentagem(valor):
    logging.debug(f"Mapeando valor bruto {valor} para percentagem.")
    return valor * 100 / 1023

def tocar_audio():
    if arduino and arduino.is_open:
        logging.info("Tocando áudio via Arduino.")
        arduino.write(b'p')
    else:
        logging.warning("Tentativa de tocar áudio, mas Arduino não está disponível ou fechado.")

def ler_dados():
    global umidadePercentagem
    if not arduino:
        logging.error("Arduino não está disponível.")
        return

    logging.info("Iniciando leitura da serial.")
    while True:
        try:
            linha = arduino.readline().decode('utf-8').strip()
            logging.debug(f"Linha recebida: '{linha}'")
            if linha.isdigit():
                valor_bruto = int(linha)
                umidadePercentagem = round(mapear_para_percentagem(valor_bruto), 1)
                logging.info(f"Umidade: {umidadePercentagem}%")
            else:
                logging.debug(f"Entrada ignorada: {linha}")
        except Exception as e:
            logging.error(f"Erro na leitura da serial: {e}")

def get_umidade_percentagem():
    logging.debug(f"Valor atual de umidade solicitado: {umidadePercentagem}")
    return umidadePercentagem

def iniciar_thread_sensor():
    logging.info("Iniciando thread do sensor.")
    threading.Thread(target=ler_dados, daemon=True).start()

if __name__ == "__main__":
    iniciar_thread_sensor()
    while True:
        print(get_umidade_percentagem())
        time.sleep(1)
