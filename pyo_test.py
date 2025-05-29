from pyo import *
s = Server(duplex=0).boot().start()

p = SfPlayer("sound/S1.1.wav", speed=1, loop=False).out()

s.gui(locals())