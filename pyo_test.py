from pyo import *
import random

# Boot server
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

print("Press a key (a–j / w,e,t,y,u) and press Enter. Type 'q' to quit.")

while True:
    key = input("Key: ").lower()
    if key == 'q':
        break
    if key in key_map:
        semitone = key_map[key]
        pitch = 2 ** (semitone / 12)
        sample = random.choice(sounds)
        SfPlayer(sample, speed=pitch, loop=False, mul=0.5).out()
    else:
        print("Not mapped.")
