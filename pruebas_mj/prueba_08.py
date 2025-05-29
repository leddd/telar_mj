from tkinter import * 
import time
import busio
import board
import adafruit_mpr121
import os
import time
import numpy
import pygame
import pyaudio
import random
import math
import threading
from datetime import datetime

mj = Tk()

mjc = Canvas(mj, width=200, height=200)
mjc.pack()

cadena = []

i2c = busio.I2C(board.SCL, board.SDA)
mpr1 = adafruit_mpr121.MPR121(i2c, address = 0x5a)
mpr2 = adafruit_mpr121.MPR121(i2c, address = 0x5c)

pygame.init()
bits = 16
sample_rate = 44100
pygame.mixer.pre_init(samddple_rate, bits)

ahora = datetime.now()
nom = ahora.strftime("%Y-%m-%d-%H-%M-%S")
archi = (nom+".txt")

def sine_x(amp, freq, time):
    return int(round(amp*math.sin(2*math.pi*freq*time)))

class Tone:
    def sine(freq,duration=0.5, speaker=None):
        num_samples = int(round(duration * sample_rate))
        sound_buffer = numpy.zeros((num_samples,2),dtype = numpy.int16)
        amplitude = 2**(bits-1)-1
        
        for sample_num in range (num_samples):
            time=float(sample_num)/sample_rate
            sine=sine_x(amplitude, freq, time)
            if speaker == 'r':
                sound_buffer[sample_num][1] = sine
            if speaker == 'l':
                sound_buffer[sample_num][0] = sine
                
            else:
                sound_buffer[sample_num][1] = sine
                sound_buffer[sample_num][0] = sine
                    
        sound = pygame.sndarray.make_sound(sound_buffer)
        sound.play(loops=1, maxtime=int(duration*80))
                    
    @staticmethod
    def create_tone_from_list(freq_list, duration=1, speaker=None):
        freq_threads = []
        for freq in freq_list:
            freq_thread = threading.Thread(target=Tone.sine, args=[freq*100,duration,speaker])
            freq_threads.append(freq_thread)
            freq_thread = threading.Thread(target=Tone.sine, args=[freq,duration,speaker])
            freq_threads.append(freq_thread)
        for freq_thread in freq_threads:
            freq_thread.start()
        for freq_thread in freq_threads:
            freq_thread.join() 

def dibujar(cadena):
    cadena.sort()
    for x in cadena:
        #Tone.create_tone_from_list([x*100, (x+1)*500])
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
