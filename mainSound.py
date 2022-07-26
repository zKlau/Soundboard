import numpy
assert numpy
import json
import argparse
import queue
import sys
import ffmpeg
import youtube_dl
import keyboard
from threading import Thread
from pygame import mixer
from pynput.keyboard import Listener
from audioplayer import AudioPlayer
from flask import Flask, request
from os import remove
from time import sleep


class MainSound:
    def __init__(self):
        with open('package.json', 'r') as json_file:
            self.packageInfo = json.load(json_file)
        
        self.player = AudioPlayer
        self.soundsJson = 'json/sounds.json'
        self.settingsJson = 'json/settings.json'
        self.keybind_pressed = False
        self.current = set()
        

    

   
    def listen(self, vol):
        self.player.__setattr__('volume', vol*100)
        self.player.play(block=False)

    #Doesnt seen to work
    def urlSoundFile(self, audioURL):
        ydl_options = {
            'fromat' : 'bestaudio',
        }
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            info = ydl.extract_info(
                audioURL, download=False)
            #print(info['formats'][0]['url'])
            URL = info['formats'][0]['url']
        
        def int_or_str(text):
            try:
                return int(text)
            except ValueError:
                return text

        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument(
            '-l', '--list-devices', action='store_true',
            help='show list of audio devices and exit')
        args, remaining = parser.parse_known_args()
        if args.list_devices:
            #print(sd.query_devices())
            parser.exit(0)
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[parser])
        parser.add_argument(
            '-d', '--device', type=int_or_str,
            help='output device (numeric ID or substring)')
        parser.add_argument(
            '-b', '--blocksize', type=int, default=1024,
            help='block size (default: %(default)s)')
        parser.add_argument(
            '-q', '--buffersize', type=int, default=20,
            help='number of blocks used for buffering (default: %(default)s)')
        args = parser.parse_args(remaining)
        if args.blocksize == 0:
            parser.error('blocksize must not be zero')
        if args.buffersize < 1:
            parser.error('buffersize must be at least 1')
        
        q = queue.Queue(maxsize=args.buffersize)        

        try:
            info = ffmpeg.probe(URL)
        except ffmpeg.Error as e:
            sys.stderr.buffer.write(e.stderr)
            parser.exit(e)
        
        streams = info.get('streams', [])
        if len(streams) != 1:
            parser.exit('There must be exactly one stream available')
        
        stream = streams[0]
        
        if stream.get('codec_type') != 'audio':
            parser.exit('The stream must be an audio stream')
    
        
        


    def playSound(self, file, id):
        with open(self.soundsJson, 'r') as json_file:
            self.sounds = json.load(json_file)
        with open(self.settingsJson, 'r') as json_file:
            self.settings = json.load(json_file)
        self.deviceName = self.settings["saved"][0]["outputName"]
        
        if "https" not in file:
            mixer.pre_init(44100, -16, 1, 512)
            mixer.init(devicename=self.deviceName)
            mixer.music.load(file)
            mixer.music.set_volume(self.sounds["sounds"][id]["volume"])
            mixer.music.play()
            self.player = AudioPlayer(file)
            self.listen(self.sounds["sounds"][id]["volume"])
        else:
            self.urlSoundFile(file,id)

    def on_press(self, key):

        with open(self.soundsJson, 'r') as json_file:
            self.sounds = json.load(json_file)
        with open("json/readInput.json", 'r') as file:
            self.allowInput = json.load(file)
        try:
            if self.keybind_pressed == False and self.allowInput == True:
                self.current.add(key.vk)
                for i in range(len(self.sounds["sounds"])):
                    if "," in self.sounds["sounds"][i]["keybind"]:
                        st = self.sounds["sounds"][i]["keybind"].replace(',','+')
                        if keyboard.is_pressed(st):
                            self.keybind_pressed = True
                            self.player = AudioPlayer(self.sounds["sounds"][i]["file"])
                            self.playSound(self.sounds["sounds"][i]["file"], i)
        except Exception as e:
            print(e, key)
    def on_release(self,key):
        try:
            self.current.pop()
        except:
            pass
        with open('json/readInput.json', 'r') as file:
            self.allowInput = json.load(file)
        with open(self.soundsJson, 'r') as json_file:
            self.sounds = json.load(json_file)
        try:
            if len(self.current) == 0 and self.keybind_pressed == False and self.allowInput == True:
                for i in range(len(self.sounds["sounds"])):
                    if "," not in self.sounds["sounds"][i]["keycode"]:
                        if key.vk == int(self.sounds["sounds"][i]["keycode"]):
                            self.player = AudioPlayer(self.sounds["sounds"][i]["file"])
                            self.playSound(self.sounds["sounds"][i]["file"],i)
            
            if len(self.current) == 0:
                self.keybind_pressed = False
        except:
            pass

    def setup(self):
        print("READY")
        with Listener(on_press=self.on_press, on_release=self.on_release) as self.listener:
            self.listener.join()


ms = MainSound()
app = Flask(__name__)

SOUNDS_FOLDER = "sounds/"
SOUNDS_JSON = "json/sounds.json"
KEYCODES_JSON = "/json/keybinds.json"

@app.route('/soundsList', methods=['GET'])
def soundList():
    json_file = open(SOUNDS_JSON, 'r')
    data = json.load(json_file)
    return data


@app.route('/addNewSound', methods=['POST'])
def addNewSound():
    jsonF = open(SOUNDS_JSON, 'r')
    data = json.load(jsonF)
    data["sounds"].append(request.json)
    with open(SOUNDS_JSON, 'w') as json_file:
        json.dump(data, json_file,
                  indent=4,
                  separators=(',', ': '))

    return f"Added:\n {request.json}"


@app.route('/uploadSound', methods=['POST'])
def uploadSound():
    file = request.files['sound']
    file.save(f'{SOUNDS_FOLDER}{file.filename}')
    return f'Added {file.filename}'


@app.route('/removeSound', methods=['POST'])
def removeSound():
    jsonF = open(SOUNDS_JSON, 'r')
    data = json.load(jsonF)
    for i in range(len(data['sounds'])):
        if data['sounds'][i]['id'] == int(request.form['id']):
            remove(data['sounds'][i]['file'])
            del data['sounds'][i]
            break

    with open(SOUNDS_JSON, 'w') as json_file:
        json.dump(data, json_file,
                  indent=4,
                  separators=(',', ': '))
    return (f'Sound Removed')


@app.route('/playSound', methods=['POST'])
def sendPlay():
    pass
    #TODO
@app.route('/updateVolume', methods=['POST'])
def updateVolume():
    jsonF = open(SOUNDS_JSON)
    data = json.load(jsonF)
    for i in range(len(data['sounds'])):
        if data['sounds'][i]['id'] == int(request.json['id']):
            data['sounds'][i]['volume'] = float(request.json['volume'])
            break

    with open(SOUNDS_JSON, 'w') as json_file:
        json.dump(data, json_file,
                  indent=4,
                  separators=(',', ': '))
    return('Volume Updated')

def startServer():
    app.run('192.168.1.2')

serverThread = Thread(target=startServer, daemon=True)
serverThread.start()
ms.setup()

