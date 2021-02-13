"""Simple script with methods for communication with telegram bot API.

For now it can:
-receive text messages
-send text, audio
-edit own messages(for inline keyboard messages)
-inline keyboard
-custom keyboard

Token should be placed in the 'token.txt' file in the script directory.
"""

import requests

apiurl = 'https://api.telegram.org/bot'
token = ''

with open('token.txt', 'rt') as f:
    token = f.read()

token = token.strip()


class Bot:  # TODO Payment methods
    #  most of variables cannot be set on start, so just defining them
    def __init__(self, api=apiurl, t=token):
        self.api = api
        self.t = t
        self.server_reply = None
        self.max_update_id = None
        self.chatid = None
        self.lastmessage = None
        self.keyboard1 = None
        self.message_id = None
        self.callback_data = None

    #  method for testing purposes
    def getme(self):
        get_me = requests.get(self.api + self.t + '/getme').content
        get_me = Bot.reformat(get_me)
        return get_me

    #  pull replies and set useful variables
    def getupdates(self, timeout=60):  # TODO long pull and handle 0-len answer
        query = f'{self.api}{self.t}/getupdates?timeout={timeout}'
        query = requests.get(query).content
        query = Bot.reformat(query)
        query = query['result']

        if len(query) == 0:
            return self.getupdates()

        self.server_reply = query[-1]
        self.max_update_id = self.server_reply['update_id']

        if 'callback_query' in self.server_reply:
            self.chatid = self.server_reply['callback_query']['message']['chat']['id']
            self.message_id = self.server_reply['callback_query']['message']['message_id']
            self.callback_data = (self.server_reply['callback_query']['message']['reply_markup']
                                                   ['inline_keyboard'][-1][-1]['callback_data'])
            return self.callback_data
        else:
            self.chatid = self.server_reply['message']['chat']['id']
            self.lastmessage = self.server_reply['message']['text']

    #  reads unread messages
    def read(self):
        requests.get(f'{self.api}{self.t}/getupdates?offset={str(self.max_update_id + 1)}')

    #  message sending method
    def sendmessage(self, text, chatid=None, keyboard=None):
        if chatid is None:
            chatid = str(self.chatid)
        query = f'{self.api}{self.t}/sendmessage?chat_id={chatid}&text={text}'

        if keyboard is not None:
            query += keyboard
        requests.get(query)

    #  sends audio
    def sendaudio(self, audio, chat_id=None):
        if chat_id is None:
            chat_id = self.chatid
        file = {'audio': open(audio, 'rb')}
        requests.post(f'{self.api}{self.t}/sendaudio?chat_id={chat_id}', files=file)

    #  edits messages for inline keyboard conversation
    def editmessagetext(self, text, chat_id=None, message_id=None, keyboard=None):
        if chat_id is None:
            chat_id = self.chatid
        if message_id is None:
            message_id = self.message_id
        query = f'{self.api}{self.t}/editMessageText?message_id={message_id}&chat_id={chat_id}&text={text}'
        if keyboard is not None:
            query += keyboard
        requests.get(query)

    #  keyboard builder (ReplyKeyboardMarkup)
    def keyboard(self, *buttons):
        self.keyboard1 = '&reply_markup={"keyboard" : ['
        end = ']}'
        for button in buttons:
            button = f'["{button}"], '
            self.keyboard1 += button
        self.keyboard1 = self.keyboard1[:-2]
        self.keyboard1 += end
        return self.keyboard1

    #  inline keyboard builder
    def inline(self, *buttons):
        self.keyboard1 = '&reply_markup={"inline_keyboard" : ['
        end = ']}'
        counter = 1
        for button in buttons:
            button = '[{"text" : ' + f'"{button}", "callback_data" : "{counter}"' + '}], '
            self.keyboard1 += button
            counter += 1
        self.keyboard1 = self.keyboard1[:-2] + end
        return self.keyboard1

    #  reformats the answer from the telegram server
    @staticmethod
    def reformat(query):
        query = query.decode("utf-8")
        query = query.replace('true', 'True').replace('false', 'False')
        query = eval(query)
        return query
