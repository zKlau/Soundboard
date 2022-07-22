import json
import threading
import time
from ast import arg
from concurrent.futures import thread
from pickle import TRUE

import numpy  # Make sure NumPy is loaded before it is used in the callback
import sounddevice as sd
from pygame import mixer
from pynput.keyboard import Key, KeyCode, Listener

assert numpy
import argparse
import queue
import sys
import tkinter as tk
import tkinter.font as tkfont
import tkinter.ttk as ttk
from asyncio.windows_utils import Popen
from tkinter import *

import ffmpeg
import soundfile as sf
import youtube_dl
from audioplayer import AudioPlayer
from numpy import append, double
from pygubu.widgets.pathchooserinput import PathChooserInput
from pygubu.widgets.tkscrolledframe import TkScrolledFrame
import keyboard

with open('package.json') as json_file:
    packageInfo = json.load(json_file)

global volumeMic
with open('json/settings.json') as json_file:
    defaultVolume = json.load(json_file)
    volumeMic = defaultVolume["saved"][0]["micVolume"]

userMicrophoneStream = None
userTalk = False
doubleAudio = None
def voiceStart():
    global userMicrophoneStream
    values = None
    with open('json/settings.json') as json_file:
        values = json.load(json_file)

    def callback(indata, outdata, frames, time, status):
        if status:
            pass
        outdata[:] = indata * volumeMic

    try:
        userMicrophoneStream = sd.Stream(device=(values["saved"][0]["inputMic"], values["saved"][0]["outputMic"]), callback=callback)
        userMicrophoneStream.start()

    except Exception as e:
        print(type(e).__name__ + ': ' + str(e))

player = None


def startSound():
    global player
    global soundMain
    soundMain = None
    global deviceName
    deviceName = None
    global player
    global keybind_pressed

    with open('json/sounds.json') as json_file:
        soundMain = json.load(json_file)

    with open('json/settings.json') as json_file:
        deviceName = json.load(json_file)

    def listen(vol):
        player.__setattr__('volume', vol*100)
        player.play(block=False)
    def urlSoundFile(audioURL,id):
        global urlAudioMic
        ydl_opts = {
            'format': 'bestaudio',
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
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
        
        #print('Getting stream information ...')
        
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
        
        channels = stream['channels']
        samplerate = float(stream['sample_rate'])
        
        
        def callback(outdata, frames, time, status):
            assert frames == args.blocksize
            if status.output_underflow:
                print('Output underflow: increase blocksize?', file=sys.stderr)
                raise sd.CallbackAbort
            assert not status
            try:
                data = q.get_nowait()
            except queue.Empty as e:
                print('Buffer is empty: increase buffersize?', file=sys.stderr)
            if len(data) == len(outdata):
                outdata[:] = data
            else:
                stream.abort()
                if userTalk:
                    userMicrophoneStream.start()
        
        
        try:
            #print('Opening stream ...')
            process = ffmpeg.input(
                URL
            ).output(
                'pipe:',
                format='f32le',
                acodec='pcm_f32le',
                ac=channels,
                ar=samplerate,
                loglevel='quiet',
            ).run_async(pipe_stdout=True)
            stream = sd.RawOutputStream(
                samplerate=samplerate, blocksize=args.blocksize,
                device=14, channels=channels, dtype='float32',
                callback=callback)
            read_size = args.blocksize * channels * stream.samplesize
            urlAudioMic = stream
            #print('Buffering ...')
            for _ in range(args.buffersize):
                q.put_nowait(process.stdout.read(read_size))
            #print('Starting Playback ...')
            with stream:
                timeout = args.blocksize * args.buffersize / samplerate
                while True:
                    q.put(process.stdout.read(read_size), timeout=timeout)
        except KeyboardInterrupt:
            parser.exit('\nInterrupted by user')
        except queue.Full:
            # A timeout occurred, i.e. there was an error in the callback
            parser.exit(1)
        except Exception as e:
            parser.exit(type(e).__name__ + ': ' + str(e))
    

    def playSound(name,id):
        global talk
        global soundMain
        global player
        with open('json/sounds.json') as json_file:
            soundMain = json.load(json_file)

        if "https" not in name:
            mixer.pre_init(44100, -16, 1, 512)
            mixer.init(devicename = deviceName["saved"][0]["outputName"] ) # Initialize it with the correct device #
            mixer.music.load(name)
            mixer.music.set_volume(soundMain["sounds"][id]["volume"])
            mixer.music.play()
            player = AudioPlayer(name)
            listen(soundMain["sounds"][id]["volume"])
        else:
            if userTalk:
                userMicrophoneStream.abort()
            urlSoundFile(name,id)

    
    global muted
    muted = False
    keybind_pressed = False
    current = set()
    allowInput = True
    def on_press(key):
        global volumeMic
        global deviceName
        global muted
        global player
        
        
        global keybind_pressed
        global keybind

        with open('json/sounds.json') as json_file:
            soundMain = json.load(json_file)
        with open('json/readInput.json') as file:
            allowInput = json.load(file)
        try:
            
            if keybind_pressed == False and allowInput == True:
                current.add(key.vk)
                for i in range(len(soundMain["sounds"])):
                    if "," in soundMain["sounds"][i]["keybind"]:
                        st = soundMain["sounds"][i]["keybind"].replace(',','+')
                        if keyboard.is_pressed(st):
                            keybind_pressed = True
                            player = AudioPlayer(soundMain["sounds"][i]["file"])
                            playSound(soundMain["sounds"][i]["file"],i)
        except:
            pass


    def on_release(key):
        global keybind_pressed
        global volumeMic
        global deviceName
        global muted
        global player

        try:
            current.pop()
        except:
            pass
        with open('json/readInput.json') as file:
            allowInput = json.load(file)
        with open('json/sounds.json') as json_file:
            soundMain = json.load(json_file)
        try:
            if len(current) == 0 and keybind_pressed == False and allowInput == True:
                for i in range(len(soundMain["sounds"])):
                    if "," not in soundMain["sounds"][i]["keycode"]:
                        if key.vk == int(soundMain["sounds"][i]["keycode"]):
                            player = AudioPlayer(soundMain["sounds"][i]["file"])
                            playSound(soundMain["sounds"][i]["file"],i)
            
            if len(current) == 0:
                keybind_pressed = False
        except:
            pass
    listener = Listener(on_press=on_press, on_release=on_release)
    listener.start()

    print("######### START TALKING #########")


def loopHole():
    while True:
        time.sleep(0.1)
guiThread = threading.Thread(target=loopHole)
userVoiceThread = threading.Thread(target=voiceStart, daemon=True)
soundThread = threading.Thread(target=startSound, daemon=True)

if userTalk:
    userVoiceThread.start()

guiThread.start()
soundThread.start()
