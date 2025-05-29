import tkinter as tk
from pyo import *
import random

# Server boot
s = Server(duplex=0).boot().start()

sounds = [
    "sound/S1.1.wav",
    "sound/S1.2.wav",
    "sound/S1.3.wav",
    "sound/S1.4.wav",
]

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
        sound = random.choice(sounds)
        SfPlayer(sound, speed=pitch, loop=False, mul=0.5).out()
        print(f"Played: {sound} at semitone {semitone} (pitch={pitch:.2f})")

# Tkinter window
root = tk.Tk()
root.title("12-note keyboard")
root.geometry("400x100")

label = tk.Label(root, text="Click here and press a–j / w,e,t,y,u to play", font=("Arial", 12))
label.pack(pady=20)

# Bind keypress
root.bind("<Key>", on_key)

# Start GUI
root.after(10, lambda: None)
s.gui(locals())
