from pickle import TRUE
import time
from pygame import mixer
import signal
import subprocess
import keyboard
import os
import win32api
'''
mixer.init(devicename = 'CABLE Input (VB-Audio Virtual Cable)') # Initialize it with the correct device
mixer.music.load("sounds/suspense.mp3") # Load the mp3
mixer.music.play() # Play it

while mixer.music.get_busy():  # wait for music to finish playing
    time.sleep(1)
'''
n = True
online = True
try:
    sig = signal.CTRL_C_EVENT
except NameError:
    sig = signal.SIGTERM
    
while(True):
    keystate = win32api.GetAsyncKeyState(0x46)&0x0001
    global p
    if n == True:
        if online == True:
            p = subprocess.Popen('py inputPass.py')
            online = False
    if keystate > 0:
        p.terminate()
        print(n)
        if n == False:
            n = True
            online = True
        elif n == True:
            n = False
