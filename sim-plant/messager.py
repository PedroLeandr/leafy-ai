import sys
import time
import threading

menu_ativo = False

try:
    import msvcrt
    def get_key():
        return msvcrt.getch().decode('utf-8').lower()
except ImportError:
    import termios, tty
    def get_key():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch.lower()

from plants.alface import Alface
from plants.tomate import Tomate

PLANTS = {
    'alface': Alface,
    'tomate': Tomate
}

def menu(plants_dict):
    global menu_ativo
    menu_ativo = True

    print("\n=== MENU ===")
    print("1 - Regar planta específica")
    print("2 - Regar todas as plantas")
    print("3 - Ver status de uma planta")
    print("4 - Voltar")

    escolha = input("Escolha: ").strip()
    if escolha == '1':
        nome = input("Nome da planta: ").strip().lower()
        if nome in plants_dict:
            plants_dict[nome].water_plant()
        else:
            print("Planta não encontrada.")
    elif escolha == '2':
        for p in plants_dict.values():
            p.water_plant()
    elif escolha == '3':
        nome = input("Nome da planta: ").strip().lower()
        if nome in plants_dict:
            plants_dict[nome].status()
        else:
            print("Planta não encontrada.")
    elif escolha == '4':
        print("Voltando à simulação...")
    else:
        print("Opção inválida.")

    menu_ativo = False

def key_listener(plants_dict):
    while True:
        key = get_key()
        if key == 'p':
            menu(plants_dict)

def main():
    global menu_ativo

    args = sys.argv[1:]
    modo_headless = False

    if '--headless' in args:
        modo_headless = True
        args.remove('--headless')

    if not args:
        print('Uso: python main.py [alface|tomate|all] [--headless]')
        return

    targets = []
    if 'all' in args:
        targets = [cls() for cls in PLANTS.values()]
    else:
        for name in args:
            if name in PLANTS:
                targets.append(PLANTS[name]())
            else:
                print(f'Planta desconhecida: {name}')

    if not targets:
        return

    plants_dict = {p.name: p for p in targets}

    print(f"Simulador iniciado para: {', '.join(plants_dict.keys())}.")

    if not modo_headless:
        print("Pressiona 'p' para abrir o menu de ações a qualquer momento.")
        threading.Thread(target=key_listener, args=(plants_dict,), daemon=True).start()

    try:
        while True:
            if not menu_ativo:
                for p in targets:
                    p.status()
                print('-'*60)
            if modo_headless:
                # Se estiver em modo headless, executa uma vez e sai
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print('Simulação terminada.')

if __name__ == '__main__':
    main()
