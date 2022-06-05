import sounddevice as sd
import soundfile as sf
import librosa
import audioread

data = audioread.audio_open('sounds/culcat.mp3')
sd.default.device = 14
sd.play(data)
sd.wait()