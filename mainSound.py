from ast import Pass
from pickle import TRUE
import time
from pygame import mixer
import subprocess
from pynput.keyboard import Key, Listener, KeyCode
import json
'''
mixer.init(devicename = 'CABLE Input (VB-Audio Virtual Cable)') # Initialize it with the correct device
mixer.music.load("sounds/suspense.mp3") # Load the mp3
mixer.music.play() # Play it

while mixer.music.get_busy():  # wait for music to finish playing
    time.sleep(1)
'''
talk = True
p = None
sounds = None

deviceName = None
with open('json/sounds.json') as json_file:
    sounds = json.load(json_file)

with open('json/settings.json') as json_file:
    deviceName = json.load(json_file)

print(deviceName["saved"][0]["outputName"])
def stopTalking():
    p.terminate()
def startTalking():
    global talk
    talk = True

def playSound(name):
    global talk
    mixer.init(devicename = deviceName["saved"][0]["outputName"]) # Initialize it with the correct device
    mixer.music.load(name) # Load the mp3
    mixer.music.play() # Play it
    while mixer.music.get_busy():  # wait for music to finish playing
        time.sleep(0.01)
    #startTalking()


def on_press(key):
    print(key.vk)
    try:
        for i in range(len(sounds["sounds"])):
            if list(sounds["sounds"][i].values())[3] == key.vk :
                print(sounds["sounds"][i]["name"])
                
                playSound(sounds["sounds"][i]["file"])
                
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
