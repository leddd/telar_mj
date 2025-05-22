from tkinter import *
import math
import random
import RPi.GPIO as GPIO
import simpleaudio as sa
GPIO.setmode(GPIO.BCM)



pines = [4,14,15,17,18,27,22,23,24,10,9,11,8,7,20,21,5,6,12,13,19,16,26]
w1 = sa.WaveObject.from_wave_file("01.wav")
w2 = sa.WaveObject.from_wave_file("02.wav")
w3 = sa.WaveObject.from_wave_file("03.wav")
w4= sa.WaveObject.from_wave_file("04.wav")
w5 = sa.WaveObject.from_wave_file("05.wav")
w6 = sa.WaveObject.from_wave_file("06.wav")
w7 = sa.WaveObject.from_wave_file("07.wav")
w8 = sa.WaveObject.from_wave_file("08.wav")
w9 = sa.WaveObject.from_wave_file("09.wav")
w10 = sa.WaveObject.from_wave_file("10.wav")
w11 = sa.WaveObject.from_wave_file("11.wav")
w12 = sa.WaveObject.from_wave_file("12.wav")
w13 = sa.WaveObject.from_wave_file("13.wav")
w14 = sa.WaveObject.from_wave_file("14.wav")
w15 = sa.WaveObject.from_wave_file("15.wav")
w16 = sa.WaveObject.from_wave_file("16.wav")
w17 = sa.WaveObject.from_wave_file("17.wav")
w18 = sa.WaveObject.from_wave_file("18.wav")
w19 = sa.WaveObject.from_wave_file("19.wav")
w20 = sa.WaveObject.from_wave_file("20.wav")
w21 = sa.WaveObject.from_wave_file("21.wav")
w22 = sa.WaveObject.from_wave_file("22.wav")
w23 = sa.WaveObject.from_wave_file("23.wav")
w24 = sa.WaveObject.from_wave_file("24.wav")

figuras= []

for x in pines:
	   GPIO.setup(x, GPIO.IN)

for x in range (24):
    parametros = []
    c = random.randint(6,20)
    for y in range (c):
        p = random.randint(0,360)
        parametros.append(p)
    figuras.append(parametros)
    
win = Tk()
w=1000
h=800
win.geometry(str(w)+"x"+str(h))
canvas =Canvas(win, bg="white", height=h, width=w)


def dibujar(parametros):
    l = 400
    a= 200

    canvas.delete("all")
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

                
def tt2():
	for x in pines:
        #r1 = random.choice(pines) #qui es donde hay que leer los pines si es que estan en alto o no
		if GPIO.input(x) == GPIO.HIGH:
			dibujar(figuras[pines.index(x)])
			match pines.index(x):
				case 0:
                    
					po= w1.play()
				case 1:
					po= w2.play()
				case 2:
					po= w3.play()
				case 3:
					po= w4.play()
				case 4:
					po= w5.play()
				case 5:
					po= w6.play()
				case 6:
					po= w7.play()
				case 7:
					po= w8.play()
				case 8:
					po= w9.play()
				case 9:
					po= w10.play()
				case 10:
					po= w11.play()
				case 11:
					po= w12.play()
				case 12:
					po= w13.play()
				case 13:
					po= w14.play()
				case 14:
					po= w15.play()
				case 15:
					po= w16.play()
				case 16:
					po= w17.play()
				case 17:
					po= w18.play()
				case 18:
					po= w19.play()
				case 19:
					po= w20.play()
				case 20:
					po= w21.play()
				case 21:
					po= w22.play()
				case 22:
					po= w23.play()
				case 23:
					po= w24.play()
            
            
	canvas.pack()
	win.after(100, tt2)
    
tt2()

win.mainloop()
