import pygame
import math
import random
import sys
import time
import os
from datetime import datetime
from pathlib import Path
from pyo import Server, SndTable, SfPlayer, TableRead, Pan, CallAfter
import busio
import board
import adafruit_mpr121

# === Sensor Configuration ===
i2c_addresses = [0x5a, 0x5c]
electrodes_per_sensor = 12
debounce_threshold = 0.05

top_row = [1, 3, 5, 7, 9, 11, 16, 13, 17, 18, 20]
bottom_row = [0, 2, 4, 6, 8, 10, 15, 12, 14, 21, 23, 22]
electrode_indices = top_row + bottom_row

remap = {
    16: 13,
    13: 15,
    18: 19,
    20: 21,
    15: 12,
    12: 14,
    14: 16,
    21: 18,
    23: 20,
}

def initialize_sensors(addresses):
    sensors = []
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        for addr in addresses:
            try:
                sensors.append(adafruit_mpr121.MPR121(i2c, address=addr))
            except Exception as e:
                print(f"Warning: Failed to init sensor at {hex(addr)}: {e}")
    except Exception as e:
        print(f"Warning: I2C initialization failed: {e}")
    return sensors

def get_touched(sensors):
    touched = []
    for si, sensor in enumerate(sensors):
        base = si * electrodes_per_sensor
        try:
            for i in range(electrodes_per_sensor):
                if sensor[i].value:
                    touched.append(base + i)
        except Exception as e:
            print(f"Warning: Sensor read error at index {si}: {e}")
    return touched

# === Audio Configuration ===
master_volume = 2
volume_curve = 0.8  # 0.0 = flat, 1.0 = max curve

s = Server(duplex=0, buffersize=1024).boot().start()
s.setAmp(master_volume)

sample_paths = [
    "sound/S1.1.wav",
    "sound/S1.2.wav",
    "sound/S1.3.wav",
    "sound/S1.4.wav",
]
tables = [SndTable(path) for path in sample_paths]

ambience_path = "sound/FX.wav"
ambience_volume = 0.05
ambience_player = SfPlayer(
    ambience_path, loop=True, mul=ambience_volume * master_volume
).out()

max_polyphony = 6
active_voices = []

time_format = "%Y-%m-%dT%H:%M:%S"
fade_time = 0.1

transpose_semitones = 0
pitch_range = 40
root_pitch_factor = 1.0
pitch_randomness = 0.4

# === Logging ===
desktop = Path.home() / "Desktop"
desktop.mkdir(exist_ok=True)
base_name = "session_log"
ext = ".txt"

def open_new_log_file():
    i = 0
    while True:
        name = f"{base_name}{'' if i == 0 else f'_{i}'}{ext}"
        log_path = desktop / name
        if not log_path.exists():
            break
        i += 1
    return open(log_path, "a"), log_path

log_file, log_path = open_new_log_file()
log_file_start_time = time.time()

def log_event(message):
    timestamp = datetime.now().strftime(time_format)
    entry = f"{timestamp} - {message}\n"
    log_file.write(entry)
    log_file.flush()

# === Pygame Setup ===
os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'

pygame.init()
pygame.mouse.set_visible(False)  # Hide the mouse cursor

WIDTH, HEIGHT = 2048, 768  # Two screens, each 1024 wide
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Bezier Key Visualizer with Sensor Audio")
clock = pygame.time.Clock()

def bezier_curve(p0, p1, p2, p3, steps=30):
    return [
        (
            (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0],
            (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1],
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
            ampl = random.uniform(80, 240)
            curve = [[self.base_pos[0] + random.uniform(-ampl, ampl), self.base_pos[1] + random.uniform(-ampl, ampl)] for _ in range(4)]
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

        # Use fade_time as the fraction of the animation for fade-in and fade-out
        if pct < fade_time:
            fade = int(255 * (pct / fade_time))
        elif pct > 1 - fade_time:
            fade = int(255 * ((1 - pct) / fade_time))
        else:
            fade = 255
        fade = max(0, min(255, fade))  # Clamp to [0, 255]
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
                shifted = [(x + dx, y + dy) for x, y in points]
                pygame.draw.lines(surface, color, False, shifted, 4)

# === Key and Sensor Logic ===
NUM_KEYS = 23
keystrokes = [KeyStroke(i) for i in range(NUM_KEYS)]
last_raw = {idx: False for idx in electrode_indices}
debounced = {idx: False for idx in electrode_indices}
last_change = {idx: time.time() for idx in electrode_indices}
activation_time = {}

sensors = initialize_sensors(i2c_addresses)
if not sensors:
    print("Warning: No sensors initialized; continuing without touch input.")

frame_count = 0
session_start = time.time()
log_event("Starting session")

try:
    running = True
    while running:
        now = time.time()

        # Check if 30 minutes have passed since the current log file was opened
        if now - log_file_start_time >= 1800:
            log_event("30 minutes passed, rotating log file.")
            log_file.close()
            log_file, log_path = open_new_log_file()
            log_file_start_time = now
            log_event("Started new log file.")

        screen.fill((0, 0, 0))  # Black background
        for k in keystrokes:
            k.update(frame_count, screen)
        pygame.display.flip()
        clock.tick(FPS)
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        raw_touches = []
        if sensors:
            try:
                raw_touches = get_touched(sensors)
            except Exception as e:
                print(f"Warning: Failed to get touches: {e}")
                raw_touches = []

        for raw_idx in electrode_indices:
            try:
                touched = raw_idx in raw_touches
                if touched != last_raw[raw_idx]:
                    last_change[raw_idx] = now
                    last_raw[raw_idx] = touched

                if (now - last_change[raw_idx]) >= debounce_threshold:
                    disp_idx = remap.get(raw_idx, raw_idx)
                    if touched and not debounced[raw_idx]:
                        debounced[raw_idx] = True
                        activation_time[raw_idx] = now

                        if 0 <= disp_idx < NUM_KEYS:
                            keystrokes[disp_idx].activate(frame_count)
                            table = random.choice(tables)
                            pitch_step = pitch_range / (NUM_KEYS - 1)
                            base_pitch = disp_idx * pitch_step + transpose_semitones
                            variation = random.uniform(-1, 1) * pitch_randomness
                            pitch_shift = base_pitch + variation
                            pitch_factor = 2 ** (pitch_shift / 12.0)
                            freq = table.getRate() * pitch_factor
                            dur = table.getDur() / pitch_factor
                            pan_pos = disp_idx / (NUM_KEYS - 1) * 2 - 1

                            # Volume curve: low notes quieter, high notes louder, controlled by volume_curve
                            base_vol = 0.1
                            note_volume = base_vol * (1 + volume_curve * (disp_idx / (NUM_KEYS - 1) - 0.5) * 2)

                            reader = TableRead(table=table, freq=freq, loop=False, mul=note_volume * master_volume)
                            panned = Pan(reader, pan=pan_pos).out()
                            reader.play()

                            if len(active_voices) >= max_polyphony:
                                old_r, old_p = active_voices.pop(0)
                                old_r.stop()
                                old_p.stop()
                            active_voices.append((reader, panned))

                            CallAfter(
                                lambda r=reader, p=panned: (
                                    active_voices.remove((r, p)) if (r, p) in active_voices else None,
                                    r.stop(),
                                    p.stop(),
                                ),
                                dur,
                            )
                            log_event(f"Activated key {disp_idx}")

                    elif not touched and debounced[raw_idx]:
                        debounced[raw_idx] = False
                        hold = now - activation_time.get(raw_idx, now)
                        print(f"Touch deactivated on electrode {disp_idx} after {hold:.3f}s hold")
                        log_event(f"Deactivated key {disp_idx} after {hold:.3f}s")

            except Exception as e:
                print(f"Warning: Sensor processing error on electrode {raw_idx}: {e}")

        time.sleep(0.01)

except KeyboardInterrupt:
    log_event("Interrupted by user")
finally:
    pygame.quit()
    s.stop()
    total = time.time() - session_start
    hrs, rem = divmod(total, 3600)
    mins, secs = divmod(rem, 60)
    log_event(f"Session ended after {int(hrs)}h{int(mins)}m{int(secs)}s, log saved to {log_path}")
    log_file.close()
    sys.exit()
