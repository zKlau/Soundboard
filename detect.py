from pygame import mixer
import pygame._sdl2 as sdl2

mixer.init() # Initialize the mixer, this will allow the next command to work

# Returns playback devices, Boolean value determines whether they are Input or Output devices.
print("Inputs:", sdl2.audio.get_audio_device_names(True))
print("Outputs:", sdl2.audio.get_audio_device_names(False))

mixer.quit() # Quit the mixer as it's initialized on your main playback device