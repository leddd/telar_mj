from pyo import *
import random
import wx

# 1) Boot server
s = Server(duplex=0).boot().start()

# 2) Sounds
sounds = [
    "sound/S1.1.wav",
    "sound/S1.2.wav",
    "sound/S1.3.wav",
    "sound/S1.4.wav",
]

# work here!!

# Mapping 12 keys to semitone offsets from C
key_map = {
    ord('A'): 0,
    ord('W'): 1,
    ord('S'): 2,
    ord('E'): 3,
    ord('D'): 4,
    ord('F'): 5,
    ord('T'): 6,
    ord('G'): 7,
    ord('Y'): 8,
    ord('H'): 9,
    ord('U'): 10,
    ord('J'): 11
}

# Base frequency (C)
base_freq = 261.63

class KeyboardFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="12-note Keyboard", size=(300, 100))
        panel = wx.Panel(self)
        self.Bind(wx.EVT_CHAR_HOOK, self.onKey)
        self.Show()

    def onKey(self, event):
        key_code = event.GetKeyCode()
        if key_code in key_map:
            semitone = key_map[key_code]
            pitch_factor = 2 ** (semitone / 12.0)
            path = random.choice(sounds)
            SfPlayer(path, speed=pitch_factor, loop=False, mul=0.5).out()
        event.Skip()

# Launch GUI with key listener
app = wx.App(False)
frame = KeyboardFrame()
s.gui(locals())