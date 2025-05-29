import pygame
import numpy as np
import random
import time

pygame.init()
screen_width, screen_height = 1000, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Curvas Bézier Interactivas')
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
clock = pygame.time.Clock()

# Curva Bézier cúbica
def bezier_cubic(p0, p1, p2, p3, steps=40):
    points = []
    for t in [i / steps for i in range(steps + 1)]:
        x = (1 - t)**3 * p0[0] + 3*(1 - t)**2 * t * p1[0] + 3*(1 - t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1 - t)**3 * p0[1] + 3*(1 - t)**2 * t * p1[1] + 3*(1 - t) * t**2 * p2[1] + t**3 * p3[1]
        points.append((x, y))
    return points

# Clase Letra
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
        num_trazos = random.randint(1, 4)  # Número de trazos
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

# Crear letras (24 teclas)
letras = [Letra(i) for i in range(24)]
key_map = {pygame.K_1 + i: i for i in range(9)}
key_map.update({pygame.K_a + i: 9 + i for i in range(12)})
key_map.update({pygame.K_z + i: 21 + i for i in range(3)})

# Bucle principal
running = True
while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in key_map:
                letras[key_map[event.key]].activar()
    
    for letra in letras:
        letra.actualizar()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
