from tkinter import *
import math
import random
import RPi.GPIO as GPIO
import simpleaudio as sa
GPIO.setmode(GPIO.BCM)
import os
import time
import numpy
import pygame
import pyaudio
import threading
import board
import busio
import adafruit_mpr121

os.system('xset r off')
figuras= []
audio= []
sonidos= [] 
tocando= []
playing= []
cadena = []

for x in range (24):
    parametros = []
    audio.append(False)
    tocando.append(False)
    for y in range (2):
        p = random.randint(0,360)
        parametros.append(p)
    figuras.append(parametros)
    
w=1000
h=700
canvas =Canvas(bg="#999999", height=h, width=w)

pygame.init()
bits = 16
sample_rate = 44100
pygame.mixer.pre_init(sample_rate, bits)

i2c = busio.I2C(board.SCL, board.SDA)
mpr1 = adafruit_mpr121.MPR121(i2c, address = 0x5a)
mpr2 = adafruit_mpr121.MPR121(i2c, address = 0x5c)

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
        sound.play(loops=1, maxtime=int(duration*1000))
                    
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
    l = 400
    a= 200
    print(cadena)
    canvas.pack()

def revisarmpr():
    print("hola")
    for i in range(12):
        if mpr1[i].value:
            print("pin {}".format(i))
        if mpr2[i].value:
            print("pin {}".format(i+12))
        
    time.sleep(1)
    

revisarmpr()
mainloop()
