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
    
sound_name = "discord_join.mp3"

keys_codes = {
    "SHIFT": 0x10,
    "CTRL": 0x11,
    "ALT": 0x12,
    "ESCAPE": 0x1B,
    "SPACEBAR": 0x20,
    "PAGE UP": 0x21,
    "PAGE DOWN": 0x22,
    "END": 0x23,
    "LEFT ARROW": 0x25,
    "UP ARROW": 0x26,
    "RIGHT ARROW": 0x27,
    "DOWN ARROW": 0x28,
    "SELECT": 0x29,
    "PRINT": 0x2A,
    "PRINT SCREEN": 0x2C,
    "DEL": 0x2E,
    "0": 0x30,
    "1": 0x31,
    "2": 0x32,
    "3": 0x33,
    "4": 0x34,
    "5": 0x35,
    "6": 0x36,
    "7": 0x37,
    "8": 0x38,
    "9": 0x39,
    "A": 0x41,
    "B": 0x42,
    "C": 0x43,
    "D": 0x44,
    "E": 0x45,
    "F": 0x46,
    "G": 0x47,
    "H": 0x48,
    "I": 0x49,
    "J": 0x4A,
    "K": 0x4B,
    "L": 0x4C,
    "M": 0x4D,
    "N": 0x4E,
    "O": 0x4F,
    "P": 0x50,
    "Q": 0x51,
    "R": 0x52,
    "S": 0x53,
    "T": 0x54,
    "U": 0x55,
    "V": 0x56,
    "W": 0x57,
    "X": 0x58,
    "Y": 0x59,
    "Z": 0x5A,
    "NUM 0": 0x60,
    "NUM 1": 0x61,
    "NUM 2": 0x62,
    "NUM 3": 0x63,
    "NUM 4": 0x64,
    "NUM 5": 0x65,
    "NUM 6": 0x66,
    "NUM 7": 0x67,
    "NUM 8": 0x68,
    "NUM 9": 0x69,
    "MULTIPLY": 0x6A,
    "ADD": 0x6B,
    "SEPARATOR":0x6C,
    "SUBSTRACT":0x6D,
    "DECIMAL": 0x6E,
    "DIVIDE": 0x6F,
    "LEFT SHIFT": 0xA0,
    "RIGHT SHIFT": 0xA1,
    "LEFT CONTROL": 0xA2,
    "RIGHT CONTROL": 0xA3
}

# key + sound
sounds = {
    keys_codes["NUM 1"]: "culcat.mp3",
    keys_codes["NUM 2"]: "discord_join.mp3",
    keys_codes["NUM 3"]: "emotional-damage.mp3",
    keys_codes["NUM 4"]: "oh_he_no.mp3",
    keys_codes["NUM 5"]: "vomit.mp3",
    keys_codes["NUM 0"]: "wow-sound.mp3"
}


def playSound(name):
    mixer.init(devicename = 'CABLE Input (VB-Audio Virtual Cable)') # Initialize it with the correct device
    mixer.music.load("sounds/" + name) # Load the mp3
    mixer.music.play() # Play it
    while mixer.music.get_busy():  # wait for music to finish playing
        time.sleep(0.01)
    


while(True):
    time.sleep(0.05)
    mute = win32api.GetAsyncKeyState(keys_codes["F"])&0x0001
    sound = win32api.GetAsyncKeyState(keys_codes["NUM 0"])&0x0001
    global p

    if n == True:
        if online == True:
            p = subprocess.Popen('py inputPass.py')
            online = False
    if mute > 0:
        p.terminate()
        if n == False:
            n = True
            online = True
        elif n == True:
            n = False
    if sound > 0:
        p.terminate()
        playSound(sounds[keys_codes["NUM 0"]])
        n = True
        online = True

    time.sleep(0.05)
