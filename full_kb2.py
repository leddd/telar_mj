import pygame
import math
import random
import sys
import time
from datetime import datetime
from pyo import Server, SndTable, TableRead, Pan, CallAfter

# Setup Pyo server
s = Server(duplex=0, buffersize=1024).boot().start()

# Preload samples
sample_paths = [
    "sound/S1.1.wav",
    "sound/S1.2.wav",
    "sound/S1.3.wav",
    "sound/S1.4.wav",
]
tables = [SndTable(path) for path in sample_paths]

# Audio configuration
max_polyphony = 6
active_voices = []

# Fade configuration for visuals
debounce_threshold = 0.05  # seconds for debounce
fade_time = 0.1  # portion of animation duration used for fade

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

# Event log
event_log = []

def log_event(message):
    timestamp = datetime.now().isoformat()
    entry = f"{timestamp} - {message}"
    event_log.append(entry)
    print(entry)

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
        for _ in range(3):
            ampl = random.uniform(40, 120)
            curve = [[
                self.base_pos[0] + random.uniform(-ampl, ampl),
                self.base_pos[1] + random.uniform(-ampl, ampl)
            ] for _ in range(4)]
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
        for i, original in enumerate(self.original_curves):
            animated = self.animated_curves[i]
            for j, (ox, oy) in enumerate(original):
                dx = 5 * math.sin(math.radians(frame * 5 + self.idx * 20 + j * 50))
                dy = 5 * math.cos(math.radians(frame * 7 + self.idx * 15 + j * 30))
                animated[j][0] = ox + dx
                animated[j][1] = oy + dy
            points = bezier_curve(*animated)
            for dx, dy in [(-0.33, -0.33), (0.33, 0.33), (0, 0)]:
                shifted = [(x+dx, y+dy) for x,y in points]
                pygame.draw.aalines(surface, color, False, shifted)

# Initialize states
debounce_raw = {i: False for i in range(NUM_KEYS)}
debounce_state = {i: False for i in range(NUM_KEYS)}
last_change = {i: time.time() for i in range(NUM_KEYS)}
activation_time = {}
keystrokes = [KeyStroke(i) for i in range(NUM_KEYS)]
frame_count = 0

# Main loop
log_event("Starting combined visual-audio session")
try:
    running = True
    while running:
        now = time.time()
        screen.fill((255,255,255))
        pygame.draw.line(screen, (200,200,200), (WIDTH//2,0), (WIDTH//2,HEIGHT), 2)
        font = pygame.font.SysFont(None,24)
        screen.blit(font.render("Zona Izquierda", True, (150,150,150)), (WIDTH//4 - 60,20))
        screen.blit(font.render("Zona Derecha", True, (150,150,150)), (3*WIDTH//4 - 60,20))
        for k in keystrokes:
            k.update(frame_count, screen)
        pygame.display.flip()
        clock.tick(FPS)
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                key_char = pygame.key.name(event.key)
                if key_char in key_map:
                    idx = key_map[key_char]
                    touched = (event.type == pygame.KEYDOWN)
                    if touched != debounce_raw[idx]:
                        last_change[idx] = now
                        debounce_raw[idx] = touched

        # Debounce logic
        for idx in range(NUM_KEYS):
            if (now - last_change[idx]) >= debounce_threshold:
                if debounce_raw[idx] and not debounce_state[idx]:
                    debounce_state[idx] = True
                    activation_time[idx] = now
                    keystrokes[idx].activate(frame_count)
                    # audio trigger
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
                        old_r, old_p = active_voices.pop(0)
                        old_r.stop(); old_p.stop()
                    active_voices.append((reader, panned))
                    CallAfter(lambda r=reader, p=panned: (active_voices.remove((r,p)) if (r,p) in active_voices else None, r.stop(), p.stop()), dur)
                    log_event(f"Touch activated on key {idx}")
                elif not debounce_raw[idx] and debounce_state[idx]:
                    debounce_state[idx] = False
                    hold = now - activation_time.get(idx, now)
                    log_event(f"Touch deactivated on key {idx} after {hold:.3f}s hold")
except KeyboardInterrupt:
    log_event("Session interrupted by user")
finally:
    # Cleanup
    pygame.quit()
    s.stop()
    # Save log to file
    log_file = "session_log.txt"
    with open(log_file, "w") as f:
        f.write("\n".join(event_log))
    print(f"Event log saved to {log_file}")
    sys.exit()
