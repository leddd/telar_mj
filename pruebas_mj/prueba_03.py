from tkinter import *
import math
import random
import RPi.GPIO as GPIO
import simpleaudio as sa
GPIO.setmode(GPIO.BCM)
import os
os.system('xset r off')
figuras= []
audio= []
sonidos= [] 
tocando= []
playing= []

for x in range (24):
    parametros = []
    audio.append(False)
    tocando.append(False)
    sonidos.append(sa.WaveObject.from_wave_file(str(x)+".wav"))
    for y in range (2):
        p = random.randint(0,360)
        parametros.append(p)
    figuras.append(parametros)
    
win = Tk()
w=1000
h=700
win.geometry(str(w)+"x"+str(h))
canvas =Canvas(win, bg="#999999", height=h, width=w)


def dibujar(parametros):
    l = 400
    a= 200

    canvas.delete("all")
    
        
    for x in range(30):
                canvas.create_line(w/4,h/4,math.sin(math.radians(x*12))*l+w/2,math.cos(math.radians(x*12))*a+h/2, width=2,fill="white")
                canvas.create_line(w/2,h/4,math.sin(math.radians(x*12))*l+w/2,math.cos(math.radians(x*12))*a+h/2, width=2,fill="white")
                canvas.create_line(w/2+w/4,h/4,math.sin(math.radians(x*12))*l+w/2,math.cos(math.radians(x*12))*a+h/2, width=2,fill="white")
                
                canvas.create_line(w/4,h/2,math.sin(math.radians(x*12))*l+w/2,math.cos(math.radians(x*12))*a+h/2, width=2,fill="white")
                canvas.create_line(w/2,h/2,math.sin(math.radians(x*12))*l+w/2,math.cos(math.radians(x*12))*a+h/2, width=2,fill="white")
                canvas.create_line(w/2+w/4,h/2,math.sin(math.radians(x*12))*l+w/2,math.cos(math.radians(x*12))*a+h/2, width=2,fill="white")
                
                canvas.create_line(w/4,h/2+h/4,math.sin(math.radians(x*12))*l+w/2,math.cos(math.radians(x*12))*a+h/2, width=2,fill="white")
                canvas.create_line(w/2,h/2+h/4,math.sin(math.radians(x*12))*l+w/2,math.cos(math.radians(x*12))*a+h/2, width=2,fill="white")
                canvas.create_line(w/2+w/4,h/2+h/4,math.sin(math.radians(x*12))*l+w/2,math.cos(math.radians(x*12))*a+h/2, width=2,fill="white")

                
    canvas.fill="black"    
    for x in range(360):
        for y in parametros:
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

                

def key_press(e):
    #print(e.keysym)
    match e.keysym:
        case 'q':
            audio[0]=True
            dibujar(figuras[0])
        case 'w':
            audio[1]=True
            dibujar(figuras[1])
        case 'e':
            audio[2]=True
            dibujar(figuras[2])
        case 'r':
            audio[3]=True
            dibujar(figuras[3])
        case 't':
            audio[4]=True
            dibujar(figuras[4])
        case 'y':
            audio[5]=True
            dibujar(figuras[5])
        case 'u':
            audio[6]=True
            dibujar(figuras[6])
        case 'i':
            audio[7]=True
            dibujar(figuras[7])
        case 'o':
            audio[8]=True
            dibujar(figuras[8])
        case 'p':
            audio[9]=True
            dibujar(figuras[9])
        case 'a':
            audio[10]=True
            dibujar(figuras[10])
        case 's':
            audio[11]=True
            dibujar(figuras[11])
        case 'd':
            audio[12]=True
            dibujar(figuras[12])
        case 'f':
            audio[13]=True
            dibujar(figuras[13])
        case 'g':
            audio[14]=True
            dibujar(figuras[14])
        case 'h':
            audio[15]=True
            dibujar(figuras[15])
        case 'j':
            audio[16]=True
            dibujar(figuras[16])
        case 'k':
            audio[17]=True
            dibujar(figuras[17])
        case 'l':
            audio[18]=True
            dibujar(figuras[18])
        case 'z':
            audio[19]=True;
            dibujar(figuras[19])
        case 'x':
            audio[20]=True
            dibujar(figuras[20])
        case 'c':
            audio[21]=True
            dibujar(figuras[21])
        case 'v':
            audio[22]=True
            dibujar(figuras[22])
        case 'b':
            audio[23]=True
            dibujar(figuras[23])

def checkplay():
    
    for i,a in enumerate(audio):
        if a == True and tocando[i] == False and len(playing)<6:
            playing.append(sonidos[i].play())
            tocando[i]=True
            #print(len(playing))
    
    for i,p in enumerate(playing):
        if p.is_playing() == False:
            playing.pop(i)
            #print(len(playing))
            for a in audio:
                a = False
           

    win.after(100,checkplay)                    
    canvas.pack()
checkplay()
win.bind('<KeyPress>',key_press)
win.mainloop()
