"""
This is from a python tutorial from: https://github.com/Uberi/speech_recognition
"""
import speech_recognition as sr

# Record Audio
r = sr.Recognizer()

with sr.Microphone() as source:
    print("Say something!")
    r.adjust_for_ambient_noise(source, duration=1)
    audio = r.listen(source,timeout=5)

# Speech recognition using Google Speech Recognition
try:
    # for testing purposes, we're just using the default API key
    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
    # instead of `r.recognize_google(audio)`
    s=r.recognize_google(audio)
    if(len(set(s))>0):
        print("You said: " + s)
    elif s==None:
        print('Nothing was said')
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))