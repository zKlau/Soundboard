import time
from urllib.request import urlopen
from pygame import mixer
from io import BytesIO, StringIO
import youtube_dl
import argparse
import queue
import sys

import ffmpeg
import sounddevice as sd

URL = "https://rr3---sn-gqn-nc1ee.googlevideo.com/videoplayback?expire=1655835175&ei=x7WxYpK9I5TXgQed0InYCQ&ip=2a02%3A2f07%3Ac109%3Aa300%3Ad87e%3Ac0d4%3A100%3Af101&id=o-ACq6_rgqUfKGMWvI0ebTgMMcLiMvp4adrjPCtDxZtG1B&itag=249&source=youtube&requiressl=yes&mh=Yd&mm=31%2C29&mn=sn-gqn-nc1ee%2Csn-c0q7lns7&ms=au%2Crdu&mv=m&mvi=3&pl=39&initcwndbps=1716250&spc=4ocVC84d8Mm8s7CsfhsFHJlDBMxOvls&vprv=1&mime=audio%2Fwebm&ns=cm7Ln7ybaDKnGEOfGL1VVLcG&gir=yes&clen=16592&dur=1.601&lmt=1592899594857462&mt=1655813089&fvip=4&keepalive=yes&fexp=24001373%2C24007246&c=WEB&txp=5411222&n=kv-yBLjCaFLecjwACR&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cspc%2Cvprv%2Cmime%2Cns%2Cgir%2Cclen%2Cdur%2Clmt&sig=AOq0QJ8wRgIhAOAdVcTF5zWA4gtX-DcMUrks4CYd4gcILmSGnF9I8bplAiEA8NCDrP-dQ4Ck7Ja4rW6eXZqvSGZ4je-FP_tC8S2dbgI%3D&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AG3C_xAwRgIhAJME_swDLcjb5ZBomn2iJu7Mf2fncMQ0M8LiOQx9oEXtAiEAnSNFXhlq7bSo5j9ZpbqrjGcETv2vaHjk_e6Wl_aD4uE%3D"
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

print('Getting stream information ...')

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
    


try:
    print('Opening stream ...')
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
        device=14 , channels=channels, dtype='float32',
        callback=callback)
    read_size = args.blocksize * channels * stream.samplesize
    print('Buffering ...')
    for _ in range(args.buffersize):
        q.put_nowait(process.stdout.read(read_size))
    print('Starting Playback ...')
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