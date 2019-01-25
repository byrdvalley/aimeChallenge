import wave
import io
import speech_recognition as sr
import time
from pygame import mixer
import matplotlib
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt
from pyAudioAnalysis import audioSegmentation as aS

r = sr.Recognizer()


###############
# Helper functions
###############

# first variable control start of the recording
# second variable control the end of the recording
global controls
controls = [False, False]


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False


numbers = ["one", "two", "to", "too", "three", "four", "five", "six"]
def isNumber(text):
    num = False
    for n in numbers:
        if n in text:
            num = True
    return num or is_number(text)

def get_wav_data_fromRAW(raw_data, convert_rate=None, convert_width=None):
    """
    Returns a byte string representing the contents of a WAV file containing the audio represented by the ``AudioData`` instance.

    If ``convert_width`` is specified and the audio samples are not ``convert_width`` bytes each, the resulting audio is converted to match.

    If ``convert_rate`` is specified and the audio sample rate is not ``convert_rate`` Hz, the resulting audio is resampled to match.

    Writing these bytes directly to a file results in a valid `WAV file <https://en.wikipedia.org/wiki/WAV>`__.
    """
    sample_rate = 44100
    sample_width = 2

    # generate the WAV file contents
    with io.BytesIO() as wav_file:
        wav_writer = wave.open(wav_file, "wb")
        try:  # note that we can't use context manager, since that was only added in Python 3.4
            wav_writer.setframerate(sample_rate)
            wav_writer.setsampwidth(sample_width)
            wav_writer.setnchannels(1)
            wav_writer.writeframes(raw_data)
            wav_data = wav_file.getvalue()
        finally:  # make sure resources are cleaned up
            wav_writer.close()
    return wav_data

def show_spkDia(flags, mt_step=0.2):
    (segs, classes) = aS.flags2segs(flags, 0.2)
    for s in range(segs.shape[0]):
        print("Speaker #{} : from {} (sec) to {} (sec)\n".format( int(classes[s]), segs[s,0], segs[s,1]))

"""        
def callback(recognizer, audio):
    # received audio data, now we'll recognize it using Google Speech Recognition
    try:
        text = recognizer.recognize_google(audio)
        if "meeting is over" in text:
            controls[1] = False
            print("OK let's end the recording")
        elif "start the meeting" in text:
            controls[0] = True
            print("OK let's start recording")
    except sr.UnknownValueError:
        print("Could not understand what you said")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
"""

def callback(recognizer, audio):
    global start
    global end
    global texts
    
    # received audio data, now we'll recognize it using Google Speech Recognition
    try:
        text = recognizer.recognize_google(audio)
        print(text)
        if "start the meeting" in text:
            start = True
        elif start and not end:
            texts.append(text)
        elif "meeting is over" in text:
            end = True
            
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

#########################
# MAIN
#########################
global start
global end
global texts

start = False
end = False
texts = []

r = sr.Recognizer()
m = sr.Microphone()
stop_listening = r.listen_in_background(m, callback)

while True: 
    time.sleep(3)
