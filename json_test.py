import json
import time
from pynput.keyboard import Key, Listener, KeyCode

data = None
'''
with open('json/sounds.json') as json_file:
    data = json.load(json_file)


        

listener = Listener(on_press=on_press)
listener.start()
while True:
    time.sleep(0.05)
'''
with open('json/sounds.json') as json_file:
    data = json.load(json_file)

def on_press(key):
    try:
        print(key.vk)
        for i in range(len(data["sounds"])):
            if key.vk in data["sounds"][i].values():
                print(data["sounds"][i]["name"])
    except:
        pass
listener = Listener(on_press=on_press)
listener.start()
while True:
    time.sleep(0.06)

