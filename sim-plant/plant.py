import os
import json
import time
import math
from db import con, cursor

class Plant:
    def __init__(self, name,
                 water_min, water_max,
                 temp_min, temp_max,
                 hum_min,  hum_max,
                 lum_min,  lum_max,
                 vase_id,
                 state_dir='sim-plant/states',
                 death_threshold=60):
        print("\n" + "="*10 + " [DEBUG] INÍCIO __init__ " + "="*10)
        print(f"[DEBUG] Nome: {name} | Vaso: {vase_id}")
        self.name = name
        self.vase_id = vase_id
        self.water_min, self.water_max = water_min, water_max
        self.temp_min,  self.temp_max  = temp_min, temp_max
        self.hum_min,   self.hum_max   = hum_min, hum_max
        self.lum_min,   self.lum_max   = lum_min, lum_max
        self.death_threshold = death_threshold
        self.state_dir = state_dir
        os.makedirs(self.state_dir, exist_ok=True)
        self.state_file = os.path.join(self.state_dir, f"{self.vase_id}.json")
        print(f"[DEBUG] Ficheiro de estado: {self.state_file}")
        print("="*10 + " [DEBUG] FIM __init__ " + "="*10 + "\n")
        self._load_state()

    def _load_state(self):
        print("\n" + "-"*5 + " [DEBUG] INÍCIO _load_state " + "-"*5)
        print(f"[DEBUG] A verificar existência de {self.state_file}")
        if os.path.isfile(self.state_file):
            with open(self.state_file, 'r') as f:
                data = json.load(f)
            print(f"[DEBUG] Estado carregado: {data}")
            self.water = data.get('water', self.water_max)
            self.growth = data.get('growth', 0.0)
            self.alive = data.get('alive', True)
            self.critical_since = data.get('critical_since', None)
            last = data.get('last_timestamp', time.time())
            print(f"[DEBUG] Synchronizing with timestamp: {last}")
            self._sync(last)
        else:
            print(f"[DEBUG] Ficheiro não encontrado, inicializando valores padrão")
            self.water = self.water_max
            self.growth = 0.0
            self.alive = True
            self.critical_since = None
            self.last_timestamp = time.time()
            print(f"[DEBUG] Salvando estado inicial em {self.state_file}")
            self._save_state()
        print("-"*5 + " [DEBUG] FIM _load_state " + "-"*5 + "\n")

    def _simulate_environment(self, t):
        print("\n" + "~"*5 + " [DEBUG] INÍCIO _simulate_environment " + "~"*5)
        day_seconds = 24 * 3600
        phase = (t % day_seconds) / day_seconds * 2 * math.pi
        temp = (float(self.temp_max) + float(self.temp_min)) / 2 \
               + (float(self.temp_max) - float(self.temp_min)) / 2 * math.sin(phase)
        hum  = (float(self.hum_max) + float(self.hum_min)) / 2 \
               + (float(self.hum_max) - float(self.hum_min)) / 2 * math.sin(phase + math.pi)
        lum  = (float(self.lum_max) + float(self.lum_min)) / 2 \
               + (float(self.lum_max) - float(self.lum_min)) / 2 * max(0, math.sin(phase))
        print(f"[DEBUG] t={t:.2f} → Temp={temp:.2f}, Hum={hum:.2f}, Lum={lum:.2f}")
        print("~"*5 + " [DEBUG] FIM _simulate_environment " + "~"*5 + "\n")
        return temp, hum, lum

    def _sync(self, last_timestamp=None):
        print("\n" + "*"*5 + " [DEBUG] INÍCIO _sync " + "*"*5)
        now = time.time()
        last = last_timestamp or self.last_timestamp
        elapsed = now - last
        print(f"[DEBUG] Elapsed={elapsed:.2f}s since {last:.2f}")
        if not getattr(self, 'alive', True):
            print(f"[DEBUG] Planta morta, skip sync")
            self.last_timestamp = now
            print("*"*5 + " [DEBUG] FIM _sync " + "*"*5 + "\n")
            return

        temp, hum, _ = self._simulate_environment((now + last) / 2)
        evap_rate = 1 + max(0, temp - (float(self.temp_min) + float(self.temp_max)) / 2) * (1 - hum / 100)
        loss = elapsed * evap_rate
        self.water = max(0, self.water - loss)
        print(f"[DEBUG] Water após evaporação: {self.water:.2f}")

        if self.water < self.water_min:
            if self.critical_since is None:
                self.critical_since = now
                print(f"[DEBUG] Entrou em estado crítico")
            elif now - self.critical_since >= self.death_threshold:
                self.alive = False
                print(f"[DEBUG] Planta morreu após critério de morte")
        else:
            self.critical_since = None

        if self.alive and (
            self.water >= self.water_min and
            float(self.temp_min) <= temp <= float(self.temp_max) and
            float(self.hum_min)  <= hum  <= float(self.hum_max) and
            float(self.lum_min)  <= _    <= float(self.lum_max)
        ):
            self.growth = min(100.0, self.growth + 0.01 * elapsed)
            print(f"[DEBUG] Crescimento acumulado: {self.growth:.2f}%")

        self.last_timestamp = now
        self._save_state()
        print("*"*5 + " [DEBUG] FIM _sync " + "*"*5 + "\n")

    def _save_state(self):
        print("\n" + "+"*5 + " [DEBUG] INÍCIO _save_state " + "+"*5)
        data = {
            'water': self.water,
            'growth': self.growth,
            'alive': self.alive,
            'critical_since': self.critical_since,
            'last_timestamp': self.last_timestamp
        }
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"[DEBUG] Estado gravado: {data}")
        print("+"*5 + " [DEBUG] FIM _save_state " + "+"*5 + "\n")

    def water_plant(self, amount=None):
        print("\n" + "#"*5 + " [DEBUG] INÍCIO water_plant " + "#"*5)
        print(f"[DEBUG] Quantidade solicitada: {amount}")
        self._sync(None)
        if not self.alive:
            print(f"[{self.name}] morreu, não pode regar.")
            print("#"*5 + " [DEBUG] FIM water_plant " + "#"*5 + "\n")
            return
        add = amount if amount is not None else (self.water_max - self.water)
        self.water = min(self.water_max, self.water + add)
        self.critical_since = None
        self.last_timestamp = time.time()
        self._save_state()
        print(f"[{self.name}] Rega efetuada: água = {self.water:.1f}")
        print("#"*5 + " [DEBUG] FIM water_plant " + "#"*5 + "\n")

    def status(self):
        print("\n" + "@"*5 + " [DEBUG] INÍCIO status " + "@"*5)
        self._sync(None)
        temp, hum, lum = self._simulate_environment(self.last_timestamp)
        if not self.alive:
            print(f"[{self.name}] 💀 MORTA 💀")
            print("@"*5 + " [DEBUG] FIM status " + "@"*5 + "\n")
            return {'name': self.name, 'alive': False}
        alerts = []
        if self.water < self.water_min: alerts.append('Água baixa')
        if not (float(self.temp_min) <= temp <= float(self.temp_max)): alerts.append('Temperatura fora')
        if not (float(self.hum_min) <= hum <= float(self.hum_max)): alerts.append('Humidade fora')
        if not (float(self.lum_min) <= lum <= float(self.lum_max)): alerts.append('Luminosidade fora')
        state = 'OK' if not alerts else ', '.join(alerts)
        print(f"[{self.name}] Água={self.water:.1f}/{self.water_max} | "
              f"Temp={temp:.1f}°C | Hum={hum:.1f}% | Lux={lum:.0f} | "
              f"Crescimento={self.growth:.2f}% | Estado: {state}")
        print("@"*5 + " [DEBUG] FIM status " + "@"*5 + "\n")
        return {
            'name': self.name,
            'water': self.water,
            'temp': temp,
            'hum': hum,
            'lum': lum,
            'growth': self.growth
        }

def get_plant_from_vase_id(vase_id):
    print("\n" + "="*10 + " [DEBUG] INÍCIO get_plant_from_vase_id " + "="*10)
    print(f"[DEBUG] Vase ID: {vase_id}")
    cursor.execute("SELECT plantId FROM vases WHERE id = %s", (vase_id,))
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"[ERRO] Vaso com id {vase_id} não encontrado")
    plant_id = row[0]
    print(f"[DEBUG] Plant ID encontrado: {plant_id}")

    cursor.execute("""
        SELECT name, waterMin, waterMax, tempMin, tempMax,
               umidMin, umidMax, lumMin, lumMax
        FROM plants WHERE id = %s
    """, (plant_id,))
    plant_data = cursor.fetchone()
    if not plant_data:
        raise ValueError(f"[ERRO] Planta com id {plant_id} não encontrada")
    print(f"[DEBUG] Dados da planta encontrados: {plant_data}")
    print("="*10 + " [DEBUG] FIM get_plant_from_vase_id " + "="*10 + "\n")

    return Plant(
        name=plant_data[0],
        water_min=plant_data[1],
        water_max=plant_data[2],
        temp_min=plant_data[3],
        temp_max=plant_data[4],
        hum_min=plant_data[5],
        hum_max=plant_data[6],
        lum_min=plant_data[7],
        lum_max=plant_data[8],
        vase_id=vase_id
    )
