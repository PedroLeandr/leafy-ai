import os
import json
import time
import math

class Plant:
    def __init__(self, name,
                 water_min, water_max,
                 temp_min, temp_max,
                 hum_min,  hum_max,
                 lum_min,  lum_max,
                 state_dir='sim-plant\states',
                 death_threshold=60):  # segundos em estado crítico para morrer
        self.name = name
        self.water_min, self.water_max = water_min, water_max
        self.temp_min,  self.temp_max  = temp_min, temp_max
        self.hum_min,   self.hum_max   = hum_min, hum_max
        self.lum_min,   self.lum_max   = lum_min, lum_max
        self.death_threshold = death_threshold
        self.state_dir = state_dir
        os.makedirs(self.state_dir, exist_ok=True)
        self.state_file = os.path.join(self.state_dir, f"{self.name}.json")
        self._load_state()

    def _load_state(self):
        if os.path.isfile(self.state_file):
            with open(self.state_file, 'r') as f:
                data = json.load(f)
            self.water = data.get('water', self.water_max)
            self.growth = data.get('growth', 0.0)
            self.alive = data.get('alive', True)
            self.critical_since = data.get('critical_since', None)
            last = data.get('last_timestamp', time.time())
            self._sync(last)
        else:
            self.water = self.water_max
            self.growth = 0.0
            self.alive = True
            self.critical_since = None
            self.last_timestamp = time.time()

    def _simulate_environment(self, t):
        day_seconds = 24*3600
        phase = (t % day_seconds) / day_seconds * 2*math.pi

        temp_min = float(self.temp_min)
        temp_max = float(self.temp_max)
        hum_min = float(self.hum_min)
        hum_max = float(self.hum_max)
        lum_min = float(self.lum_min)
        lum_max = float(self.lum_max)

        temp = (temp_max + temp_min)/2 + (temp_max - temp_min)/2 * math.sin(phase)
        hum  = (hum_max + hum_min)/2 + (hum_max - hum_min)/2 * math.sin(phase + math.pi)
        lum  = (lum_max + lum_min)/2 + (lum_max - lum_min)/2 * max(0, math.sin(phase))
        return temp, hum, lum

    def _sync(self, last_timestamp=None):
        now = time.time()
        last = last_timestamp or self.last_timestamp
        elapsed = now - last
        if not getattr(self, 'alive', True):
            self.last_timestamp = now
            return

        temp, hum, _ = self._simulate_environment((now+last)/2)
        evap_rate = 1 + max(0, temp - (float(self.temp_min)+float(self.temp_max))/2) * (1 - hum/100)
        loss = elapsed * evap_rate
        self.water = max(0, self.water - loss)

        if self.water < self.water_min:
            if self.critical_since is None:
                self.critical_since = now
            elif now - self.critical_since >= self.death_threshold:
                self.alive = False
        else:
            self.critical_since = None

        if self.alive and (
            self.water >= self.water_min and
            float(self.temp_min) <= temp <= float(self.temp_max) and
            float(self.hum_min)  <= hum  <= float(self.hum_max) and
            float(self.lum_min)  <= _    <= float(self.lum_max)):
            self.growth = min(100.0, self.growth + 0.01 * elapsed)

        self.last_timestamp = now
        self._save_state()

    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump({
                'water': self.water,
                'growth': self.growth,
                'alive': self.alive,
                'critical_since': self.critical_since,
                'last_timestamp': self.last_timestamp
            }, f)

    def water_plant(self, amount=None):
        self._sync(None)
        if not self.alive:
            print(f"[{self.name}] morreu, não pode regar.")
            return
        add = amount if amount is not None else (self.water_max - self.water)
        self.water = min(self.water_max, self.water + add)
        self.critical_since = None
        self.last_timestamp = time.time()
        self._save_state()
        print(f"[{self.name}] Rega efetuada: água = {self.water:.1f}")

    def status(self):
        self._sync(None)
        temp, hum, lum = self._simulate_environment(self.last_timestamp)
        if not self.alive:
            print(f"[{self.name}] 💀 MORTA 💀")
            return {'name': self.name, 'alive': False}

        alerts = []
        if self.water < self.water_min: alerts.append('Água baixa')
        if not (float(self.temp_min) <= temp <= float(self.temp_max)): alerts.append('Temperatura fora')
        if not (float(self.hum_min) <= hum <= float(self.hum_max)): alerts.append('Humidade fora')
        if not (float(self.lum_min) <= lum <= float(self.lum_max)): alerts.append('Luminosidade fora')
        state = 'OK' if not alerts else ', '.join(alerts)
        status_str = (f"[{self.name}] Água={self.water:.1f}/{self.water_max} | "
                      f"Temp={temp:.1f}°C | Hum={hum:.1f}% | Lux={lum:.0f} | "
                      f"Crescimento={self.growth:.2f}% | Estado: {state}")
        print(status_str)
        return {'name': self.name, 'water': self.water, 'temp': temp, 'hum': hum, 'lum': lum, 'growth': self.growth}
