from tkinter import *
import math
import random
import RPi.GPIO as GPIO
import simpleaudio as sa
GPIO.setmode(GPIO.BCM)
figuras = []

win = Tk()
w=1000
h=800
canvas = Canvas(win, bg="white", height=h, width=w)
win.geometry(str(w)+"x"+str(h))

def dibujar(index):
    print("hola")
    l = 400
    a = 200

    canvas.delete("all")
    for x in range (24):
        parametros = []
        for y in range (1):
            parametros.append(random.randint(0,360))
        figuras.append(parametros)

        
    for x in range(360):
         for y in figuras[index]:
            if y == x:
                canvas.create_line(w/4,h/4,math.sin(math.radians(x))*l+w/2,math.cos(math.radians(x))*a+h/2, width=random.randint(2,6))
                canvas.create_line(w/2,h/4,math.sin(math.radians(x))*l+w/2,math.cos(math.radians(x))*a+h/2, width=random.randint(2,6))
                canvas.create_line(w/2+w/4,h/4,math.sin(math.radians(x))*l+w/2,math.cos(math.radians(x))*a+h/2, width=random.randint(2,6))
                
                canvas.create_line(w/4,h/2,math.sin(math.radians(x))*l+w/2,math.cos(math.radians(x))*a+h/2, width=random.randint(2,6))
                canvas.create_line(w/2,h/2,math.sin(math.radians(x))*l+w/2,math.cos(math.radians(x))*a+h/2, width=random.randint(2,6))
                canvas.create_line(w/2+w/4,h/2,math.sin(math.radians(x))*l+w/2,math.cos(math.radians(x))*a+h/2, width=random.randint(2,6))
                
                canvas.create_line(w/4,h/2+h/4,math.sin(math.radians(x))*l+w/2,math.cos(math.radians(x))*a+h/2, width=random.randint(2,6))
                canvas.create_line(w/2,h/2+h/4,math.sin(math.radians(x))*l+w/2,math.cos(math.radians(x))*a+h/2, width=random.randint(2,6))
                canvas.create_line(w/2+w/4,h/2+h/4,math.sin(math.radians(x))*l+w/2,math.cos(math.radians(x))*a+h/2, width=random.randint(2,6))
    canvas.pack()
win.after(1000, dibujar(random.randint(0,23)))
win.mainloop()
