from tkinter import *
import random
import math
from pyo import *


# Force ALSA playback only (duplex=0), 2 channels out
s = Server(audio='alsa', duplex=0, nchnls=2).boot()
s.start()

# now you can build your synths/players…


# Inicializar servidor de audio
s = Server().boot()
s.start()

# Diccionario de osciladores activos
osciladores = {}

# Ventana gráfica
win = Tk()
w, h = 800, 600
win.geometry(f"{w}x{h}")
canvas = Canvas(win, bg="white", height=h, width=w)
canvas.pack()

# Asignar 24 teclas a acciones
teclas = "qwertyuiopasdfghjklzxcvbnm"[:24]

def bezier(p0, p1, p2, p3, t):
    """Calcula punto en curva Bézier cúbica"""
    return (
        (1 - t) ** 3 * p0 +
        3 * (1 - t) ** 2 * t * p1 +
        3 * (1 - t) * t ** 2 * p2 +
        t ** 3 * p3
    )

def dibujar_curvas(tecla):
    canvas.delete("all")
    for _ in range(random.randint(2, 4)):
        puntos = [(random.randint(0, w), random.randint(0, h)) for _ in range(4)]
        last = puntos[0]
        for t in [i / 50.0 for i in range(51)]:
            x = bezier(puntos[0][0], puntos[1][0], puntos[2][0], puntos[3][0], t)
            y = bezier(puntos[0][1], puntos[1][1], puntos[2][1], puntos[3][1], t)
            canvas.create_line(last[0], last[1], x, y, fill=random.choice(["red", "blue", "green", "purple"]), width=2)
            last = (x, y)

def sonido_tecla(tecla):
    if tecla in osciladores:
        osciladores[tecla].stop()
    freq = 200 + teclas.index(tecla) * 30
    env = Adsr(attack=0.01, decay=0.1, sustain=0.4, release=0.3, dur=1, mul=0.3)
    osc = Sine(freq=freq, mul=env).out()
    env.play()
    osciladores[tecla] = osc

def presionar(event):
    tecla = event.char
    if tecla in teclas:
        dibujar_curvas(tecla)
        sonido_tecla(tecla)

win.bind("<Key>", presionar)

win.mainloop()
