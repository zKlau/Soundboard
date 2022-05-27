import sounddevice as sd

for i in range(len(sd.query_devices())):
        print(sd.query_devices()[i])