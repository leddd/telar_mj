import pygame
import pygame.gfxdraw
import random
import math
from pygame.math import Vector2

# Initialize Pygame
inga
pygame.init()

# Screen settings
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
        # Fade in/out alpha
        if pct < 0.25:
            alpha = int((pct / 0.25) * 255)
        elif pct > 0.75:
            alpha = int(((1 - pct) / 0.25) * 255)
        else:
            alpha = 255

        # Update animated points and draw curves
        for i in range(len(self.original_curves)):
            original = self.original_curves[i]
            animated = self.animated_curves[i]
            for j in range(4):
                animated[j].x = original[j].x + 5 * math.sin(math.radians(frame_count * 5 + self.idx * 20 + j * 50))
                animated[j].y = original[j].y + 5 * math.cos(math.radians(frame_count * 7 + self.idx * 15 + j * 30))

            points = [(p.x, p.y) for p in animated]
            draw_bezier(surface, points, alpha)

# Bezier drawing with antialiasing and alpha support
def draw_bezier(surface, points, alpha):
    # Create a transparent surface for antialiased drawing
    temp = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    # Compute interpolated points
    bezier_points = []
    for t in range(21):
        u = t / 20
        x = (1 - u)**3 * points[0][0] + 3 * (1 - u)**2 * u * points[1][0] + 3 * (1 - u) * u**2 * points[2][0] + u**3 * points[3][0]
        y = (1 - u)**3 * points[0][1] + 3 * (1 - u)**2 * u * points[1][1] + 3 * (1 - u) * u**2 * points[2][1] + u**3 * points[3][1]
        bezier_points.append((x, y))

    # Draw antialiased lines for each segment
    for i in range(len(bezier_points) - 1):
        x1, y1 = bezier_points[i]
        x2, y2 = bezier_points[i + 1]
        # Antialiased line with alpha
        pygame.gfxdraw.aaline(temp, int(x1), int(y1), int(x2), int(y2), (0, 0, 0, alpha))
        # Draw second line for thickness
        pygame.gfxdraw.aaline(temp, int(x1), int(y1) + 1, int(x2), int(y2) + 1, (0, 0, 0, alpha))

    # Blit the temp surface onto main surface
    surface.blit(temp, (0, 0))

# Initialize strokes
keystrokes = [KeyStroke(i) for i in range(NUM_KEYS)]

running = True
while running:
    screen.fill((255, 255, 255))
    frame_count += 1

    # Draw divider and labels
    pygame.draw.line(screen, (200, 200, 200), (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)
    screen.blit(font.render("Zona Izquierda", True, (150, 150, 150)), (WIDTH//4 - 50, 10))
    screen.blit(font.render("Zona Derecha", True, (150, 150, 150)), (3*WIDTH//4 - 50, 10))

    # Update and draw strokes
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
