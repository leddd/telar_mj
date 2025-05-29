from pyo import *

s = Server(duplex=0).boot()

path = SNDS_PATH + "/sound/S1.1.wav"

# stereo playback with a slight shift between the two channels.
sf = SfPlayer(path, speed=[1, 0.995], loop=True, mul=0.4).out()

s.gui(locals())