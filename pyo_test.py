from pyo import *
import random

# 1) Boot server
s = Server(duplex=0).boot().start()

# 2) Sounds
sounds = [
    "sound/S1.1.wav",
    "sound/S1.2.wav",
    "sound/S1.3.wav",
    "sound/S1.4.wav",
]

# 3) Key → semitone
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
    'z': 11,
}

# 4) Key callback
def play_note(evt):
    key = evt.char  # FIXED: use .char instead of .key
    if key in key_map:
        semitone = key_map[key]
        pitch = 2 ** (semitone / 12)
        SfPlayer(random.choice(sounds), speed=pitch, loop=False, mul=0.4).out()
        print(f"Pressed {key} → +{semitone} st → pitch factor {pitch:.2f}")

# 5) Start GUI and bind
s.gui(locals())
s.win.bind("<Key>", play_note)  # FIXED: must call this after s.gui()
