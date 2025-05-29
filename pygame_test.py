import pygame
import random
import math
from pygame.math import Vector2

pygame.init()

WIDTH, HEIGHT = 1000, 600
FPS = 60
NUM_KEYS = 12
KEYS = ['a','w','s','e','d','f','t','g','y','h','u','j']

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Visual Keyboard")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 16)

frame_count = 0

class KeyStroke:
    def __init__(self, idx):
        self.idx = idx
        self.duration = FPS * 2  # 2 seconds
        self.start_frame = -self.duration
        self.original_curves = []
        self.animated_curves = []

        base_x = ((idx / (NUM_KEYS - 1)) * (WIDTH - 40)) + 20
        base_y = HEIGHT // 2
        self.base_pos = Vector2(base_x, base_y)

    def generate_curves(self):
        self.original_curves.clear()
        self.animated_curves.clear()
        for _ in range(3):
            ampl = random.uniform(40, 120)
            base_curve = [self.base_pos + Vector2(random.uniform(-ampl, ampl), random.uniform(-ampl, ampl)) for _ in range(4)]
            self.original_curves.append(base_curve)
            self.animated_curves.append([pt.copy() for pt in base_curve])

    def activate(self):
        self.generate_curves()
        self.start_frame = frame_count

    def update(self, surface):
        frames_passed = frame_count - self.start_frame
        if frames_passed < 0 or frames_passed > self.duration:
            return

        pct = frames_passed / self.duration
        if pct < 0.25:
            alpha = int(pct / 0.25 * 255)
        elif pct > 0.75:
            alpha = int((1 - (pct - 0.75) / 0.25) * 255)
        else:
            alpha = 255

        for i in range(len(self.original_curves)):
            original = self.original_curves[i]
            animated = self.animated_curves[i]
            for j in range(4):
                animated[j].x = original[j].x + 5 * math.sin(math.radians(frame_count * 5 + self.idx * 20 + j * 50))
                animated[j].y = original[j].y + 5 * math.cos(math.radians(frame_count * 7 + self.idx * 15 + j * 30))

            points = [(p.x, p.y) for p in animated]
            draw_bezier(surface, points, alpha)

def draw_bezier(surface, points, alpha):
    # Approximate bezier with many points
    def bezier_interp(t):
        x = (1 - t)**3 * points[0][0] + 3 * (1 - t)**2 * t * points[1][0] + 3 * (1 - t) * t**2 * points[2][0] + t**3 * points[3][0]
        y = (1 - t)**3 * points[0][1] + 3 * (1 - t)**2 * t * points[1][1] + 3 * (1 - t) * t**2 * points[2][1] + t**3 * points[3][1]
        return (x, y)

    bezier_points = [bezier_interp(t / 20) for t in range(21)]
    for i in range(len(bezier_points) - 1):
        pygame.draw.line(surface, (0, 0, 0, alpha), bezier_points[i], bezier_points[i + 1], 2)

# Initialize keystrokes
keystrokes = [KeyStroke(i) for i in range(NUM_KEYS)]

running = True
while running:
    screen.fill((255, 255, 255))
    frame_count += 1

    pygame.draw.line(screen, (200, 200, 200), (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)
    screen.blit(font.render("Zona Izquierda", True, (150, 150, 150)), (WIDTH//4 - 50, 10))
    screen.blit(font.render("Zona Derecha", True, (150, 150, 150)), (3*WIDTH//4 - 50, 10))

    for stroke in keystrokes:
        stroke.update(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.unicode in KEYS:
                idx = KEYS.index(event.unicode)
                keystrokes[idx].activate()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
