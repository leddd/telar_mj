from pyo import *

# 1) Boot server (output-only).
s = Server(duplex=0).boot().start()

# 2) Play at 1.5× speed (≈ +7 semitones). Loop forever.
sf = SfPlayer("sound/S1.1.wav",
              speed=1.5,    # 1.0 = original pitch; 2.0 = +1 octave
              loop=True,
              mul=0.4).out()

# 3. Enter the GUI loop
s.gui(locals())
