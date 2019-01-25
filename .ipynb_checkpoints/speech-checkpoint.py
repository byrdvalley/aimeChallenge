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

        

#########################
# MAIN
#########################
mixer.init()
start_sound = mixer.Sound("start_record.wav")
end_sound = mixer.Sound("end_record.wav")
how_sound = mixer.Sound("howmany.wav")
thanks_sound = mixer.Sound("thanks.wav")

stop = True
l = []
start = False
mixer.init
while(stop):
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("say something")
        audio1 = r.listen(source, phrase_time_limit=10)
        print("time over")
        print("recognition...")
    
    if start:
        l.append(audio1.get_raw_data())        
    try:
        #speech_as_text = r.recognize_sphinx(audio1, keyword_entries=keywords)
        speech_as_text = r.recognize_google(audio1)
        print("text : " + speech_as_text)
        if "meeting is over" in speech_as_text:
            end_sound.play()
            stop = False
            
        elif "start the meeting" in speech_as_text:
            start_sound.play()
            time.sleep(3)
            start = True
            print("OK let's start recording")

    except:
        print("didn't work")
        pass
            

        
time.sleep(3)
# Let AIME ask for how many participants
answered = False
while(not answered):
    with sr.Microphone() as source:
        how_sound.play()
        time.sleep(1)
        r.adjust_for_ambient_noise(source)
        audio2 = r.listen(source)

    try:
        speech_as_text = r.recognize_google(audio2)
        print("text : " + speech_as_text)
        if isNumber(speech_as_text):
            thanks_sound.play()
            time.sleep(5)
            answered = True
            
    except:
        print("was not a number")
        pass
    
binall = b''
for elem in l[:-1]:
    binall += elem


with open("microphone-results_final.wav", "wb+") as f:
    f.write(get_wav_data_fromRAW(binall))

num_part = int(speech_as_text)
sd = aS.speakerDiarization("./microphone-results_final.wav", num_part, mt_size=2.0, mt_step= 0.2, st_win=0.05 ,lda_dim=0)

show_spkDia(sd)