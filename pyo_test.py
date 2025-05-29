import tkinter as tk
from pyo import *
import random

# Start server
s = Server(duplex=0, buffersize=512).boot().start()

# Preload samples
sample_paths = [
    "sound/S1.1.wav",
    "sound/S1.2.wav",
    "sound/S1.3.wav",
    "sound/S1.4.wav",
]
tables = [(SndTable(path), path) for path in sample_paths]

# Key mapping
key_map = {
    'a': 0, 'w': 1, 's': 2, 'e': 3,
    'd': 4, 'f': 5, 't': 6, 'g': 7,
    'y': 8, 'h': 9, 'u': 10, 'j': 11
}

base_freq = 261.63
max_polyphony = 6
active_voices = []
pressed_keys = set()

def on_key_press(event):
    key = event.char.lower()
    if key not in key_map:
        return
    if key in pressed_keys:
        return  # debounce: ignore repeat press until released

    pressed_keys.add(key)

    semitone = key_map[key]
    pitch = 2 ** (semitone / 12.0)
    (table, path) = random.choice(tables)
    pan_pos = semitone / 11.0

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

    print(f"Played: {path} | pitch={pitch:.2f} | pan={pan_pos:.2f} | dur={dur:.2f}s")

def on_key_release(event):
    key = event.char.lower()
    pressed_keys.discard(key)  # allow key to be played again

# GUI
root = tk.Tk()
root.title("12-note keyboard")
root.geometry("400x100")

label = tk.Label(root, text="Click here and press a–j / w,e,t,y,u", font=("Arial", 12))
label.pack(pady=20)

root.bind("<KeyPress>", on_key_press)
root.bind("<KeyRelease>", on_key_release)
root.after(10, lambda: None)

s.gui(locals())
