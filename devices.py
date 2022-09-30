import json
import sounddevice as sd
import json

_ins = {}
_outs = {}
file = None
def write_json(new_data, where,filename='json/devices.json'):
        with open(filename,'r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)
            # Join new_data with file_data inside emp_details
            file_data[where].append(new_data)
            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent = 4)
            # python object to be appended


def delete():
    with open('json/devices.json') as f:
        file = json.load(f)

    print(file["inputDevices"][0])
    #file = json.load(open('mainSound/json/devices.json'))
    del file["inputDevices"][0]
    del file["outputDevices"][0]

    open('json/devices.json', "w").write(
        json.dumps(file,sort_keys=True, indent=4)
    )
delete()
#"Windows DirectSound"
for i in range(len(sd.query_devices())):
        if(sd.query_devices()[i]['hostapi'] == 1):
            if(sd.query_devices()[i]['max_input_channels'] > 0):
                _ins[sd.query_devices()[i]['name']] = i
            else:
                _outs[sd.query_devices()[i]['name']] = i

#_ins = dict((v, k) for k, v in _ins.items())
#_outs = dict((v, k) for k, v in _outs.items())
write_json(_ins,"inputDevices")
write_json(_outs,"outputDevices")


