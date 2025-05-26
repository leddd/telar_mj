#!/usr/bin/env python3
import sys, tty, termios, time
from pyo import Server, Sine

# Simple getch() for Linux terminal
def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch

# Map keys to frequencies (in Hz)
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

# Boot pyo server (ALSA, no input, stereo out)
s = Server(audio='alsa', duplex=0, nchnls=2).boot()
s.start()

# One sine oscillator whose freq and amp we’ll control
sine = Sine(freq=440, mul=0).out()

print("Press keys a-k for notes, q to quit.")
try:
    while True:
        ch = getch()
        if ch == 'q':
            break
        freq = key_map.get(ch)
        if freq:
            # play note for 0.5s
            sine.setFreq(freq)
            sine.mul = 0.1
            time.sleep(0.5)
            sine.mul = 0
        else:
            # ignore unrecognized keys
            continue
finally:
    s.stop()
    s.shutdown()
    print("\nGoodbye!")
