"""Simple telegram bot for text to speech transformation

"""

import api_methods
from gtts import gTTS
from time import sleep


def tospeech(text):
    textToSpeech = gTTS(text, lang='ru')
    textToSpeech.save('audio.mp3')


def logic():
    while mybot.lastmessage != 'стоп':
        try:
            mybot.getupdates()
            #print(mybot.lastmessage)
        except KeyError:
            mybot.sendmessage('Некорректный ввод. Введите текст')
            mybot.read()
            continue
        sleep(2)
        if mybot.lastmessage == '/start':
            mybot.sendmessage('Я трансформирую текст в аудио, напиши текст, и я это озвучу.')
            sleep(2)
            logic()

        tospeech(mybot.lastmessage)
        mybot.sendaudio('audio.mp3')
        sleep(2)
        mybot.read()
        sleep(2)
    else:
        mybot.read()


if __name__ == '__main__':
    mybot = api_methods.Bot()
    logic()
