import pyttsx3
import speech_recognition as sr
from datetime import date
import time
import webbrowser
import datetime
from pynput.keyboard import Key, Controller
import pyautogui
import sys
import os
from os import listdir
from os.path import isfile, join
import smtplib
import wikipedia
import Gesture_Controller
#import Gesture_Controller_Gloved as Gesture_Controller
import app
from threading import Thread


# ================== Object Initialization ==================
TODAY = date.today()
RECOGNIZER = sr.Recognizer()
KEYBOARD_CONTROLLER = Controller()
SPEECH_ENGINE = pyttsx3.init('sapi5')
SPEECH_ENGINE = pyttsx3.init()
VOICES = SPEECH_ENGINE.getProperty('voices')
SPEECH_ENGINE.setProperty('voice', VOICES[0].id)

# ================== Configuration Variables ==================
FILE_EXPLORER_ACTIVE = False
CURRENT_FILES = []
CURRENT_PATH = ''
IS_ASSISTANT_AWAKE = True

# ================== Microphone Setup ==================
with sr.Microphone() as source:
        RECOGNIZER.energy_threshold = 500 
        RECOGNIZER.dynamic_energy_threshold = False

# Audio to String
def record_audio():
    with sr.Microphone() as source:
        RECOGNIZER.pause_threshold = 0.8
        recognized_text = ''
        audio = RECOGNIZER.listen(source, phrase_time_limit=5)

        try:
            recognized_text = RECOGNIZER.recognize_google(audio)
        except sr.RequestError:
            reply('Sorry my Service is down. Plz check your Internet connection')
        except sr.UnknownValueError:
            print('cant recognize')
            pass
        return recognized_text.lower()


def reply(audio):
    app.ChatBot.addAppMsg(audio)

    print(audio)
    SPEECH_ENGINE.say(audio)
    SPEECH_ENGINE.runAndWait()


def greet_user():
    hour = int(datetime.datetime.now().hour)

    if hour>=0 and hour<12:
        reply("Good Morning!")
    elif hour>=12 and hour<18:
        reply("Good Afternoon!")   
    else:
        reply("Good Evening!")  
        
    reply("I am Jarvis, how may I help you?")

# Executes Commands (input: string)
def respond(voice_data):
    global FILE_EXPLORER_ACTIVE, CURRENT_FILES, IS_ASSISTANT_AWAKE, CURRENT_PATH
    print(voice_data)
    voice_data.replace('jarvis','')
    app.eel.addUserMsg(voice_data)

    if IS_ASSISTANT_AWAKE==False:
        if 'wake up' in voice_data:
            IS_ASSISTANT_AWAKE = True
            greet_user()

    # STATIC CONTROLS
    elif 'hello' in voice_data:
        greet_user()

    elif 'what is your name' in voice_data:
        reply('My name is Jarvis!')

    elif 'date' in voice_data:
        reply(TODAY.strftime("%B %d, %Y"))

    elif 'time' in voice_data:
        reply(str(datetime.datetime.now()).split(" ")[1].split('.')[0])

    elif 'search' in voice_data:
        reply('Searching for ' + voice_data.split('search')[1])
        url = 'https://google.com/search?q=' + voice_data.split('search')[1]
        try:
            webbrowser.get().open(url)
            reply('This is what I found Sir')
        except:
            reply('Please check your Internet')

    elif 'location' in voice_data:
        reply('Which place are you looking for ?')
        temp_audio = record_audio()
        app.eel.addUserMsg(temp_audio)
        reply('Locating...')
        url = 'https://google.nl/maps/place/' + temp_audio + '/&amp;'
        try:
            webbrowser.get().open(url)
            reply('This is what I found Sir')
        except:
            reply('Please check your Internet')

    elif ('bye' in voice_data) or ('by' in voice_data):
        reply("Good bye Sir! Have a nice day.")
        IS_ASSISTANT_AWAKE = False

    elif ('exit' in voice_data) or ('terminate' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
        app.ChatBot.close()
        #sys.exit() always raises SystemExit, Handle it in main loop
        sys.exit()
        
    
    # DYNAMIC CONTROLS
    elif 'launch gesture recognition' in voice_data:
        if Gesture_Controller.GestureController.gc_mode:
            reply('Gesture recognition is already active')
        else:
            gc = Gesture_Controller.GestureController()
            t = Thread(target = gc.start)
            t.start()
            reply('Launched Successfully')

    elif ('stop gesture recognition' in voice_data) or ('top gesture recognition' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
            reply('Gesture recognition stopped')
        else:
            reply('Gesture recognition is already inactive')
        
    elif 'copy' in voice_data:
        with KEYBOARD_CONTROLLER.pressed(Key.ctrl):
            KEYBOARD_CONTROLLER.press('c')
            KEYBOARD_CONTROLLER.release('c')
        reply('Copied')
          
    elif 'page' in voice_data or 'pest'  in voice_data or 'paste' in voice_data:
        with KEYBOARD_CONTROLLER.pressed(Key.ctrl):
            KEYBOARD_CONTROLLER.press('v')
            KEYBOARD_CONTROLLER.release('v')
        reply('Pasted')
        
    # File Navigation (Default Folder set to C://)
    elif 'list' in voice_data:
        counter = 0
        CURRENT_PATH = 'C://'
        CURRENT_FILES = listdir(CURRENT_PATH)
        filestr = ""
        for f in CURRENT_FILES:
            counter+=1
            print(str(counter) + ':  ' + f)
            filestr += str(counter) + ':  ' + f + '<br>'
        FILE_EXPLORER_ACTIVE = True
        reply('These are the files in your root directory')
        app.ChatBot.addAppMsg(filestr)
        
    elif FILE_EXPLORER_ACTIVE == True:
        counter = 0   
        if 'open' in voice_data:
            if isfile(join(CURRENT_PATH,CURRENT_FILES[int(voice_data.split(' ')[-1])-1])):
                os.startfile(CURRENT_PATH + CURRENT_FILES[int(voice_data.split(' ')[-1])-1])
                FILE_EXPLORER_ACTIVE = False
            else:
                try:
                    CURRENT_PATH = CURRENT_PATH + CURRENT_FILES[int(voice_data.split(' ')[-1])-1] + '//'
                    CURRENT_FILES = listdir(CURRENT_PATH)
                    filestr = ""
                    for f in CURRENT_FILES:
                        counter+=1
                        filestr += str(counter) + ':  ' + f + '<br>'
                        print(str(counter) + ':  ' + f)
                    reply('Opened Successfully')
                    app.ChatBot.addAppMsg(filestr)
                    
                except:
                    reply('You do not have permission to access this folder')
                                    
        if 'back' in voice_data:
            filestr = ""
            if CURRENT_PATH == 'C://':
                reply('Sorry, this is the root directory')
            else:
                a = CURRENT_PATH.split('//')[:-2]
                CURRENT_PATH = '//'.join(a)
                CURRENT_PATH += '//'
                CURRENT_FILES = listdir(CURRENT_PATH)
                for f in CURRENT_FILES:
                    counter+=1
                    filestr += str(counter) + ':  ' + f + '<br>'
                    print(str(counter) + ':  ' + f)
                reply('ok')
                app.ChatBot.addAppMsg(filestr)
                   
    else: 
        reply('I am not functioned to do this !')

# ------------------Driver Code--------------------

t1 = Thread(target = app.ChatBot.start)
t1.start()

# Lock main thread until Chatbot has started
while not app.ChatBot.started:
    time.sleep(0.5)

greet_user()
voice_data = None
while True:
    if app.ChatBot.isUserInput():
        #take input from GUI
        voice_data = app.ChatBot.popUserInput()
    else:
        #take input from Voice
        voice_data = record_audio()

    #process voice_data
    if 'jarvis' in voice_data:
        try:
            #Handle sys.exit()
            respond(voice_data)
        except SystemExit:
            reply("Exit Successfull")
            break
        except:
            #some other exception got raised
            print("EXCEPTION raised while closing.") 
            break
    print(voice_data)
