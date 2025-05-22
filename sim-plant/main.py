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

from db import cursor
from plants.vase import DatabasePlant

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
        vaso_id = input("ID do vaso: ").strip().upper()
        if vaso_id in plants_dict:
            plants_dict[vaso_id].water_plant()
        else:
            print("Vaso não encontrado.")
    elif escolha == '2':
        for p in plants_dict.values():
            p.water_plant()
    elif escolha == '3':
        vaso_id = input("ID do vaso: ").strip().upper()
        if vaso_id in plants_dict:
            plants_dict[vaso_id].status()
        else:
            print("Vaso não encontrado.")
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
    if not args:
        print('Uso: python main.py [id_do_vaso_1 id_do_vaso_2 ... | all]')
        return

    if 'all' in [a.lower() for a in args]:
        cursor.execute("SELECT id FROM vases")
        vaso_ids = [row[0] for row in cursor.fetchall()]
    else:
        vaso_ids = [arg.strip().upper() for arg in args]

    targets = []

    for vaso_id in vaso_ids:
        cursor.execute("SELECT plantId FROM vases WHERE id = %s", (vaso_id,))
        result = cursor.fetchone()
        if result:
            plant_id = result[0]
            cursor.execute("SELECT name FROM plants WHERE id = %s", (plant_id,))
            plant_result = cursor.fetchone()
            if plant_result:
                plant_name = plant_result[0]
                try:
                    targets.append((vaso_id, DatabasePlant(plant_name, vaso_id)))
                except ValueError as e:
                    print(e)
            else:
                print(f"Planta com ID {plant_id} não encontrada.")
        else:
            print(f"Vaso com ID {vaso_id} não encontrado.")

    if not targets:
        return

    plants_dict = {vid: plant for vid, plant in targets}

    print(f"Simulador iniciado para vasos: {', '.join(plants_dict.keys())}.")
    print("Pressiona 'p' para abrir o menu de ações a qualquer momento.")

    threading.Thread(target=key_listener, args=(plants_dict,), daemon=True).start()

    try:
        while True:
            if not menu_ativo:
                for p in plants_dict.values():
                    p.status()
                print('-'*60)
            time.sleep(1)
    except KeyboardInterrupt:
        print('Simulação terminada.')

if __name__ == '__main__':
    main()
