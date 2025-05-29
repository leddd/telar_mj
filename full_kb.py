import pygame
import math
import random
import sys
from pyo import Server, SndTable, TableRead, Pan, CallAfter

# Setup Pyo server
s = Server(duplex=0, buffersize=512).boot().start()

# Preload samples
sample_paths = [
    "sound/S1.1.wav",
    "sound/S1.2.wav",
    "sound/S1.3.wav",
    "sound/S1.4.wav",
]
tables = [SndTable(path) for path in sample_paths]

# Audio configuration
base_freq = 261.63
max_polyphony = 6
active_voices = []

# Fade configuration for visuals
fade_time = 0.1  # portion of animation duration used for fade (0.0 to 0.5)

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 1000, 600
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bezier Key Visualizer with Audio")
clock = pygame.time.Clock()

# Key mapping
KEYS = ['a','w','s','e','d','f','t','g','y','h','u','j']
key_map = {k: i for i, k in enumerate(KEYS)}
NUM_KEYS = len(KEYS)

# Bézier interpolation
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
        self.duration = FPS * 2  # 2 seconds
        self.start_frame = -self.duration
        self.original_curves = []
        self.animated_curves = []

        base_x = (idx / (NUM_KEYS - 1)) * (WIDTH - 40) + 20
        base_y = HEIGHT // 2
        self.base_pos = (base_x, base_y)

    def generate_curves(self):
        self.original_curves.clear()
        self.animated_curves.clear()
        for _ in range(3):  # 3 curves per key
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

# Initialize visuals
keystrokes = [KeyStroke(i) for i in range(NUM_KEYS)]
frame_count = 0

# Main loop
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
            if key_char in key_map:
                idx = key_map[key_char]
                # Trigger visual
                keystrokes[idx].activate(frame_count)
                # Trigger audio
                table = random.choice(tables)
                semitone = idx
                pitch = 2 ** (semitone / 12.0)
                pan_pos = semitone / (NUM_KEYS - 1)
                freq = table.getRate() * pitch
                dur = table.getDur() / pitch

                reader = TableRead(table=table, freq=freq, loop=False, mul=0.1)
                panned = Pan(reader, pan=pan_pos).out()
                reader.play()

                if len(active_voices) >= max_polyphony:
                    oldest_reader, oldest_pan = active_voices.pop(0)
                    oldest_reader.stop()
                    oldest_pan.stop()

                active_voices.append((reader, panned))

                def cleanup():
                    if (reader, panned) in active_voices:
                        active_voices.remove((reader, panned))
                    reader.stop()
                    panned.stop()
                CallAfter(cleanup, dur)

                print(f"Played: {table.path} | pitch={pitch:.2f} | pan={pan_pos:.2f} | dur={dur:.2f}s")

pygame.quit()
s.stop()
sys.exit()
