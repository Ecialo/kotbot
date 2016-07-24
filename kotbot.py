# -*- coding: utf-8 -*-
from telezombie import (
    api,
    types,
)
from telezombie2 import (
    api as api2
)
from tornado import (
    ioloop,
    gen,
    httpclient,
    web,
)
import os
import teletoken
from catfig import *
from kotchat import kotchat
__author__ = 'ecialo'


TOKEN = teletoken.TOKEN
TOKEN_DEV = teletoken.TOKEN_DEV
PORT = int(os.getenv('PORT', 8000))


class KotHandler(api.TeleHookHandler):

    @gen.coroutine
    def on_text(self, message):
        yield self.application.settings['kotbot'].on_text(message)

    @gen.coroutine
    def post(self, *args, **kwargs):
        try:
            super().post()
        except Exception as ex:
            print(ex)


def check_loudness(text):
    return text.upper() == text


class DKotBot(api2.TeleLich):

    def __init__(self, token):
        self._api = api2.TeleZombie(token)
        self.kot_chats = {}
        self.commands = {
            '/start': self.handle_start,    # Work
            '/add_to_feeder': self.handle_add_to_feeder,
            '/help': self.handle_help,
            '/care': self.handle_care,
            '/stop': self.handle_stop,      # Work
            # '/hunger': self.handle_hunger,
            # '/sleep': self.handle_sleep,
            # '/play': self.handle_play,
        }

    @gen.coroutine
    def on_text(self, message):
        iloop = ioloop.IOLoop.current()
        text = message.text
        chat_id = message.chat.id_
        lotext = text.lower()
        # putext = lotext.strip(string.punctuation)
        if text.startswith(COMMAND_START):
            yield self.commands[COMMAND_START](message)
        elif text.startswith(COMMAND_SYM):
            if message.chat.id_ in self.kot_chats:
                command = self.commands.get(re.search(COMMAND, text).group())
                if command:
                    yield command(message)
        else:
            if message.chat.id_ in self.kot_chats:
                if lotext.endswith(LOUD) or check_loudness(text):
                    yield self.kot_chats[chat_id].kot_wake_up(message)
                if any(((mew_trigger in lotext) for mew_trigger in MEW_TRIGGER)):
                    iloop.spawn_callback(self.kot_chats[chat_id].kot_mew, message)
                if any(((eat_word in lotext) for eat_word in EAT_WORDS)):
                    iloop.spawn_callback(self.kot_chats[chat_id].kot_eat, message)
                elif lotext.count(HELLO_WORD) >= HELLO_COUNT:
                    iloop.spawn_callback(self.kot_chats[chat_id].kot_hello, message)
                elif SCARE_WORD in lotext:
                    iloop.spawn_callback(self.kot_chats[chat_id].kot_scare, message)
                elif any(((cat in lotext) for cat in CAT)):
                    iloop.spawn_callback(self.kot_chats[chat_id].kot_cats_reaction, message)

    @gen.coroutine
    def handle_start(self, message):
        print(message.chat, message.from_)
        chat = message.chat
        if chat.id_ not in self.kot_chats:
            self.kot_chats[chat.id_] = kotchat.KotChat(chat.id_, self)
        self.kot_chats[chat.id_].start(message)

    @gen.coroutine
    def handle_stop(self, message):
        chat = message.chat
        self.kot_chats[chat.id_].stop(message)
        self.kot_chats.pop(chat.id_)

    @gen.coroutine
    def handle_help(self, message):
        chat = message.chat
        yield self.send_message(chat_id=chat.id_, text=HELP_MESSAGE)

    @gen.coroutine
    def handle_add_to_feeder(self, message):
        self.kot_chats[message.chat.id_].add_food_to_feeder(message)

    @gen.coroutine
    def handle_care(self, message):
        self.kot_chats[message.chat.id_].kot_care(message)

    @gen.coroutine
    def handle_hunger(self, message):
        self.kot_chats[message.chat.id_].kot_want_eat()

    @gen.coroutine
    def handle_sleep(self, message):
        self.kot_chats[message.chat.id_].kot_want_sleep()

    @gen.coroutine
    def handle_play(self, message):
        self.kot_chats[message.chat.id_].kot_want_care()

    @gen.coroutine
    def run(self, polling=True):
        if polling:
            yield self.poll()
        else:
            yield self.listen(
                'https://{ip}/{token}'.format(
                    ip=teletoken.IP,
                    token=teletoken.TOKEN,
                ),
                cert=teletoken.CERT
            )
            application = web.Application(
                [
                    (r"/{token}".format(token=teletoken.TOKEN), KotHandler)
                ],
                kotbot=self,
            )
            application.listen(PORT)


class KotBot(api2.TeleLich):

    def __init__(self, token):
        super().__init__(token)
        self.kot_chats = {}
        self.commands = {
            "/start": self.handle_start,
            "/help": self.handle_help,
            "/stop": self.handle_stop,
            # "/add_to_feeder": self.handle_add_to_feeder,
            # "/care": self.handle_care,

        }

    @gen.coroutine
    def on_text(self, message):
        chat_id = message.chat.id_
        text = message.text
        loop = ioloop.IOLoop.current()
        kotchat_exist = message.chat.id_ in self.kot_chats
        if text.startswith(COMMAND_START):
            yield self.commands[COMMAND_START](message)
        elif text.startswith(COMMAND_SYM) and kotchat_exist:
            command = self.commands.get(re.search(COMMAND, text).group())
            if command:
                yield command(message)
        elif kotchat_exist:
            loop.spawn_callback(self.kot_chats[chat_id].on_text, message)

    @gen.coroutine
    def handle_start(self, message):
        chat_id = message.chat.id_
        # loop = ioloop.IOLoop.current()
        if chat_id in self.kot_chats:
            self.kot_chats[chat_id] = kotchat.KotChat(chat_id, self)
            yield self.send_message(
                chat_id,
                START_MESSAGE,
                parse_mode=api2.PARSE_MODE_HTML
            )
        else:
            yield self.send_message(
                chat_id,
                ALREADY_CAT_MESSAGE,
                parse_mode=api2.PARSE_MODE_HTML
            )

    @gen.coroutine
    def handle_help(self, message):
        yield self.send_message(
            message.chat.id_,
            HELP_MESSAGE
        )

    @gen.coroutine
    def handle_stop(self, message):
        chat_id = message.chat.id_
        self.kot_chats[chat_id].stop()
        self.kot_chats.pop(message.chat.id_)
        yield self.send_message(
            chat_id,
            STOP_MESSAGE,
            parse_mode=api2.PARSE_MODE_HTML
        )

    @gen.coroutine
    def run(self, polling=True):
        if polling:
            yield self.poll()
        else:
            yield self.listen(
                'https://{ip}/{token}'.format(
                    ip=teletoken.IP,
                    token=teletoken.TOKEN,
                ),
                cert=teletoken.CERT
            )
            application = web.Application(
                [
                    (r"/{token}".format(token=teletoken.TOKEN), KotHandler)
                ],
                kotbot=self,
            )
            application.listen(PORT)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--polling", action='store_true')
    parser.add_argument("-d", "--dev", action="store_true")
    args = parser.parse_args()
    token = TOKEN if not args.dev else TOKEN_DEV
    kotbot = KotBot(token)
    ioloop.IOLoop.current().spawn_callback(kotbot.run, args.polling)
    ioloop.IOLoop.current().start()
