# -*- coding: utf-8 -*-

import string
import random as rnd
import re
import json
from collections import (
    defaultdict,
    deque,
)
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
)
import teletoken
from catfig import *
__author__ = 'ecialo'

# with open('./catfig.json') as catfig_file:
#     catfig = json.load(catfig_file)

TOKEN = teletoken.TOKEN


class BufferFile(types.InputFile):

    def __init__(self, buffer):
        # print(buffer)
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
        b = io.BytesIO(self.buff.getbuffer())
        while True:
            chunk = b   .read(chunk_size)
            if not chunk:
                break
            yield chunk


class KotChatMember:

    def __init__(self, user):
        self._carma = INITAL_CARMA
        self.is_target_for_care = False
        self.user = user

    @property
    def carma(self):
        return self._carma

    @carma.setter
    def carma(self, value):
        self._carma = min(MAX_CARMA, max(0, value))


class KotChat:

    def __init__(self, chat_id, kotbot):
        self.chat_id = chat_id
        self.kotbot = kotbot
        self.is_running = False

        self.members = {}
        self.feeder = deque(maxlen=FEEDER_SIZE)
        self.is_asleep = False
        self._satiety = INITAL_SATIETY
        self.want_care = False
        self.cared = False
        self.times_not_cared = 0

        iloop = ioloop.IOLoop.current()
        iloop.call_later(1*SECONDS_IN_MINUTE, self.kot_want_eat)
        iloop.call_later(3*SECONDS_IN_MINUTE, self.kot_want_care)
        iloop.call_later(5*SECONDS_IN_MINUTE, self.kot_want_sleep)

    # def add_member(self, user):
    #     self.members[user.id_] = KotChatMember(user)

    @gen.coroutine
    def send_message(self, *args, **kwargs):
        return (yield self.kotbot.send_message(self.chat_id, *args, **kwargs))

    @gen.coroutine
    def send_photo(self, *args, **kwargs):
        yield self.kotbot.send_photo(self.chat_id, *args, **kwargs)

    @property
    def satiety(self):
        return self._satiety

    @satiety.setter
    def satiety(self, value):
        self._satiety = min(MAX_SATIETY, max(0, value))

    @gen.coroutine
    def start(self, _):
        self.is_running = True
        yield self.send_message(
            START_MESSAGE,
            parse_mode=api2.PARSE_MODE_HTML
        )

    @gen.coroutine
    def stop(self, _):
        self.is_running = False
        yield self.send_message(
            STOP_MESSAGE,
            parse_mode=api2.PARSE_MODE_HTML
        )

    @gen.coroutine
    def kot_want_care(self):
        while self.is_running:
            if not self.is_asleep:
                if not self.want_care:
                    try:
                        target_for_care = rnd.choice(list(self.members.values()))
                    except IndexError:
                        yield gen.sleep(rnd.randint(*CARE_GAP))
                    else:
                        target_for_care.is_target_for_care = True
                        user = target_for_care.user
                        self.want_care = True
                        yield self.send_message(
                            WANT_CARE_MESSAGE.format(
                                fname=user.first_name or "",
                                sname=user.last_name or "",
                            ),
                            parse_mode=api2.PARSE_MODE_HTML,
                        )
                        yield gen.sleep(rnd.randint(*CARE_TIMEOUT))
                elif self.want_care and not self.cared:
                    self.times_not_cared += 1
                    self.send_photo(BufferFile(CARE_IMG))
                    if self.times_not_cared >= 2:
                        # print("bad")
                        list(filter(lambda member: member.is_target_for_care, self.members.values()))[0].carma -= 1
                else:
                    self.want_care = False
                    self.cared = False
                    self.times_not_cared = 0
                    yield gen.sleep(rnd.randint(*CARE_GAP))
            # else:
            #     yield self.kot_sleep()

    @gen.coroutine
    def kot_want_sleep(self):
        while self.is_running:
            self.is_asleep = True
            sleep_time = rnd.randint(*SLEEP_DURATION)
            ioloop.IOLoop.current().call_later(sleep_time, self.kot_wake_up)
            yield self.send_message(
                SLEEP_MESSAGE,
                parse_mode=api2.PARSE_MODE_HTML
            )
            sleep_gap = rnd.randint(*SLEEP_GAP)
            yield gen.sleep(sleep_gap)

    @gen.coroutine
    def kot_want_eat(self):
            # print(self.satiety)
        while self.is_running:
            self.satiety -= 1
            if not self.is_asleep:
                if self.feeder:
                    food = self.feeder.popleft()
                    message = yield self.send_message(
                        FEEDER_CONSUME_MESSAGE.format(food=food),
                        parse_mode=api2.PARSE_MODE_HTML
                    )
                    yield self.kot_eat(message)
                else:
                    yield self.send_message(MEW)
            yield gen.sleep(SATIETY_TO_WAIT[self.satiety])

    @gen.coroutine
    def add_food_to_feeder(self, message):
        command_text = message.text.split()
        new_food = " ".join(command_text[1::])
        user = message.from_
        feeder_overflow = len(self.feeder) == self.feeder.maxlen
        self.feeder.append(new_food)
        base_message = ADD_FOOD_TO_FEEDER_MESSAGE.format(
            new_food=new_food,
            fname=user.first_name or "",
            sname=user  .last_name or "",
        )
        if feeder_overflow:
            old_food = self.feeder.popleft()
            overflow_message = FEEDER_OVERFLOW_MESSAGE.format(old_food=old_food)
        else:
            overflow_message = ""
        yield self.send_message(
            "".join([base_message, overflow_message]),
            parse_mode=api2.PARSE_MODE_HTML,
        )

    @gen.coroutine
    def kot_wake_up(self, reason=None):
        if self.is_asleep:
            self.is_asleep = False
            if reason is None:
                yield self.send_message(WAKEUP_MESSAGE)
            else:
                userid = reason.from_.id_
                if userid in self.members:
                    self.members[reason.from_.id_].carma -= 1
                    yield self.kot_agressive(reason)

    @gen.coroutine
    def kot_sleep(self, message):
        yield self.send_message(
            rnd.choice(SLEEP_MESSAGES),
            reply_to_message_id=message.message_id,
        )

    @gen.coroutine
    def kot_scare(self, message):
        userid = message.from_.id_
        if userid in self.members:
            if not self.is_asleep:
                self.members.pop(message.from_.id_)
                yield self.kot_agressive(message)
            else:
                yield self.kot_sleep(message)

    @gen.coroutine
    def kot_care(self, message):
        userid = message.from_.id_
        user = message.from_
        if not self.is_asleep:
            # print(self.members[userid].is_target_for_care, self.members[userid].user.username)
            if userid in self.members and self.members[userid].is_target_for_care:
                if self.times_not_cared == 0:
                    self.members[message.from_.id_].carma += 1
                yield self.send_message(
                    TARGET_CARE_MESSAGE.format(
                        fname=user.first_name or "",
                        sname=user.last_name or "",
                    ),
                    parse_mode=api2.PARSE_MODE_HTML,
                )
            else:
                yield self.send_message(
                    CARE_MESSAGE.format(
                        fname=user.first_name or "",
                        sname=user.last_name or "",
                    ),
                    parse_mode=api2.PARSE_MODE_HTML,
                )
        else:
            yield self.send_message(
                SLEEP_CARE_MESSAGE.format(
                    fname=user.first_name or "",
                    sname=user.last_name or "",
                ),
                parse_mode=api2.PARSE_MODE_HTML,
            )

    @gen.coroutine
    def kot_hello(self, message):
        if message.from_.id_ not in self.members:
            self.members[message.from_.id_] = KotChatMember(message.from_)
        yield self.send_message(
            HELLO_MESSAGE,
            reply_to_message_id=message.message_id,
        )

    @gen.coroutine
    def kot_eat(self, message):
        if not self.is_asleep:
            userid = message.from_.id_
            username = message.from_.username
            fname = message.from_.first_name
            sname = message.from_.last_name
            rmessage = []
            # print(self.members[userid].carma)
            if userid in self.members and self.members[userid].carma >= NORMAL_CARMA:
                rmessage.append(SATIETY_TO_MESSAGE[self.satiety])
                if self.satiety < MAX_SATIETY:
                    self.satiety += 1
                    self.members[userid].carma += 1
                else:
                    rmessage.append(
                        VOMIT_MESSAGE.format(
                            fname=fname or "",
                            sname=sname or "",
                        )
                    )
                    self.members[userid].carma -= 2
            elif userid in self.members and self.members[userid].carma < BAD_CARMA:
                yield self.kot_agressive(message)
            elif username == KOTYARABOT:
                rmessage.append(SATIETY_TO_MESSAGE[self.satiety])
                self.satiety += 1
            if rmessage:
                yield self.send_message(
                    "".join(rmessage),
                    reply_to_message_id=message.message_id,
                    parse_mode=api2.PARSE_MODE_HTML,
                )
        else:
            yield self.kot_sleep(message)

    @gen.coroutine
    def kot_cats_reaction(self, message):
        if message.from_.id_ in self.members:
            if not self.is_asleep:
                member = self.members[message.from_.id_]
                if member.carma >= NORMAL_CARMA:
                    client = httpclient.AsyncHTTPClient()
                    kotimg = yield client.fetch("http://thecatapi.com/api/images/get?type=jpg&size=small")
                    img_to_send = BufferFile(kotimg.buffer)
                    yield self.send_photo(
                        img_to_send,
                        reply_to_message_id=message.message_id,
                    )
                elif member.carma < BAD_CARMA:
                    yield self.kot_agressive(message)
            else:
                yield self.kot_sleep(message)

    @gen.coroutine
    def kot_agressive(self, message):
        yield self.send_message(
            rnd.choice(AGRESSIVE_MESSAGES),
            reply_to_message_id=message.message_id,
        )


class KotBot(api2.TeleLich):

    def __init__(self, token):
        self._api = api2.TeleZombie(token)
        self.kot_chats = {}
        self.commands = {
            '/start': self.handle_start,    # Work
            '/add_to_feeder': self.handle_add_to_feeder,
            '/help': self.handle_help,
            '/care': self.handle_care,
            '/stop': self.handle_stop,      # Work
            '/hunger': self.handle_hunger,
            '/sleep': self.handle_sleep,
            '/play': self.handle_play,
        }
        # self.http_client = httpclient.AsyncHTTPClient()

    # def on

    @gen.coroutine
    def on_text(self, message):
        # id_ = message.message_id
        iloop = ioloop.IOLoop.current()
        text = message.text
        chat_id = message.chat.id_
        lotext = text.lower()
        # putext = lotext.strip(string.punctuation)
        if text.startswith(COMMAND_START):
            yield self.commands[COMMAND_START](message)
        elif text.startswith(COMMAND_SYM):
            if message.chat.id_ in self.kot_chats:
                yield self.commands[re.search(COMMAND, text).group()](message)
        else:
            if message.chat.id_ in self.kot_chats:
                if lotext.endswith(LOUD):
                    yield self.kot_chats[chat_id].kot_wake_up(message)
                if any(((eat_word in lotext) for eat_word in EAT_WORDS)):
                    iloop.spawn_callback(self.kot_chats[chat_id].kot_eat, message)
                elif lotext.count(HELLO_WORD) >= HELLO_COUNT:
                    iloop.spawn_callback(self.kot_chats[chat_id].kot_hello, message)
                elif SCARE_WORD in lotext:
                    iloop.spawn_callback(self.kot_chats[chat_id].kot_scare, message)
                elif CAT in lotext:
                    iloop.spawn_callback(self.kot_chats[chat_id].kot_cats_reaction, message)
        # if text.startswith("/start"):
        #     yield self.handle_start(message)

    @gen.coroutine
    def handle_start(self, message):
        # self.chat_feed[message.chat.id_] = 3
        chat = message.chat
        # print(chat)
        # print(message.from_)
        if chat.id_ not in self.kot_chats:
            self.kot_chats[chat.id_] = KotChat(chat.id_, self)
        self.kot_chats[chat.id_].start(message)
        # yield self.send_message(chat_id=chat.id_, text="@Zloe_ALoe улюлюлю")
        # ioloop.IOLoop.current().call_later(100, self.satiety, chat.id_)

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
        # print(message)
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
        yield self.poll()


@gen.coroutine
def forever():
    lich = KotBot(TOKEN)
    yield lich.poll()


if __name__ == '__main__':
    kotbot = KotBot(TOKEN)
    ioloop.IOLoop.current().spawn_callback(kotbot.run)
    ioloop.IOLoop.current().start()
