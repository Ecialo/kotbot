# -*- coding: utf-8 -*-

import string
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
        self.chat_feed = {}
        self.http_client = httpclient.AsyncHTTPClient()

    # def on

    @gen.coroutine
    def on_text(self, message):
        # id_ = message.message_id
        text = message.text
        if text.startswith("/start"):
            yield self.handle_start(message)
        elif text.startswith("/help"):
            yield self.handle_help(message)
        elif text.lower().count("кис") >= 3:
            yield self.handle_start(message)
        # elif text.startswith("/tryapka"):
        elif text.lower().rstrip(string.punctuation) == "брысь":
            yield self.handle_tryapka(message)
        # elif text.startswith("/feed"):
        #     yield self.handle_feed(message)
        elif "куша" in text.lower():
            yield self.handle_feed(message)
        elif "кот" in text.lower():
            yield self.handle_cats(message)

        # yield self.send_message(chat_id=chat.id_, text=text)

    @gen.coroutine
    def handle_start(self, message):
        self.chat_feed[message.chat.id_] = 3
        chat = message.chat
        yield self.send_message(chat_id=chat.id_, text="Мур-мур-мур...")
        ioloop.IOLoop.current().call_later(100, self.hunger, chat.id_)


    @gen.coroutine
    def handle_help(self, message):
        chat = message.chat
        yield self.send_message(chat_id=chat.id_, text="Котик реагирует на других котиков, если не обижен, "
                                                       "любит кушать и его можно прогнать или поманить")

    @gen.coroutine
    def handle_cats(self, message):
        chat = message.chat
        id_ = message.message_id
        if chat.id_ in self.chat_feed:
            kotimg = yield self.http_client.fetch("http://thecatapi.com/api/images/get?type=jpg")
            # img = io.BytesIO(kotimg.body)
            img_to_send = BufferFile(kotimg.buffer)
            yield self.send_photo(chat.id_, img_to_send, reply_to_message_id=id_)
        else:
            self.send_message(chat_id=chat.id_, text="ШшШшшШШ!!!", reply_to_message_id=id_)

    @gen.coroutine
    def handle_tryapka(self, message):
        chat = message.chat
        if chat.id_ in self.chat_feed:
            id_ = message.message_id
            self.chat_feed.pop(chat.id_)
            yield self.send_message(chat_id=chat.id_, text="ШшШшшШШ!!!", reply_to_message_id=id_)


    @gen.coroutine
    def handle_feed(self, message):
        chat = message.chat
        if chat.id_ in self.chat_feed:
            id_ = message.message_id
            old_hunger = self.chat_feed[message.chat.id_]
            self.chat_feed[message.chat.id_] = min(old_hunger + 1, 5)
            yield self.send_message(chat_id=chat.id_, text=self.HUNGER_MESSAGE[old_hunger], reply_to_message_id=id_)

    @gen.coroutine
    def hunger(self, chat_id):
        if chat_id in self.chat_feed:
            # now = dt.datetime.now()
            # time_since_last_feed = (now - self.chat_feed[chat_id]).total_seconds()
            ioloop.IOLoop.current().call_later(self.HUNGER[self.chat_feed[chat_id]], self.hunger, chat_id)
            self.chat_feed[chat_id] = max(self.chat_feed[chat_id] - 1, 0)
            yield self.send_message(chat_id=chat_id, text="МЯУ!")


@gen.coroutine
def forever():
    lich = KotBot(TOKEN)
    yield lich.poll()


if __name__ == '__main__':
    ioloop.IOLoop.current().spawn_callback(forever)
    ioloop.IOLoop.current().start()
