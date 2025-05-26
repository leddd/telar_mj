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

# Boot with a larger buffer and explicit samplerate
s = Server(
    audio     = 'alsa',
    duplex    = 0,          # output only
    nchnls    = 2,
    samplerate= 44100,      # lock to 44.1 kHz
    buffersize= 1024,       # larger buffer to smooth glitches
    latency   = 0.05        # in seconds; you can bump to 0.1 if needed
).boot()
s.start()

sine = Sine(freq=440, mul=0).out()
print("Press a–k for notes, q to quit.")
try:
    while True:
        ch = getch()
        if ch=='q': break
        if ch in key_map:
            sine.setFreq(key_map[ch])
            sine.mul = 0.1
            time.sleep(0.5)
            sine.mul = 0
finally:
    s.stop(); s.shutdown()
