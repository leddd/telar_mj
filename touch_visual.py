#!/usr/bin/env python3
import time, sys, busio, board, random
import pygame
import numpy as np
import termios, tty
from adafruit_mpr121 import MPR121
from pygame.locals import QUIT

# ——————————————————————————————————————————————————————————————
# 1) SENSOR SETUP (MPR121)
# ——————————————————————————————————————————————————————————————
I2C_ADDRESSES     = [0x5a, 0x5c]
ELECTRODES_PER_IC = 12
DEBOUNCE_THRESH   = 0.05  # seconds

# physical-to-logical mapping:
TOP_ROW    = [1, 3, 5, 7, 9, 11, 16, 13, 17, 18, 20]   # 11 pads
BOTTOM_ROW = [0, 2, 4, 6, 8, 10, 15, 12, 14, 21, 23, 22]  # 12 pads
RAW_INDICES = TOP_ROW + BOTTOM_ROW
REMAP = {
    16:13, 13:15, 18:19, 20:21,
    15:12, 12:14, 14:16, 21:18, 23:20,
}

def init_sensors():
    i2c = busio.I2C(board.SCL, board.SDA)
    sensors = []
    for addr in I2C_ADDRESSES:
        try:
            sensors.append(MPR121(i2c, address=addr))
        except Exception as e:
            print(f"Failed to init sensor {hex(addr)}: {e}")
    if not sensors:
        print("No MPR121 sensors found; exiting.")
        sys.exit(1)
    return sensors

def read_raw_touches(sensors):
    """Return list of raw electrode indices currently touched."""
    out = []
    for si, sensor in enumerate(sensors):
        base = si * ELECTRODES_PER_IC
        for i in range(ELECTRODES_PER_IC):
            if sensor[i].value:
                out.append(base + i)
    return out

# Debounce state
_last_raw    = {idx: False for idx in RAW_INDICES}
_last_change = {idx: time.time() for idx in RAW_INDICES}
_debounced   = {idx: False for idx in RAW_INDICES}


# ——————————————————————————————————————————————————————————————
# 2) AUDIO + GRAPHICS SETUP
# ——————————————————————————————————————————————————————————————
pygame.init()
screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Curvas Bézier Interactivas y Sonido Estéreo")
clock = pygame.time.Clock()
WHITE, BLACK = (255,255,255), (0,0,0)

def generar_sonido_estereo(freq_L, freq_R, dur):
    t = np.linspace(0, dur, int(44100*dur), endpoint=False)
    wave = np.stack((np.sin(2*np.pi*freq_L*t), np.sin(2*np.pi*freq_R*t)), axis=-1)
    snd = (wave * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(snd)

def bezier_cubic(p0,p1,p2,p3,steps=40):
    pts = []
    for i in range(steps+1):
        t = i/steps
        x = (1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3*p3[0]
        y = (1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3*p3[1]
        pts.append((x,y))
    return pts

class Letra:
    def __init__(self, idx):
        self.idx = idx
        self.base_x = (1000/24)*idx + 20
        self.base_y = 300
        self.duracion = 2.0
        self.start_time = None
        self.crear_anim()

    def crear_anim(self):
        self.trazos = []
        for _ in range(random.randint(1,4)):
            ampl = random.uniform(40,120)
            pts = [(random.uniform(-ampl,ampl), random.uniform(-ampl,ampl))
                   for _ in range(4)]
            self.trazos.append(pts)

    def activar(self):
        self.crear_anim()
        self.start_time = time.time()
        modo = random.choice(['simple','doble','barrido'])
        base = 220*(2**(self.idx/12))
        if modo=='simple':
            generar_sonido_estereo(base, base+2, 0.3).play()
        elif modo=='doble':
            generar_sonido_estereo(base, base+20, 0.4).play()
        else:
            for i in range(3):
                f1 = base*(1+0.05*i)
                generar_sonido_estereo(f1, f1+5, 0.2).play()
                time.sleep(0.1)

    def actualizar(self):
        if not self.start_time or time.time()-self.start_time > self.duracion:
            return
        for curva in self.trazos:
            pts = bezier_cubic(
                (self.base_x+curva[0][0], self.base_y+curva[0][1]),
                (self.base_x+curva[1][0], self.base_y+curva[1][1]),
                (self.base_x+curva[2][0], self.base_y+curva[2][1]),
                (self.base_x+curva[3][0], self.base_y+curva[3][1])
            )
            pygame.draw.aalines(screen, BLACK, False, pts)

# instantiate 24 letters
letras = [Letra(i) for i in range(24)]

# ——————————————————————————————————————————————————————————————
# 3) MAIN LOOP: POLL SENSORS + UPDATE SCREEN
# ——————————————————————————————————————————————————————————————
sensors = init_sensors()
print("Touch‐to‐play ready, press Ctrl+C to quit.")

try:
    while True:
        screen.fill(WHITE)
        # handle quit events
        for ev in pygame.event.get():
            if ev.type == QUIT:
                raise KeyboardInterrupt

        # Read and debounce raw touches
        now = time.time()
        raw = read_raw_touches(sensors)
        for idx in RAW_INDICES:
            touched = idx in raw
            if touched != _last_raw[idx]:
                _last_change[idx] = now
                _last_raw[idx] = touched

            if now - _last_change[idx] >= DEBOUNCE_THRESH:
                if touched and not _debounced[idx]:
                    _debounced[idx] = True
                    mapped = REMAP.get(idx, idx)
                    letras[mapped].activar()
                elif not touched and _debounced[idx]:
                    _debounced[idx] = False

        # draw all active animations
        for letra in letras:
            letra.actualizar()

        pygame.display.flip()
        clock.tick(60)

except KeyboardInterrupt:
    pass

finally:
    pygame.quit()
    print("Goodbye!")
