from ast import Pass
from pickle import TRUE
import time
from pygame import mixer
import subprocess
from pynput.keyboard import Key, Listener, KeyCode
import json
import ui
import threading
import sounddevice as sd
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy
import argparse
from pygubu.widgets.pathchooserinput import PathChooserInput
from pygubu.widgets.tkscrolledframe import TkScrolledFrame
import tkinter.font as tkfont
import sys
from tkinter import *
from asyncio.windows_utils import Popen
import tkinter as tk
import tkinter.ttk as ttk
from turtle import update
from numpy import append
'''
mixer.init(devicename = 'CABLE Input (VB-Audio Virtual Cable)') # Initialize it with the correct device
mixer.music.load("sounds/suspense.mp3") # Load the mp3
mixer.music.play() # Play it

while mixer.music.get_busy():  # wait for music to finish playing
    time.sleep(1)
'''
def stop():
    sys.exit()

def audioStart():
    values = None
    with open('json/settings.json') as json_file:
        values = json.load(json_file)


    def int_or_str(text):
        """Helper function for argument parsing."""
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
        print(sd.query_devices())
        parser.exit(0)
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[parser])
    parser.add_argument(
        '-i', '--input-device', type=int_or_str,
        help='input device (numeric ID or substring)')
    parser.add_argument(
        '-o', '--output-device', type=int_or_str,
        help='output device (numeric ID or substring)')
    parser.add_argument(
        '-c', '--channels', type=int, default=2,
        help='number of channels')
    parser.add_argument('--dtype', help='audio data type')
    parser.add_argument('--samplerate', type=float, help='sampling rate')
    parser.add_argument('--blocksize', type=int, help='block size')
    parser.add_argument('--latency', type=float, help='latency in seconds')
    args = parser.parse_args(remaining)


    def callback(indata, outdata, frames, time, status):
        if status:
            print(status)
        outdata[:] = indata

    try:
        with sd.Stream(device=(values["saved"][0]["inputMic"], values["saved"][0]["outputMic"]),
                       samplerate=args.samplerate, blocksize=args.blocksize,
                       dtype=args.dtype, latency=args.latency,
                       channels=args.channels, callback=callback):

            #print('#' * 80)
            #print('press Return to quit')
            #print('#' * 80)
            input()

    except KeyboardInterrupt:
        parser.exit('')
    except Exception as e:
        print(type(e).__name__ + ': ' + str(e))

def userInterface():
    sounds = None

    with open('json/sounds.json') as json_file:
        sounds = json.load(json_file)

    keybinds = None
    _inputMic = None
    _outputMic = None
    _ins = {}
    _outs = {}
    p = None
    #"Windows DirectSound"
    for i in range(len(sd.query_devices())):
            if(sd.query_devices()[i]['hostapi'] == 1):
                if(sd.query_devices()[i]['max_input_channels'] > 0):

                    _ins[sd.query_devices()[i]['name']] = i
                else:

                        _outs[sd.query_devices()[i]['name']] = i

    #print("$$$$$")
    #print(_outs.keys())
    with open('json/keybinds.json') as json_file:
        keybinds = json.load(json_file)


    def addSound(name,keybind,path):
        global sounds
        with open('json/sounds.json') as json_file:
            sounds = json.load(json_file)

        key = None
        for i in range(len(keybinds['keybinds'][0])):
            if(list(keybinds['keybinds'][0].keys())[i] == keybind):
                key = list(keybinds['keybinds'][0].values())[i]

        x = {
                "id": len(sounds['sounds']),
                "name": name,
                "file": path,
                "keycode": key,
                "keybind": keybind
            }
        write_json(x)
        updateList()
        print("added")


    def combo_configure(event):
        combo = event.widget
        style = ttk.Style()

        long = max(combo.cget('values'), key=len)

        font = tkfont.nametofont(str(combo.cget('font')))
        width = max(0,font.measure(long.strip() + '0') - combo.winfo_width())

        style.configure('TCombobox', postoffset=(0,0,width,0))

    def saveInOut(input,output):
        for i in range(len(_ins)):
            if list(_ins)[i] == input:
                write_json_inout(_ins[list(_ins)[i]],"inputMic")
        for i in range(len(_outs)):
            if list(_outs)[i] == output:
                write_json_inout(_outs[list(_outs)[i]],"outputMic")
                write_json_inout(output,"outputName")

    #listZone = None

    class GuiApp:
        def __init__(self, master=None):
            global listZone
            # build ui
            self.toplevel3 = tk.Tk() if master is None else tk.Toplevel(master)
            self.Main = tk.Frame(self.toplevel3)
            self.Header = tk.Frame(self.Main)
            self.label3 = ttk.Label(self.Header)
            self.label3.configure(
                anchor="s",
                background="#049a8f",
                font="{Yu Mincho} 20 {bold}",
                foreground="#023436",
            )
            self.label3.configure(text="Soundpad - demo")
            self.label3.pack(anchor="w", padx="15", side="top")
            self.separator7 = ttk.Separator(self.Header)
            self.separator7.configure(orient="horizontal")
            self.separator7.pack(fill="x", side="bottom")
            self.credits = ttk.Label(self.Header)
            self.credits.configure(
                background="#049a8f",
                font="{Yu Mincho} 8 {italic}",
                foreground="#023436",
                text="Made by Claudiu Padure",
            )
            self.credits.pack(anchor="s", side="right")
            self.Header.configure(background="#049a8f", height="80", width="200")
            self.Header.pack(anchor="w", fill="x", side="top")
            self.Header.pack_propagate(0)
            self.SideMenu = tk.Frame(self.Main)
            self.inputMicro = ttk.Label(self.SideMenu)
            self.inputMicro.configure(
                background="#03b5aa",
                font="{Yu Mincho} 11 {bold}",
                foreground="#023436",
                text="Input MIC:",
            )
            self.inputMicro.pack(padx="10", side="top")
            self.inputMic = ttk.Combobox(self.SideMenu,values=list(_ins.keys()))
            self.inputMic.bind('<Configure>', combo_configure)
            self.inputMic.pack(padx="25", side="top")

            _inputMic = self.inputMic.get()

            self.outputMic = ttk.Label(self.SideMenu)
            self.outputMic.configure(
                background="#03b5aa",
                font="{Yu Mincho} 11 {bold}",
                foreground="#023436",
                text="Output MIC:",
            )
            self.OutputMic = ttk.Combobox(self.SideMenu,values=list(_outs.keys()))
            self.outputMic.pack(anchor="n", side="top")
            self.OutputMic.bind('<Configure>', combo_configure)
            self.OutputMic.pack(anchor="n", side="top")
            _outputMic = self.OutputMic.get()

            self.SaveMics = ttk.Button(self.SideMenu,command=lambda: saveInOut(self.inputMic.get(),self.OutputMic.get()))
            self.SaveMics.configure(default="normal", text="Save")
            self.SaveMics.pack(pady="5",side="top")


            self.label5 = ttk.Label(self.SideMenu)
            self.label5.configure(
                background="#03b5aa", font="{Yu Mincho} 10 {}", text="Version 0.0.1"
            )
            self.label5.pack(side="bottom")
            self.label8 = ttk.Label(self.SideMenu)
            self.label8.configure(
                background="#03b5aa",
                font="{Yu Mincho} 12 {bold}",
                foreground="#023436",
                text="Add Sound",
            )
            self.label8.pack(pady="20", side="top")
            self.soundPath = PathChooserInput(self.SideMenu)
            self.soundPath.configure(type="file")
            self.soundPath.pack(anchor="n", side="top")
            self.soundName = ttk.Entry(self.SideMenu)
            self.soundName.configure(font="{Yu Mincho} 12 {}")
            _text_ = """Sound Name"""
            self.soundName.delete("0", "end")
            self.soundName.insert("0", _text_)
            self.soundName.pack(pady="10", side="top")

            self.selectKeybind = ttk.Combobox(self.SideMenu, values=list(keybinds["keybinds"][0].keys()))
            #self.selectKeybind.v = keybinds["keybinds"]
            self.selectKeybind.pack(side="top")
            self.AddButton = ttk.Button(self.SideMenu,command=lambda: addSound(self.soundName.get(), self.selectKeybind.get(), self.soundPath.cget("path")))
            self.AddButton.configure(default="normal", text="Add")
            self.AddButton.pack(pady="5",side="top")
            self.SideMenu.configure(background="#03b5aa", height="200", width="200")
            self.SideMenu.pack(anchor="w", fill="y", side="left")
            self.separator1 = ttk.Separator(self.Main)
            self.separator1.configure(orient="vertical", takefocus=False)
            self.separator1.pack(fill="both", side="top")
            self.separator4 = ttk.Separator(self.Main)
            self.separator4.configure(orient="vertical")
            self.separator4.pack(fill="y", side="left")
            self.sounds = tk.Frame(self.Main)
            self.soundZone = TkScrolledFrame(self.sounds, scrolltype="vertical")

            # Sound Holder
            #listZone = self.soundZone
            #print(listZone.innerframe)
            DisplaySound(self.soundZone)
            ################

            self.soundZone.innerframe.configure(background="#037971")
            self.soundZone.configure(usemousewheel=True)
            self.soundZone.pack(expand="true", fill="both", side="top")
            self.sounds.configure(background="#037971", height="200", width="200")
            self.sounds.pack(anchor="center", expand="true", fill="both", side="bottom")
            self.Main.configure(background="#00bfb3", height="200", width="200")
            self.Main.pack(anchor="center", expand="true", fill="both", side="top")
            self.toplevel3.configure(background="#690f96", height="200", width="200")
            self.toplevel3.geometry("800x600")
            self.toplevel3.minsize(800, 600)

            # Main widget

            def callback():
                #p.terminate()
                #p2.terminate()
                self.toplevel3.destroy()
                stop()


            self.toplevel3.protocol("WM_DELETE_WINDOW", callback)

            self.mainwindow = self.toplevel3
            #p = subprocess.Popen('mainSound.exe')
            #p2 = subprocess.Popen('inputPass.exe')


        def run(self):

            self.mainwindow.mainloop()

    sh = []
    btns = []



    def DisplaySound(listZone):
        for i in range(len(sounds["sounds"])):
            SoundHolder = tk.Frame(listZone.innerframe)
            sh.append(SoundHolder)
            SoundName = ttk.Label(SoundHolder)
            #Name
            SoundName.configure(
                background="#03b5aa", font="{Yu Mincho} 12 {bold}", text=sounds["sounds"][i]["name"]
            )
            SoundName.pack(padx="10", side="left")
            keybindText = ttk.Label(SoundHolder)
            #Keybind
            keybindText.configure(
                background="#03b5aa", font="{Yu Mincho} 9 {bold}", text=sounds["sounds"][i]["keybind"]
            )
            keybindText.pack(padx="20", side="left")
            playSound = ttk.Button(SoundHolder)
            playSound.configure(text="Play Sound")
            playSound.pack(padx="10", side="right")
            delete = ttk.Button(SoundHolder, command=lambda c=i: delwrite_json(c) )
            delete.configure(text=i)
            btns.append(delete)
            delete.pack(side="right")
            SoundHolder.configure(background="#03b5aa", height="25", width="200")
            SoundHolder.pack(pady="5",padx="5",fill="x", side="top")

            SoundHolder.pack_propagate(0)

    def delwrite_json(toRemoveId, filename='json/sounds.json'):
        file_data = json.load(open(filename))
        del file_data["sounds"][toRemoveId]
        # Join new_data with file_data inside emp_details
        #file_data["sounds"].append(new_data)

        #for i in range(len(file_data)):
        #    if(file_data["sounds"][i]['id'] == toRemoveId):
        #        file_data["sounds"].pop(i)

        # Sets file's current position at offset.
        #file.seek(0)
        # convert back to json.
        open(filename, "w").write(
            json.dumps(file_data, sort_keys=True, indent=4, separators=(',', ': '))
        )
        updateList()
        #json.dump(file_data, file, indent = 4)
    

    def write_json(new_data, filename='json/sounds.json'):
        with open(filename,'r+') as file:
              # First we load existing data into a dict.
            file_data = json.load(file)
            # Join new_data with file_data inside emp_details
            file_data["sounds"].append(new_data)
            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent = 4)
    
    def write_json_inout(new_data, name, filename='json/settings.json'):

        with open(filename,'r+') as file:
              # First we load existing data into a dict.
            file_data = json.load(file)
            # Join new_data with file_data inside emp_details
            file_data["saved"][0][name] = new_data
            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent = 4)
            file.truncate()
    
        # python object to be appended

    def updateList():
        global sounds
        with open('json/sounds.json') as json_file:
            sounds = json.load(json_file)
        for i in range(len(sh)):
            sh[i].destroy()
        DisplaySound()
    if __name__ == "__main__":
        app = GuiApp()
        app.run()


def startSound():
    talk = True
    p = None
    soundMain = None

    deviceName = None
    with open('json/sounds.json') as json_file:
        soundMain = json.load(json_file)

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
        try:
            for i in range(len(soundMain["sounds"])):
                if list(soundMain["sounds"][i].values())[3] == key.vk :
                    print(soundMain["sounds"][i]["name"])

                    playSound(soundMain["sounds"][i]["file"])

        except:
            pass


    listener = Listener(on_press=on_press)
    listener.start()

    print("######### START TALKING #########")
p1 = threading.Thread(target=userInterface)
p = threading.Thread(target=audioStart, daemon=True)
p2 = threading.Thread(target=startSound, daemon=True)
p.start()
p1.start()
p2.start()