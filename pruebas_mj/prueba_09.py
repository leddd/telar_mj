from tkinter import * 
import time
import busio
import board
import adafruit_mpr121
import time
from datetime import datetime
import pygame as pg
import numpy as np

#INICIALIZACION DEL ESPACIO DE PANTALLA
pg.mixer.init()
mj = Tk()

mjc = Canvas(mj, width=200, height=200)
mjc.pack()

cadena = []

i2c = busio.I2C(board.SCL, board.SDA)
mpr1 = adafruit_mpr121.MPR121(i2c, address = 0x5a)
mpr2 = adafruit_mpr121.MPR121(i2c, address = 0x5c)

ahora = datetime.now()
nom = ahora.strftime("%Y-%m-%d-%H-%M-%S")
archi = (nom+".txt")

#FUNCION PARA GENERAR SINTESIS DE AUDIO
def synth(frequency, duration=1, sampling_rate=44100):
    frames = int(duration*sampling_rate)
    arr = np.cos(2*np.pi*frequency*np.linspace(0,duration, frames))
    arr = arr + np.cos(4*np.pi*frequency*np.linspace(0,duration, frames))
    arr = arr - np.cos(6*np.pi*frequency*np.linspace(0,duration, frames))
    arr = arr/max(np.abs(arr))
    sound = np.asarray([32767*arr,32767*arr]).T.astype(np.int16)
    sound = pg.sndarray.make_sound(sound.copy())
    return sound

#ARRAY DE SONIDOS (NOTAS?)
sonidos = {}
for x in range(30):
    sample=synth(20*x+500)
    sonidos[x]=sample

def dibujar(cadena):
    cadena.sort()
    for x in cadena:
        sonidos[x].play()
        sonidos[x].fadeout(1000)
        mjc.create_line(0,0,(x+1)*10,(x+1)*10)
        time.sleep(0.1)
        mjc.update()
        mjc.delete("all")
    
    lista = ""
    for x in range (12):
        m = "O "
        for y in cadena:
            if x == y:
                m = "X "
        lista+=m
        
    ahora = datetime.now()
    nom = ahora.strftime("%Y-%m-%d-%H-%M-%S")
    global archi
    with open(archi, "a") as f:
        f.write(nom+"  "+lista+"\n")

def plot(cadena):
    if len(cadena)>0:
        print(cadena)
        dibujar(cadena)

def revisarmpr():
    while True:
        cadena=[]
        for i in range(12):
            if mpr1[i].value:
                cadena.append(i)
            if mpr2[i].value:
                cadena.append(i+12)    
        plot(cadena)
        
mj.after(100, revisarmpr)
mj.mainloop()
