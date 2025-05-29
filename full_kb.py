
import pygame
import math
import random
import sys
from pyo import *

# Setup audio
s = Server(duplex=0).boot().start()
sounds = [
    "sound/S1.1.wav",
    "sound/S1.2.wav",
    "sound/S1.3.wav",
    "sound/S1.4.wav",
]
KEYS = ['a','w','s','e','d','f','t','g','y','h','u','j']
NUM_KEYS = len(KEYS)
base_freq = 261.63

# Setup visuals
pygame.init()
WIDTH, HEIGHT = 1000, 600
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Audio + Visual Keyboard")
clock = pygame.time.Clock()
fade_time = 0.25

def bezier_curve(p0, p1, p2, p3, steps=30):
    return [
        (
            (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0],
            (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1]
        )
        for t in [i / steps for i in range(steps + 1)]
    ]

class KeyStroke:
    def __init__(self, idx):
        self.idx = idx
        self.duration = FPS * 2
        self.start_frame = -self.duration
        self.original_curves = []
        self.animated_curves = []
        base_x = (idx / (NUM_KEYS - 1)) * (WIDTH - 40) + 20
        base_y = HEIGHT // 2
        self.base_pos = (base_x, base_y)

    def generate_curves(self):
        self.original_curves.clear()
        self.animated_curves.clear()
        for _ in range(3):
            ampl = random.uniform(40, 120)
            curve = []
            for _ in range(4):
                x = self.base_pos[0] + random.uniform(-ampl, ampl)
                y = self.base_pos[1] + random.uniform(-ampl, ampl)
                curve.append([x, y])
            self.original_curves.append(curve)
            self.animated_curves.append([p.copy() for p in curve])

    def activate(self, frame):
        self.generate_curves()
        self.start_frame = frame

    def update(self, frame, surface):
        frames_passed = frame - self.start_frame
        if frames_passed < 0 or frames_passed > self.duration:
            return
        pct = frames_passed / self.duration
        if pct < fade_time:
            fade = int(255 * (1 - (pct / fade_time)))
        elif pct > 1 - fade_time:
            fade = int(255 * ((pct - (1 - fade_time)) / fade_time))
        else:
            fade = 0
        color = (fade, fade, fade)
        for i in range(len(self.original_curves)):
            original = self.original_curves[i]
            animated = self.animated_curves[i]
            for j in range(4):
                ox, oy = original[j]
                dx = 5 * math.sin(math.radians(frame * 5 + self.idx * 20 + j * 50))
                dy = 5 * math.cos(math.radians(frame * 7 + self.idx * 15 + j * 30))
                animated[j][0] = ox + dx
                animated[j][1] = oy + dy
            bezier_points = bezier_curve(*animated)
            offsets = [(-0.33, -0.33), (0.33, 0.33), (0, 0)]
            for dx, dy in offsets:
                shifted = [(x + dx, y + dy) for (x, y) in bezier_points]
                pygame.draw.aalines(surface, color, False, shifted)

keystrokes = [KeyStroke(i) for i in range(NUM_KEYS)]
frame_count = 0

running = True
while running:
    screen.fill((255, 255, 255))
    pygame.draw.line(screen, (200, 200, 200), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 2)
    font = pygame.font.SysFont(None, 24)
    label_left = font.render("Zona Izquierda", True, (150, 150, 150))
    label_right = font.render("Zona Derecha", True, (150, 150, 150))
    screen.blit(label_left, (WIDTH // 4 - label_left.get_width() // 2, 20))
    screen.blit(label_right, (3 * WIDTH // 4 - label_right.get_width() // 2, 20))
    for k in keystrokes:
        k.update(frame_count, screen)
    pygame.display.flip()
    clock.tick(FPS)
    frame_count += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            key_char = pygame.key.name(event.key)
            if key_char in KEYS:
                idx = KEYS.index(key_char)
                keystrokes[idx].activate(frame_count)
                semitone = idx
                pitch = 2 ** (semitone / 12.0)
                sound = random.choice(sounds)
                pan = (idx / (NUM_KEYS - 1)) * 2 - 1
                SfPlayer(sound, speed=pitch, loop=False, mul=0.1).mix(2).out(chnl=[0 if pan < 0 else 1])
pygame.quit()
s.stop()
sys.exit()
