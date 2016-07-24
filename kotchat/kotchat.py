# -*- coding: utf-8 -*-
import string
import random as rnd
import re
import json
from collections import (
    # defaultdict,
    deque,
)
from tornado import (
    ioloop,
    gen,
    httpclient,
    # web,
)
from catfig import *
from telezombie2 import (
    api as api2,
    types as types2,
)
from . import state
__author__ = 'ecialo'


class KotChatMember:

    def __init__(self, user):
        self._carma = INITAL_CARMA
        self.user = user
        self.is_in_chat = True

    @property
    def carma(self):
        return self._carma

    @carma.setter
    def carma(self, value):
        self._carma = min(MAX_CARMA, max(0, value))


class DKotChat:

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
        self.times_cared = 0

        iloop = ioloop.IOLoop.current()
        iloop.call_later(1*SECONDS_IN_MINUTE, self.kot_want_eat)
        iloop.call_later(5*SECONDS_IN_MINUTE, self.kot_want_care)
        # iloop.call_later(30, self.kot_want_care)
        iloop.call_later(10*SECONDS_IN_MINUTE, self.kot_want_sleep)
        # iloop.call_later(10, self.kot_want_sleep)

    @gen.coroutine
    def send_message(self, *args, **kwargs):
        return (yield self.kotbot.send_message(self.chat_id, *args, **kwargs))

    @gen.coroutine
    def send_html_message(self, *args, **kwargs):
        return (yield self.kotbot.send_message(self.chat_id, parse_mode=api2.PARSE_MODE_HTML, *args, **kwargs))

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
        yield self.send_html_message(START_MESSAGE)

    @gen.coroutine
    def stop(self, _):
        self.is_running = False
        yield self.send_message(STOP_MESSAGE)

    @gen.coroutine
    def kot_want_care(self):
        while self.is_running:
            # print("want care", self.want_care, self.cared)
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
                    yield self.send_photo(types2.BufferFile(CARE_IMG))
                    if self.times_not_cared >= 2:
                        # print("bad")
                        list(filter(lambda member: member.is_target_for_care, self.members.values()))[0].carma -= 1
                    yield gen.sleep(rnd.randint(*CARE_TIMEOUT))
                else:
                    self.want_care = False
                    self.cared = False
                    self.times_not_cared = 0
                    yield gen.sleep(rnd.randint(*CARE_GAP))
            else:
                yield gen.sleep(rnd.randint(*CARE_GAP))

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
                    yield self.kot_mew(None)
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
                if self.members[userid].is_target_for_care:
                    self.want_care = False
                    self.cared = False
                    self.times_not_cared = 0
                self.members.pop(message.from_.id_)
                yield self.kot_agressive(message)
            else:
                yield self.kot_sleep(message)

    @gen.coroutine
    def kot_care(self, message):
        userid = message.from_.id_
        user = message.from_
        if not self.is_asleep:
            suc = rnd.randint(0, self.times_cared)
            print(suc)
            if suc > 5:
                self.times_cared = 0
                yield self.send_message(
                    BAD_CARE_MESSAGE.format(
                        fname=user.first_name or "",
                        sname=user.last_name or "",
                    ),
                    parse_mode=api2.PARSE_MODE_HTML,
                )
                return
            else:
                self.times_cared += 1
            # print(self.members[userid].is_target_for_care, self.members[userid].user.username)
            if userid in self.members and self.members[userid].is_target_for_care:
                self.cared = True
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
                        DISAPPOINTED_CARE_MESSAGE.format(
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
        if not self.is_asleep:
            if message.from_.id_ not in self.members:
                self.members[message.from_.id_] = KotChatMember(message.from_)
            yield self.send_message(
                HELLO_MESSAGE,
                reply_to_message_id=message.message_id,
            )
        else:
            yield self.kot_sleep(message)

    @gen.coroutine
    def kot_eat(self, message):
        if not self.is_asleep:
            userid = message.from_.id_
            username = message.from_.username
            fname = message.from_.first_name
            sname = message.from_.last_name
            rmessage = []
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
                    img_to_send = types2.BufferFile(kotimg.buffer)
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

    @gen.coroutine
    def kot_mew(self, message):
        yield self.send_message(
            rnd.choice(MEW)
        )


class KotChat:

    def __init__(self, chat_id, kotbot):
        self.members = {}
        self.state = state.Hello(self)
        self.is_running = True
        self.kotbot = kotbot
        self.chat_id = chat_id

        self.name = None
        self._satiety = INITAL_SATIETY
        self.times_cared = 0

    # def __getitem__(self, item):
    #     pass
    #
    # def __setitem__(self, key, value):
    #     pass

    @gen.coroutine
    def send_message(self, text, *args, **kwargs):
        return (yield self.kotbot.send_message(
            self.chat_id,
            text.format(cat_name=self.name),
            parse_mode=api2.PARSE_MODE_HTML,
            *args, **kwargs
        ))

    @gen.coroutine
    def send_photo(self, *args, **kwargs):
        yield self.kotbot.send_photo(self.chat_id, *args, **kwargs)

    def change_state(self, state_):
        self.state.is_running = False
        self.state = state_(self)

    def stop(self):
        self.is_running = False

    @property
    def satiety(self):
        return self._satiety

    @satiety.setter
    def satiety(self, value):
        self._satiety = min(MAX_SATIETY, max(0, value))

    @gen.coroutine
    def on_text(self, message):
        user = message.from_
        if user.id_ not in self.members:
            self.members[user.id_] = KotChatMember(user)
        yield self.state.on_text(message)

    @gen.coroutine
    def kot_want_eat(self):
        while self.is_running:
            yield self.state.kot_want_sleep()

    @gen.coroutine
    def kot_want_sleep(self):
        while self.is_running:
            yield self.state.kot_want_eat()

    @gen.coroutine
    def kot_want_care(self):
        while self.is_running:
            yield self.state.kot_want_care()
