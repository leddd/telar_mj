import random
from pyo import Server, SfPlayer, Metro, TrigFunc

# 1) Boot & start server (output only)
s = Server(audio="alsa", duplex=0).boot().start()

# 2) List of your four samples
sounds = [
    "sound/S1.1.wav",
    "sound/S1.2.wav",
    "sound/S1.3.wav",
    "sound/S1.4.wav",
]

# 3) Define a play-once function
def play_random():
    path = random.choice(sounds)
    # loop=False so it only plays once
    SfPlayer(path, speed=1.5, loop=False, mul=0.4).out()

# 4) Demo trigger: a 1 Hz metronome
metro = Metro(time=1.0).play()
TrigFunc(metro, play_random)

# 5) (Or instead of Metro, call play_random() in your touch-sensor callback)

# 6) Keep GUI alive if you want pyo’s console
s.gui(locals())
