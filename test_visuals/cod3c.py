import pygame
import numpy as np
import random
import time
import sounddevice as sd

pygame.init()

# --- Configuración Pantalla ---
screen_width, screen_height = 1000, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Curvas Bézier Interactivas con Sonido')
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
clock = pygame.time.Clock()

# --- Parámetros audio ---
sample_rate = 44100

# --- Mapeo teclas a índice 0-23 (para curvas y tonos) ---
key_map = {}
# 1-9
for i in range(9):
    key_map[pygame.K_1 + i] = i
# a-l (12 teclas)
for i in range(12):
    key_map[pygame.K_a + i] = 9 + i
# z, x, c (3 teclas)
for i in range(3):
    key_map[pygame.K_z + i] = 21 + i

# --- Mapeo de frecuencias para 24 teclas (notas cromáticas, por ejemplo) ---
frequencies = [
    110, 116.54, 123.47, 130.81, 138.59, 146.83, 155.56, 164.81,
    174.61, 185.00, 196.00, 207.65, 220.00, 233.08, 246.94, 261.63,
    277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00, 415.30
]

# --- Clase para tonos ---
class ToneGenerator:
    def __init__(self, frequency):
        self.frequency = frequency
        self.phase = 0.0
        self.phase_increment = 2 * np.pi * frequency / sample_rate

    def generate(self, frames, active_count):
        t = (np.arange(frames) + self.phase) / sample_rate
        self.phase = (self.phase + frames) % sample_rate
        wave = np.sin(2 * np.pi * self.frequency * t)
        amplitude = 0.5 / active_count if active_count else 0.5
        return amplitude * wave

# --- Efectos ---
def apply_reverb(signal, delay_ms=80, decay=0.4):
    delay_samples = int(sample_rate * delay_ms / 1000)
    reverb_signal = np.copy(signal)
    for i in range(delay_samples, len(signal)):
        reverb_signal[i] += decay * signal[i - delay_samples]
    max_val = np.max(np.abs(reverb_signal))
    if max_val > 1:
        reverb_signal /= max_val
    return reverb_signal

def apply_echo(signal, delay_ms=200, decay=0.5):
    delay_samples = int(sample_rate * delay_ms / 1000)
    echo_signal = np.copy(signal)
    for i in range(delay_samples, len(signal)):
        echo_signal[i] += decay * signal[i - delay_samples]
    max_val = np.max(np.abs(echo_signal))
    if max_val > 1:
        echo_signal /= max_val
    return echo_signal

# --- Variables globales audio ---
active_tones = {}

# --- Callback para audio ---
def audio_callback(outdata, frames, time, status):
    if status:
        print(status)
    output = np.zeros(frames)
    active_items = list(active_tones.items())
    if len(active_items) > 3:
        active_items = active_items[:3]
    count = len(active_items) if active_items else 1
    for idx, gen in active_items:
        output += gen.generate(frames, count)
    output = apply_reverb(output)
    output = apply_echo(output)
    max_val = np.max(np.abs(output))
    if max_val > 1:
        output /= max_val
    outdata[:] = output.reshape(-1, 1)

# --- Inicializar stream ---
stream = sd.OutputStream(channels=1, callback=audio_callback,
                         samplerate=sample_rate, blocksize=1024)
stream.start()

# --- Curvas Bézier ---
def bezier_cubic(p0, p1, p2, p3, steps=40):
    points = []
    for t in [i / steps for i in range(steps + 1)]:
        x = (1 - t)**3 * p0[0] + 3*(1 - t)**2 * t * p1[0] + 3*(1 - t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1 - t)**3 * p0[1] + 3*(1 - t)**2 * t * p1[1] + 3*(1 - t) * t**2 * p2[1] + t**3 * p3[1]
        points.append((x, y))
    return points

class Letra:
    def __init__(self, idx):
        self.idx = idx
        self.trazos = []
        self.base_x = (screen_width / 24) * idx + 20
        self.base_y = screen_height / 2
        self.crear_animacion()
        self.start_time = None
        self.duracion_anim = 2

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

    def actualizar(self):
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

# Crear letras
letras = [Letra(i) for i in range(24)]

# --- Loop principal ---
running = True
while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key in key_map:
                idx = key_map[event.key]
                # Activar animación curva
                letras[idx].activar()
                # Agregar tono si no está activo
                if idx not in active_tones:
                    freq = frequencies[idx]
                    active_tones[idx] = ToneGenerator(freq)

        elif event.type == pygame.KEYUP:
            if event.key in key_map:
                idx = key_map[event.key]
                # Parar tono
                if idx in active_tones:
                    del active_tones[idx]

    for letra in letras:
        letra.actualizar()

    pygame.display.flip()
    clock.tick(60)

stream.stop()
stream.close()
pygame.quit()
