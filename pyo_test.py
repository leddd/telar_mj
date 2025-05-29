from pyo import *

# 1. Start the server (output only)
s = Server(audio="alsa", duplex=0, buffersize=256).boot()

path = "sound/S1.1.wav" 

# Loads the sound file in RAM. Beginning and ending points
# can be controlled with "start" and "stop" arguments.
t = SndTable(path)

# Gets the frequency relative to the table length.
freq = t.getRate()

# Simple stereo looping playback (right channel is 180 degrees out-of-phase).
osc = Osc(table=t, freq=freq, phase=[0, 0.5], mul=0.4).out()

# 3. Enter the GUI loop
s.gui(locals())
