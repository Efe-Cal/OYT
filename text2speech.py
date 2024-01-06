from time import sleep
from gtts import gTTS
import os
import win32gui, win32con, win32api
from mutagen.mp3 import MP3


def text2speech(text, language='tr'):
    tts = gTTS(text=text, lang=language, lang_check=False)
    tts.save("./output.mp3")  # Save speech to a file
    os.system("start output.mp3")
    sleep(0.5)
    length = MP3("./output.mp3").info.length
    
    the_program_to_hide = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(the_program_to_hide , win32con.SW_HIDE)
    sleep(length+1)
    win32api.PostMessage(the_program_to_hide, win32con.WM_CLOSE, 0, 0)

    os.remove("output.mp3")