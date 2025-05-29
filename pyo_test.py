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

# work here!!

# 3) Mapping keys to semitone steps (C to B)
key_map = {
    'a': 0,   # C
    'w': 1,   # C#
    's': 2,   # D
    'e': 3,   # D#
    'd': 4,   # E
    'f': 5,   # F
    't': 6,   # F#
    'g': 7,   # G
    'y': 8,   # G#
    'h': 9,   # A
    'u': 10,  # A#
    'j': 11   # B
}

# 4) Base frequency and pitch calculation
base_freq = 261.63  # Middle C (C4)

# 5) Key press callback
def play_note(event):
    key = event.key
    if key in key_map:
        semitone = key_map[key]
        freq = base_freq * (2 ** (semitone / 12.0))
        snd_path = random.choice(sounds)
        sf = SfPlayer(snd_path, speed=freq/base_freq, loop=False, mul=0.5).out()

# 6) Bind key event
s.setCallback(play_note)

# GUI
s.gui(locals())
