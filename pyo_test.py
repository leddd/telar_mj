from pyo import *
import random
import tkinter as tk

# 1) Boot server
s = Server(duplex=0).boot().start()

# 2) Sounds
sounds = [
    "sound/S1.1.wav",
    "sound/S1.2.wav",
    "sound/S1.3.wav",
    "sound/S1.4.wav",
]

# work here!!

import tkinter as tk

# 12-key mapping: A to J and W, E, T, Y, U for black keys
key_map = {
    'a': 0,
    'w': 1,
    's': 2,
    'e': 3,
    'd': 4,
    'f': 5,
    't': 6,
    'g': 7,
    'y': 8,
    'h': 9,
    'u': 10,
    'j': 11
}

base_freq = 261.63  # C4

def on_key(event):
    key = event.char.lower()
    if key in key_map:
        semitone = key_map[key]
        pitch = 2 ** (semitone / 12)
        sample = random.choice(sounds)
        SfPlayer(sample, speed=pitch, loop=False, mul=0.5).out()

# Simple Tkinter window
root = tk.Tk()
root.title("12-note Keyboard")
root.geometry("300x100")
label = tk.Label(root, text="Click here and press A–J / W–U keys")
label.pack(pady=30)

root.bind("<Key>", on_key)

# Prevent GUI lockup
root.after(10, lambda: None)

# Start pyo GUI and tkinter
s.gui(locals())
