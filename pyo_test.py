import tkinter as tk
from pyo import *
import random

# Start server with small buffer to reduce latency
s = Server(duplex=0, buffersize=512).boot().start()

# Preload samples into memory
sample_paths = [
    "sound/S1.1.wav",
    "sound/S1.2.wav",
    "sound/S1.3.wav",
    "sound/S1.4.wav",
]
tables = [SndTable(path) for path in sample_paths]

# Key mapping
key_map = {
    'a': 0, 'w': 1, 's': 2, 'e': 3,
    'd': 4, 'f': 5, 't': 6, 'g': 7,
    'y': 8, 'h': 9, 'u': 10, 'j': 11
}

base_freq = 261.63

# Active readers for optional debugging (not needed for cleanup)
active_readers = []

def on_key(event):
    key = event.char.lower()
    if key in key_map:
        semitone = key_map[key]
        pitch = 2 ** (semitone / 12.0)
        table = random.choice(tables)
        pan_pos = semitone / 11.0

        freq = table.getRate() * pitch
        dur = table.getDur() / pitch

        # Create and play the TableRead
        reader = TableRead(table=table, freq=freq, loop=False, mul=0.1)
        panned = Pan(reader, pan=pan_pos).out()
        reader.play()

        # Automatically stop after sample ends
        def cleanup():
            reader.stop()
            panned.stop()
        CallAfter(cleanup, dur)

        active_readers.append(reader)

        print(f"Played: {table.getPath()} | pitch={pitch:.2f} | pan={pan_pos:.2f} | dur={dur:.2f}s")

# Tkinter GUI
root = tk.Tk()
root.title("12-note keyboard")
root.geometry("400x100")

label = tk.Label(root, text="Click here and press a–j / w,e,t,y,u", font=("Arial", 12))
label.pack(pady=20)

root.bind("<Key>", on_key)
root.after(10, lambda: None)

s.gui(locals())
