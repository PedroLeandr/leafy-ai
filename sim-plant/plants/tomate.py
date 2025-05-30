
from db import cursor

class Tomate():
    def __init__(self):
        cursor.execute(
            "SELECT waterMin, waterMax, tempMin, tempMax, umidMin, umidMax, lumMin, lumMax FROM plants WHERE name = 'tomate'"
        )
        result = cursor.fetchone()
        if result:
            water_min, water_max, temp_min, temp_max, umid_min, umid_max, lum_min, lum_max = result
            super().__init__(
                name='tomate',
                water_min=water_min, water_max=water_max,
                temp_min=temp_min, temp_max=temp_max,
                hum_min=umid_min, hum_max=umid_max,
                lum_min=lum_min, lum_max=lum_max
            )
        else:
            raise ValueError("Tomate não encontrado na base de dados")
