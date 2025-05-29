from pyo import *
import random
import math

# 1) Boot server
s = Server(duplex=0).boot().start()

# 2) List of sound files
sounds = [
    "sound/S1.1.wav",
    "sound/S1.2.wav",
    "sound/S1.3.wav",
    "sound/S1.4.wav",
]

# 3) Key-to-semitone mapping (A to L → 0 to 11)
# You can adjust this layout if you prefer different keys
key_map = {
    'a': 0,
    's': 1,
    'd': 2,
    'f': 3,
    'g': 4,
    'h': 5,
    'j': 6,
    'k': 7,
    'l': 8,
    ';': 9,
    "'": 10,
    'z': 11,  # optional 12th key
}

# 4) Key press callback
def play_note(evt):
    key = evt.key
    if key in key_map:
        semitone = key_map[key]
        pitch_factor = 2 ** (semitone / 12)  # convert semitone to speed ratio
        path = random.choice(sounds)
        SfPlayer(path, speed=pitch_factor, loop=False, mul=0.4).out()
        print(f"Key '{key.upper()}' → semitone {semitone} → {path}")

# 5) Bind to GUI
s.setMidiInputDevice(99)  # disables MIDI
s.setAmp(1)
s.gui(locals(), exitfunc=None)

# 6) Attach key press handler to the GUI
s.win.bind("<Key>", play_note)
