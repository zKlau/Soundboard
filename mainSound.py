from pickle import TRUE
import time
from pygame import mixer
from pynput.keyboard import Key, Listener, KeyCode
import json
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
from numpy import append
import queue
import ffmpeg
import youtube_dl

with open('package.json') as json_file:
    packageInfo = json.load(json_file)

global volumeMic
with open('json/settings.json') as json_file:
    defaultVolume = json.load(json_file)
    volumeMic = defaultVolume["saved"][0]["micVolume"]

userMicrophoneStream = None
userTalk = False

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

def startSound():
    talk = True
    p = None
    global soundMain
    soundMain = None
    global deviceName
    deviceName = None
    with open('json/sounds.json') as json_file:
        soundMain = json.load(json_file)

    with open('json/settings.json') as json_file:
        deviceName = json.load(json_file)

    #print(deviceName["saved"][0]["outputName"])
    def stopTalking():
        p.terminate()
    def startTalking():
        global talk
        talk = True
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

        with open('json/sounds.json') as json_file:
            soundMain = json.load(json_file)
        if "https" not in name:
            mixer.pre_init(44100, -16, 1, 512)
            mixer.init(devicename = deviceName["saved"][0]["outputName"]) # Initialize it with the correct device
            mixer.music.load(name) # Load the mp3
            mixer.music.set_volume(soundMain["sounds"][id]["volume"])
            mixer.music.play() # Play it
        else:
            if userTalk:
                userMicrophoneStream.abort()
            urlSoundFile(name,id)

    
    global muted
    muted = False

    def on_press(key):
        global volumeMic
        global deviceName
        global muted
        
        try:
            
            if key.vk == deviceName["saved"][0]["muteKeybind"]:
                if muted == False:
                    if userTalk:
                        userMicrophoneStream.abort()
                    muted = True
                elif muted == True:
                    if userTalk:
                        userMicrophoneStream.start()
                    muted = False
            else:
                with open('json/sounds.json') as json_file:
                    soundMain = json.load(json_file)
                for i in range(len(soundMain["sounds"])):
                    #print(list(soundMain["sounds"][i].values())[3])
                    if list(soundMain["sounds"][i].values())[3] == key.vk :
                        #print(soundMain["sounds"][i]["name"])

                        playSound(soundMain["sounds"][i]["file"],i)

        except:
            pass


    listener = Listener(on_press=on_press)
    listener.start()

    print("######### START TALKING #########")

def user_interface():
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

    def changeVolume(vol):
        global volumeMic
        volumeMic = vol/10
        write_json_inout(volumeMic,"micVolume")
        #print("Volume set to " + str(vol) + "%")

    def changeVolumeSound(vol,id):
        write_json_soundVolume(vol,id)

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
                "keybind": keybind,
                "volume": 1
            }
        write_json(x)
        updateList()
        #print("added")

    def open_popup(win):
        top = Toplevel(win)
        top.geometry("575x105")
        top.title("Restart the program")
        top.configure(
                background="#03b5aa",
            )
        #Label(top, text= "Do you wish to restart?", font=('Mistral 18 bold'))
        label5 = ttk.Label(top)
        label5.configure(
                background="#03b5aa", font="{Yu Mincho} 15 {bold}", text="To save the settings you need to restart the program!"
            )
        label5.pack(side="top")

        exitPop = ttk.Button(top)
        exitPop.configure(default="normal", text="Restart Now", command= lambda: win.destroy())
        exitPop.pack(pady="5",side="top")

        backPop = ttk.Button(top)
        backPop.configure(default="normal", text="Later", command= lambda: top.destroy())
        backPop.pack(pady="5",side="top")

    def combo_configure(event):
        combo = event.widget
        style = ttk.Style()

        long = max(combo.cget('values'), key=len)

        font = tkfont.nametofont(str(combo.cget('font')))
        width = max(0,font.measure(long.strip() + '0') - combo.winfo_width())

        style.configure('TCombobox', postoffset=(0,0,width,0))

    def saveInOut(input,output,win):
        for i in range(len(_ins)):
            if list(_ins)[i] == input:
                write_json_inout(_ins[list(_ins)[i]],"inputMic")
        for i in range(len(_outs)):
            if list(_outs)[i] == output:
                write_json_inout(_outs[list(_outs)[i]],"outputMic")
                write_json_inout(output,"outputName")
        open_popup(win)

    global listZone
    listZone = None
    
    

    class GuiApp:
        def __init__(self, master=None):
            global listZone
            # build ui
            self.toplevel3 = tk.Tk() if master is None else tk.Toplevel(master)
            self.toplevel3.title(packageInfo["nick"])
            self.Main = tk.Frame(self.toplevel3)
            self.Header = tk.Frame(self.Main)
            self.label3 = ttk.Label(self.Header)
            self.label3.configure(
                anchor="s",
                background="#049a8f",
                font="{Yu Mincho} 20 {bold}",
                foreground="#023436",
            )
            self.label3.configure(text=packageInfo["nick"])
            self.label3.pack(anchor="w", padx="15", side="top")
            self.separator7 = ttk.Separator(self.Header)
            self.separator7.configure(orient="horizontal")
            self.separator7.pack(fill="x", side="bottom")
            self.credits = ttk.Label(self.Header)
            self.credits.configure(
                background="#049a8f",
                font="{Yu Mincho} 8 {italic}",
                foreground="#023436",
                text="Made by " + packageInfo["author"],
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

            self.SaveMics = ttk.Button(self.SideMenu,command=lambda: saveInOut(self.inputMic.get(),self.OutputMic.get(),self.toplevel3))
            self.SaveMics.configure(default="normal", text="Save")
            self.SaveMics.pack(pady="5",side="top")


            self.label5 = ttk.Label(self.SideMenu)
            self.label5.configure(
                background="#03b5aa", font="{Yu Mincho} 10 {}", text="Version " + packageInfo["version"]
            )
            self.label5.pack(side="bottom")
            self.label8 = ttk.Label(self.SideMenu)
            self.label8.configure(
                background="#03b5aa",
                font="{Yu Mincho} 12 {bold}",
                foreground="#023436",
                text="Add Sound",
            )
            self.label8.pack(pady="5", side="top")
            self.soundPath = PathChooserInput(self.SideMenu)
            self.soundPath.configure(type="file")
            self.soundPath.pack(anchor="n", side="top")
            self.soundName = ttk.Entry(self.SideMenu)
            self.soundName.configure(font="{Yu Mincho} 12 {}")
            _text_ = """Sound Name"""
            self.soundName.delete("0", "end")
            self.soundName.insert("0", _text_)
            self.soundName.pack(pady="2", side="top")

            self.selectKeybind = ttk.Combobox(self.SideMenu, values=list(keybinds["keybinds"][0].keys()))
            #self.selectKeybind.v = keybinds["keybinds"]
            self.selectKeybind.pack(side="top")
            self.AddButton = ttk.Button(self.SideMenu,command=lambda: addSound(self.soundName.get(), self.selectKeybind.get(), self.soundPath.cget("path")))
            self.AddButton.configure(default="normal", text="Add")
            self.AddButton.pack(pady="2",side="top")
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
            listZone = self.soundZone
            #print(listZone.innerframe)
            DisplaySound()
            ################


            self.MicVolume = ttk.Label(self.SideMenu)
            self.MicVolume.configure(
                background="#03b5aa",
                font="{Yu Mincho} 12 {bold}",
                foreground="#023436",
                text="Microphone volume",
            )
            self.MicVolume.pack(pady="10", side="top")
            self.MicVolumeScale = tk.Scale(self.SideMenu)
            self.MicVolumeScale.configure(
                activebackground="#023436",
                background="#03b5aa",
                borderwidth="5",
                font="{Yu Mincho} 12 {}",
            )
            self.MicVolumeScale.configure(
                foreground="#023436",
                highlightbackground="#03b5aa",
                highlightcolor="#023436",
                orient="horizontal",
            )
            self.MicVolumeScale.configure(relief="raised", troughcolor="#049a8f")
            self.MicVolumeScale.pack(ipadx="25", side="top")
            self.micVolumeSave = tk.Button(self.SideMenu, command = lambda: changeVolume(self.MicVolumeScale.get()))
            self.micVolumeSave.configure(font="{Yu Mincho} 11 {}", text="Save")
            self.micVolumeSave.pack(pady="5", side="top")


            self.label1 = tk.Label(self.SideMenu)
            self.label1.configure(
                background="#03b5aa",
                font="{Yu Mincho} 12 {bold}",
                foreground="#023436",
                text="Mute MIC keybind",
            )
            self.label1.pack(side="top")
            self.MuteKeybind = ttk.Combobox(self.SideMenu,values=list(keybinds["keybinds"][0].keys()))
            self.MuteKeybind.pack(side="top")
            self.SaveMute = tk.Button(self.SideMenu, command= lambda: write_json_inout(keybinds["keybinds"][0][self.MuteKeybind.get()], "muteKeybind"))
            self.SaveMute.configure(font="{Yu Mincho} 11 {}", text="Save")
            self.SaveMute.pack(pady="5", side="top")



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
                print("exit")
                #sys.exit()


            self.toplevel3.protocol("WM_DELETE_WINDOW", callback)

            self.mainwindow = self.toplevel3
            #p = subprocess.Popen('mainSound.exe')
            #p2 = subprocess.Popen('inputPass.exe')


        def run(self):

            self.mainwindow.mainloop()

    sh = []
    btns = []



    def DisplaySound():
        global sounds
        volumes = []
        with open('json/sounds.json') as json_file:
            sounds = json.load(json_file)
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
            #playSound = ttk.Button(SoundHolder)
            #playSound.configure(text="Play Sound")
            #playSound.pack(padx="10", side="right")
            
            delete = ttk.Button(SoundHolder, command=lambda c=i: delwrite_json(c) )
            delete.configure(text="X", width="5")
            btns.append(delete)
            delete.pack(side="right")

            soundSaveVol = ttk.Button(SoundHolder, command= lambda c=i: changeVolumeSound(volumes[c].get(),c))
            soundSaveVol.configure(text="✔", width="5")
            soundSaveVol.pack(side="right", padx="5")

            soundVolume = ttk.Scale(SoundHolder)
            soundVolume.configure(orient="horizontal")
            soundVolume.pack(pady="3", side="top")
            volumes.append(soundVolume)
            SoundHolder.configure(background="#03b5aa", height="25", width="200")
            SoundHolder.pack(pady="5",padx="5",fill="x", side="top")

            SoundHolder.pack_propagate(0)

    def delwrite_json(toRemoveId, filename='json/sounds.json'):
        file_data = json.load(open(filename))
        del file_data["sounds"][toRemoveId]
        
        open(filename, "w").write(
            json.dumps(file_data, sort_keys=True, indent=4, separators=(',', ': '))
        )
        updateList()
    

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
    def write_json_soundVolume(new_data,id, filename='json/sounds.json'):

        with open(filename,'r+') as file:
              # First we load existing data into a dict.
            file_data = json.load(file)
            # Join new_data with file_data inside emp_details
            file_data["sounds"][id]["volume"] = new_data
            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent = 4)
            file.truncate()
    
        # python object to be appended

    def updateList():
        with open('json/sounds.json') as json_file:
            sounds = json.load(json_file)
        for i in range(len(sh)):
            sh[i].destroy()
        DisplaySound()
    if __name__ == "__main__":
        app = GuiApp()
        app.run()

guiThread = threading.Thread(target=user_interface)
userVoiceThread = threading.Thread(target=voiceStart, daemon=True)
soundThread = threading.Thread(target=startSound, daemon=True)

if userTalk:
    userVoiceThread.start()

guiThread.start()
soundThread.start()