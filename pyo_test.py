from pyo import *

# 1. Start the server (output only)
s = Server(audio="alsa", duplex=0).boot()
s.start()

# 2. Use a simple relative path:
sf = SfPlayer("sound/S1.1.wav", speed=[1, 0.995], loop=True, mul=0.4).out()

# 3. Enter the GUI loop
s.gui(locals())
