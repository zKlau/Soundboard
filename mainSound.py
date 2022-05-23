from ast import Pass
from pickle import TRUE
import time
from pygame import mixer
import subprocess
from pynput.keyboard import Key, Listener, KeyCode
'''
mixer.init(devicename = 'CABLE Input (VB-Audio Virtual Cable)') # Initialize it with the correct device
mixer.music.load("sounds/suspense.mp3") # Load the mp3
mixer.music.play() # Play it

while mixer.music.get_busy():  # wait for music to finish playing
    time.sleep(1)
'''
n = True
online = True
sound = 0
mute = 0
talk = True
p = None


sound_name = "discord_join.mp3"

key_codes = {
    "NUM 1": 97,
    "NUM 2": 98,
    "NUM 3": 99,
    "NUM 4": 100,
    "NUM 5": 101,
    "NUM 0": 96
}

# key + sound
sounds = {
    key_codes["NUM 1"]: "culcat.mp3",
    key_codes["NUM 2"]: "discord_join.mp3",
    key_codes["NUM 3"]: "emotional-damage.mp3",
    key_codes["NUM 4"]: "oh_he_no.mp3",
    key_codes["NUM 5"]: "vomit.mp3",
    key_codes["NUM 0"]: "wow-sound.mp3"
}

def stopTalking():
    p.terminate()
def startTalking():
    global talk
    talk = True

def playSound(name):
    global talk
    mixer.init(devicename = 'CABLE Input (VB-Audio Virtual Cable)') # Initialize it with the correct device
    mixer.music.load("sounds/" + name) # Load the mp3
    mixer.music.play() # Play it
    while mixer.music.get_busy():  # wait for music to finish playing
        time.sleep(0.01)
    startTalking()



def on_press(key):
    try:
        num = key.vk
        if num in sounds:
            stopTalking()
            print("play sound")
            playSound(sounds[num])
    except:
        pass
        

listener = Listener(on_press=on_press)
listener.start()

print("######### START TALKING #########")
while True:
    time.sleep(0.05)

    if talk == True:
        p = subprocess.Popen('py inputPass.py')
        talk = False
