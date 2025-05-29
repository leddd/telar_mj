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

# List to hold references to players (prevent GC)
active_players = []

# Dummy initial input (silence) to bootstrap the mix bus
silent = Noise(mul=0).stop()
mix_bus = silent

# Output stage: dynamic compression to prevent clipping
master = Compress(mix_bus, thresh=-6, ratio=4, risetime=0.01, falltime=0.2, knee=0.5, outputAmp=True).out()

def on_key(event):
    global mix_bus
    key = event.char.lower()
    if key in key_map:
        semitone = key_map[key]
        pitch = 2 ** (semitone / 12.0)
        sound = random.choice(sounds)
        player = SfPlayer(sound, speed=pitch, loop=False, mul=0.15)
        active_players.append(player)

        # Combine current mix with new player
        mix_bus = mix_bus + player
        master.setInput(mix_bus)

        print(f"Played: {sound} at pitch {pitch:.2f}")

# Simple Tkinter window
root = tk.Tk()
root.title("12-note keyboard")
root.geometry("400x100")

label = tk.Label(root, text="Click here and press a–j / w,e,t,y,u to play", font=("Arial", 12))
label.pack(pady=20)

root.bind("<Key>", on_key)
root.after(10, lambda: None)

# Start GUI and Pyo GUI
s.gui(locals())
