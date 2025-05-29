from pyo import *
import random

# 1) Boot server (output-only).
s = Server(duplex=0).boot().start()

sounds = [
    "sound/S1.1.wav",
    "sound/S1.2.wav",
    "sound/S1.3.wav",
    "sound/S1.4.wav",
]

def random_sound():
    return random.choice(sounds)

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
        SfPlayer(random_sound(), speed=pitch_factor, loop=False, mul=0.4).out()

# 3. Enter the GUI loop
s.gui(locals())
