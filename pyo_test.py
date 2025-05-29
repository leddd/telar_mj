import tkinter as tk
from pyo import *
import random

# Server
s = Server(duplex=0, buffersize=512).boot().start()

# Preload samples
sample_paths = [
    "sound/S1.1.wav",
    "sound/S1.2.wav",
    "sound/S1.3.wav",
    "sound/S1.4.wav",
]
tables = [SndTable(path) for path in sample_paths]

# Keyboard mapping
key_map = {
    'a': 0, 'w': 1, 's': 2, 'e': 3,
    'd': 4, 'f': 5, 't': 6, 'g': 7,
    'y': 8, 'h': 9, 'u': 10, 'j': 11
}

base_freq = 261.63

def on_key(event):
    key = event.char.lower()
    if key in key_map:
        semitone = key_map[key]
        pitch = 2 ** (semitone / 12.0)
        table = random.choice(tables)
        pan_pos = semitone / 11.0

        # Trigger
        trig = Trig()
        dur = table.getDur() / pitch
        env = TrigEnv(trig, table=table, dur=dur, mul=0.1)
        panned = Pan(env, outs=2, pan=pan_pos).out()

        trig.play()  # fire

        print(f"Played: pitch={pitch:.2f}, pan={pan_pos:.2f}")

# UI
root = tk.Tk()
root.title("12-note keyboard")
root.geometry("400x100")
label = tk.Label(root, text="Click here and press a–j / w,e,t,y,u to play", font=("Arial", 12))
label.pack(pady=20)
root.bind("<Key>", on_key)
root.after(10, lambda: None)

s.gui(locals())
