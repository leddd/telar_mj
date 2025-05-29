import tkinter as tk
from pyo import *
import random

# Boot server
s = Server(duplex=0).boot().start()

# 1. Preload all samples into SndTables
sample_paths = [
    "sound/S1.1.wav",
    "sound/S1.2.wav",
    "sound/S1.3.wav",
    "sound/S1.4.wav",
]
tables = [SndTable(path) for path in sample_paths]

# 2. Key-to-semitone mapping
key_map = {
    'a': 0, 'w': 1, 's': 2, 'e': 3,
    'd': 4, 'f': 5, 't': 6, 'g': 7,
    'y': 8, 'h': 9, 'u': 10, 'j': 11
}

base_freq = 261.63

# 3. Store current playing readers (optional, no GC leak risk here)
active_readers = []

def on_key(event):
    key = event.char.lower()
    if key in key_map:
        semitone = key_map[key]
        pitch_factor = 2 ** (semitone / 12.0)
        table = random.choice(tables)

        # Calculate playback rate
        rate = pitch_factor

        # Pan from left (0.0) to right (1.0)
        pan_pos = semitone / 11.0

        # Use TableRead for sample playback
        dur = table.getDur() / rate  # Adjust duration to match pitch speed
        reader = TableRead(table=table, freq=table.getRate() * rate, loop=False, mul=0.1)
        panned = Pan(reader, outs=2, pan=pan_pos).out()
        # Auto-stop reader after playback
        reader.play()

        active_readers.append(panned)  # Not strictly needed, just for reference

        print(f"Played: {random.choice(sample_paths)} | pitch={pitch_factor:.2f} | pan={pan_pos:.2f}")

# 4. Tkinter UI
root = tk.Tk()
root.title("12-note keyboard")
root.geometry("400x100")

label = tk.Label(root, text="Click here and press a–j / w,e,t,y,u to play", font=("Arial", 12))
label.pack(pady=20)

root.bind("<Key>", on_key)
root.after(10, lambda: None)

# 5. Start GUI and Pyo
s.gui(locals())
