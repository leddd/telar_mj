import pygame
import numpy as np
import random
import time
import sounddevice as sd
import board
import busio
import adafruit_mpr121

# --- Inicializar I2C ---
i2c = busio.I2C(board.SCL, board.SDA)

# Sensor derecho (dirección default 0x5A)
mpr121_right = adafruit_mpr121.MPR121(i2c, address=0x5A)

# Sensor izquierdo (cambia dirección I2C o bus, aquí ejemplo 0x5B)
mpr121_left = adafruit_mpr121.MPR121(i2c, address=0x5B)

# --- Configuración pantallas ---
pygame.init()
screen_width, screen_height = 800, 600  # Ajusta según resolución 11"
# Pantalla derecha - ventana principal
screen_right = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Pantalla Derecha')

# Para simplificar, ventana izquierda será una segunda ventana Pygame (si el sistema lo soporta)
# Si no, puedes dividir la ventana principal en dos áreas.
screen_left = pygame.Surface((screen_width, screen_height))  # renderizamos aquí y mostramos en main window si no hay segunda pantalla.

WHITE, BLACK = (255, 255, 255), (0, 0, 0)
clock = pygame.time.Clock()

# --- Configuración audio y funciones (igual que antes) ---
sample_rate = 44100

# Mapeo índices canales
# Derecho: 0-11 → indices 0-11
# Izquierdo: 0-1 → indices 12-13 (mapear separado)
frequencies = [110 + i*10 for i in range(24)]  # Ajusta frecuencias reales

# Clase y funciones ToneGenerator, efectos, audio_callback igual que el ejemplo anterior
# ...

# Activos de cada pantalla
active_tones_right = {}
active_tones_left = {}

# Letras por pantalla
class Letra:
    def __init__(self, idx, base_x, base_y):
        self.idx = idx
        self.base_x = base_x
        self.base_y = base_y
        self.trazos = []
        self.start_time = None
        self.duracion_anim = 2
        self.crear_animacion()
    
    def crear_animacion(self):
        self.trazos = []
        num_trazos = random.randint(1, 4)
        for _ in range(num_trazos):
            ampl = random.uniform(40, 120)
            curva = [
                (random.uniform(-ampl, ampl), random.uniform(-ampl, ampl)),
                (random.uniform(-ampl, ampl), random.uniform(-ampl, ampl)),
                (random.uniform(-ampl, ampl), random.uniform(-ampl, ampl)),
                (random.uniform(-ampl, ampl), random.uniform(-ampl, ampl))
            ]
            self.trazos.append(curva)
    
    def activar(self):
        self.crear_animacion()
        self.start_time = time.time()
    
    def actualizar(self, screen):
        if self.start_time is None or time.time() - self.start_time > self.duracion_anim:
            return
        for curva in self.trazos:
            puntos = bezier_cubic(
                (self.base_x + curva[0][0], self.base_y + curva[0][1]),
                (self.base_x + curva[1][0], self.base_y + curva[1][1]),
                (self.base_x + curva[2][0], self.base_y + curva[2][1]),
                (self.base_x + curva[3][0], self.base_y + curva[3][1])
            )
            pygame.draw.aalines(screen, BLACK, False, puntos)

# Crear letras para ambas pantallas
letras_right = [Letra(i, (screen_width / 12) * i + 20, screen_height / 2) for i in range(12)]
letras_left = [Letra(i, (screen_width / 2) + 20, screen_height / 2) for i in range(2)]

# Audio active tones combined:
active_tones = {}

# Audio callback igual, pero combinando tonos activos de ambos sensores
def audio_callback(outdata, frames, time, status):
    if status:
        print(status)
    output = np.zeros(frames)
    all_tones = list(active_tones.values())
    count = len(all_tones) if all_tones else 1
    for gen in all_tones[:3]:  # max 3 tonos simultaneos
        output += gen.generate(frames, count)
    output = apply_reverb(output)
    output = apply_echo(output)
    max_val = np.max(np.abs(output))
    if max_val > 1:
        output /= max_val
    outdata[:] = output.reshape(-1, 1)

# Iniciar audio
stream = sd.OutputStream(channels=1, callback=audio_callback,
                         samplerate=sample_rate, blocksize=1024)
stream.start()

def leer_mpr121(mpr121):
    return [mpr121[i].value for i in range(len(mpr121))]

running = True
while running:
    screen_right.fill(WHITE)
    screen_left.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Leer sensores
    estados_right = leer_mpr121(mpr121_right)  # 12 canales
    estados_left = leer_mpr121(mpr121_left)    # 2 canales

    # Actualizar letras y tonos derecha
    for i, activo in enumerate(estados_right):
        if activo and i not in active_tones:
            letras_right[i].activar()
            freq = frequencies[i]
            active_tones[i] = ToneGenerator(freq)
        elif not activo and i in active_tones:
            del active_tones[i]

    # Actualizar letras y tonos izquierda (usamos índices 12 y 13 para tonos)
    for i, activo in enumerate(estados_left):
        idx = 12 + i
        if activo and idx not in active_tones:
            letras_left[i].activar()
            freq = frequencies[idx]
            active_tones[idx] = ToneGenerator(freq)
        elif not activo and idx in active_tones:
            del active_tones[idx]

    # Dibujar letras
    for letra in letras_right:
        letra.actualizar(screen_right)

    for letra in letras_left:
        letra.actualizar(screen_left)

    # Mostrar pantallas (para dos ventanas reales, habría que inicializar 2 ventanas pygame)
    # Aquí mostramos las superficies para simplificar (ejemplo ventana única)
    screen.blit(screen_right, (0, 0))
    screen.blit(screen_left, (screen_width//2, 0))

    pygame.display.flip()
    clock.tick(60)

stream.stop()
stream.close()
pygame.quit()
