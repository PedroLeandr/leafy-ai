import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from plant import Plant as SimulatedPlant, get_plant_from_vase_id
from db import cursor

class DatabasePlant(SimulatedPlant):
    def __init__(self, plant_name, vase_id):
        print(f"[DEBUG] DatabasePlant::__init__ -> plant_name={plant_name}, vase_id={vase_id}")
        cursor.execute(
            "SELECT waterMin, waterMax, tempMin, tempMax, umidMin, umidMax, lumMin, lumMax "
            "FROM plants WHERE name = %s",
            (plant_name,)
        )
        result = cursor.fetchone()
        print(f"[DEBUG] Query de parâmetros da planta '{plant_name}': {result}")
        if result:
            water_min, water_max, temp_min, temp_max, hum_min, hum_max, lum_min, lum_max = result
            super().__init__(
                name=plant_name,
                water_min=water_min, water_max=water_max,
                temp_min=temp_min, temp_max=temp_max,
                hum_min=hum_min, hum_max=hum_max,
                lum_min=lum_min, lum_max=lum_max,
                vase_id=vase_id
            )
            print(f"[DEBUG] DatabasePlant instanciada com sucesso: {self}")
        else:
            raise ValueError(f"[ERRO] '{plant_name}' não encontrado na base de dados")

def sim_owner_vases(user_id):
    print(f"[DEBUG] Iniciando simulação de vasos para user_id: {user_id}")
    cursor.execute('SELECT * FROM vases_users WHERE userId = %s', (user_id,))
    user_vases = cursor.fetchall()
    print(f"[DEBUG] Vasos do usuário: {user_vases}")

    full_vases = []

    for vase_row in user_vases:
        vase_id = vase_row[0]
        print(f"[DEBUG] Vaso ID: {vase_id}")

        # debug call a get_plant_from_vase_id
        try:
            print(f"[DEBUG] Chamando get_plant_from_vase_id({vase_id})")
            get_plant_from_vase_id(vase_id)
        except Exception as e:
            print(f"[ERRO] Erro ao chamar get_plant_from_vase_id: {e}")

        cursor.execute('SELECT * FROM vases WHERE id = %s', (vase_id,))
        vase_data = cursor.fetchall()
        print(f"[DEBUG] Dados do vaso {vase_id}: {vase_data}")

        for vase_entry in vase_data:
            plant_id = vase_entry[1]
            print(f"[DEBUG]  Planta ID: {plant_id}")

            cursor.execute('SELECT * FROM plants WHERE id = %s', (plant_id,))
            plant_data = cursor.fetchall()
            print(f"[DEBUG]  Dados da planta com ID {plant_id}: {plant_data}")

            if plant_data:
                plant_name = plant_data[0][1]
                print(f"[DEBUG]    Nome da planta: {plant_name}")

                try:
                    # passa agora vase_id como segundo argumento
                    plant_instance = DatabasePlant(plant_name, vase_id)
                    print(f"[DEBUG]    Instância criada: {plant_instance}")
                except ValueError as e:
                    print(f"[ERRO] {e}")

            full_vases.append(vase_entry)

    print(f"[DEBUG] Resultado final: {full_vases}")
    return full_vases if full_vases else None

# Execução para debug
if __name__ == "__main__":
    sim_owner_vases(1)
