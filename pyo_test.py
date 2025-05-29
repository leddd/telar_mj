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


# 2) Play at 1.5× speed (≈ +7 semitones). Loop forever.
sf = SfPlayer(random_sound(),
              speed=1.5,    # 1.0 = original pitch; 2.0 = +1 octave
              loop=True,
              mul=0.4).out()
print(random_sound())

# 3. Enter the GUI loop
s.gui(locals())
