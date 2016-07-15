# -*- coding: utf-8 -*-

import string
import random as rnd
from collections import (
    defaultdict,
    deque,
)
from telezombie import (
    api,
    types,
)
from tornado import (
    ioloop,
    gen,
    httpclient,
)
import teletoken
__author__ = 'ecialo'

TOKEN = teletoken.TOKEN
MAX_CARMA = 10


class BufferFile(types.InputFile):

    def __init__(self, buffer):
        self.buff = buffer
        self._file_path = "file.jpg"

    @property
    def content_type(self):
        # import mimetypes
        # return mimetypes.guess_type(self._file_path)[0]
        return "image/jpeg"

    @property
    def content(self):
        # with open(self.buff, 'rb') as fin:
        return self.buff.read()

    @property
    def size(self):
        return self.buff.getbuffer().nbytes

    def stream(self, chunk_size=524288):
        # with io.Bopen(self.buff, 'rb') as fin:
        while True:
            chunk = self.buff.read(chunk_size)
            if not chunk:
                break
            yield chunk


class KotChatMember:

    def __init__(self, user):
        self.carma = 3
        self.is_target_for_care = False
        self.user = user


class KotChat:

    KORMUSHKA_OVERFLOW = 'Так как кормушка была переполнена из неё вывалился недоеденный корм, а именно {old_food}'

    def __init__(self, kotbot):
        self.kotbot = kotbot
        self.is_running = False

        self.members = {}
        self.kormushka = deque(maxlen=5)     # TODO переименовать это
        self.is_asleep = False
        self.hunger = 5

    def add_member(self, user):
        self.members[user.id_] = KotChatMember(user)

    @gen.coroutine
    def start(self, message):
        self.is_running = True
        yield self.kotbot.send_message("ПрИвЕтИк!!!")

    @gen.coroutine
    def stop(self, message):
        self.is_running = False
        yield self.kotbot.send_message("ПоКеДовА!!!")

    @gen.coroutine
    def kot_want_care(self):
        while self.is_running:
            pass

    @gen.coroutine
    def kot_want_sleep(self):
        pass

    @gen.coroutine
    def kot_want_eat(self):
        pass

    @gen.coroutine
    def meet_hello(self, message):
        pass

    @gen.coroutine
    def cats_reaction(self, message):
        pass

    @gen.coroutine
    def add_food_to_kormushka(self, message):
        command_text = message.text.split()
        new_food = " ".join(command_text[1::])
        kormushka_overflow = len(self.kormushka) == self.kormushka.maxlen
        self.kormushka.append(new_food)
        base_message = 'Вы добавили "{new_food}" в кормушку.'.format(new_food=new_food)
        if kormushka_overflow:
            old_food = self.kormushka.popleft()
            overflow_message = self.KORMUSHKA_OVERFLOW.format(old_food=old_food)
        else:
            overflow_message = ""
        yield self.kotbot.send_message("\n".join([base_message, overflow_message]))

    @gen.coroutine
    def kot_wake_up(self, message):
        pass

    @gen.coroutine
    def kot_sleep(self, message):
        pass

    @gen.coroutine
    def kot_goodbye(self, message):
        pass

    @gen.coroutine
    def kot_care(self, message):
        pass


class KotBot(api.TeleLich):

    HUNGER = {
        5: 300,
        4: 200,
        3: 120,
        2: 60,
        1: 15,
        0: 2,
    }

    HUNGER_MESSAGE = {
        5: "Няяяям-Няяяяям",
        4: "Ням-Ням-Ням",
        3: "Омномном",
        2: "Омномномномном",
        1: "Омномномчавкхлюп",
        0: "ОМНОМНОМЧАВКНОМХЛЮПЧАВКНОМ"
    }

    def __init__(self, token):
        super(KotBot, self).__init__(token)
        # self.kot_chats = defaultdict(lambda: KotChat(self))
        self.kot_chats = {}
        # self.http_client = httpclient.AsyncHTTPClient()

    # def on

    @gen.coroutine
    def on_text(self, message):
        # id_ = message.message_id
        text = message.text
        if text.startswith("/start"):
            yield self.handle_start(message)
        # elif text.startswith("/help"):
        #     yield self.handle_help(message)
        # elif text.lower().count("кис") >= 3:
        #     yield self.handle_start(message)
        # # elif text.startswith("/tryapka"):
        # elif text.lower().rstrip(string.punctuation) == "брысь":
        #     yield self.handle_tryapka(message)
        # # elif text.startswith("/feed"):
        # #     yield self.handle_feed(message)
        # elif "куша" in text.lower():
        #     yield self.handle_feed(message)
        # elif "кот" in text.lower():
        #     yield self.handle_cats(message)

        # yield self.send_message(chat_id=chat.id_, text=text)

    @gen.coroutine
    def handle_start(self, message):
        # self.chat_feed[message.chat.id_] = 3
        chat = message.chat
        # print(chat)
        # print(message.from_)
        if chat.id_ not in self.kot_chats:
            self.kot_chats[chat.id_] = KotChat(self)
        self.kot_chats[chat.id_].start(message)
        # yield self.send_message(chat_id=chat.id_, text="@Zloe_ALoe улюлюлю")
        # ioloop.IOLoop.current().call_later(100, self.hunger, chat.id_)

    @gen.coroutine
    def handle_stop(self, message):
        chat = message.chat
        self.kot_chats[chat.id_].stop(message)
        self.kot_chats.pop(chat.id_)

    @gen.coroutine
    def handle_help(self, message):
        chat = message.chat
        yield self.send_message(chat_id=chat.id_, text="Котик реагирует на других котиков, если не обижен, "
                                                       "любит кушать и его можно прогнать или поманить")
    #
    # @gen.coroutine
    # def handle_cats(self, message):
    #     chat = message.chat
    #     id_ = message.message_id
    #     if chat.id_ in self.chat_feed:
    #         kotimg = yield self.http_client.fetch("http://thecatapi.com/api/images/get?type=jpg")
    #         # img = io.BytesIO(kotimg.body)
    #         img_to_send = BufferFile(kotimg.buffer)
    #         yield self.send_photo(chat.id_, img_to_send, reply_to_message_id=id_)
    #     else:
    #         yield self.send_message(chat_id=chat.id_, text="ШшШшшШШ!!!", reply_to_message_id=id_)
    #
    # @gen.coroutine
    # def handle_tryapka(self, message):
    #     chat = message.chat
    #     if chat.id_ in self.chat_feed:
    #         id_ = message.message_id
    #         self.chat_feed.pop(chat.id_)
    #         yield self.send_message(chat_id=chat.id_, text="ШшШшшШШ!!!", reply_to_message_id=id_)
    #
    #
    # @gen.coroutine
    # def handle_feed(self, message):
    #     chat = message.chat
    #     if chat.id_ in self.chat_feed:
    #         id_ = message.message_id
    #         old_hunger = self.chat_feed[message.chat.id_]
    #         self.chat_feed[message.chat.id_] = min(old_hunger + 1, 5)
    #         yield self.send_message(chat_id=chat.id_, text=self.HUNGER_MESSAGE[old_hunger], reply_to_message_id=id_)
    #
    # @gen.coroutine
    # def hunger(self, chat_id):
    #     if chat_id in self.chat_feed:
    #         # now = dt.datetime.now()
    #         # time_since_last_feed = (now - self.chat_feed[chat_id]).total_seconds()
    #         ioloop.IOLoop.current().call_later(self.HUNGER[self.chat_feed[chat_id]], self.hunger, chat_id)
    #         self.chat_feed[chat_id] = max(self.chat_feed[chat_id] - 1, 0)
    #         yield self.send_message(chat_id=chat_id, text="МЯУ!")


@gen.coroutine
def forever():
    lich = KotBot(TOKEN)
    yield lich.poll()


if __name__ == '__main__':
    ioloop.IOLoop.current().spawn_callback(forever)
    ioloop.IOLoop.current().start()
