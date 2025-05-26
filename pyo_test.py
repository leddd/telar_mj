#!/usr/bin/env python3
import sys, tty, termios, time
from pyo import Server, Sine

def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

# Map computer keys to frequencies
key_map = {
    'a': 261.63,  # C4
    's': 293.66,  # D4
    'd': 329.63,  # E4
    'f': 349.23,  # F4
    'g': 392.00,  # G4
    'h': 440.00,  # A4
    'j': 493.88,  # B4
    'k': 523.25,  # C5
}

# Boot pyo for ALSA output-only with a smoother buffer
s = Server(
    audio     = 'alsa',
    duplex    = 0,
    nchnls    = 2,
    sr        = 44100,   # use “sr” instead of “samplerate”
    buffersize= 1024,
    latency   = 0.05
).boot()
s.start()

sine = Sine(freq=440, mul=0).out()
print("Press a–k for notes, q to quit.")

try:
    while True:
        ch = getch()
        if ch == 'q':
            break
        if ch in key_map:
            sine.setFreq(key_map[ch])
            sine.mul = 0.1
            time.sleep(0.5)
            sine.mul = 0
finally:
    # Properly stop & shutdown to avoid destructor errors
    s.stop()
    s.shutdown()
    print("\nGoodbye!")
