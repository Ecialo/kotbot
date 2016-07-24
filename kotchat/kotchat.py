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


class KotChat:

    def __init__(self, start_message, kotbot):
        self.members = {start_message.from_.id_: KotChatMember(start_message.from_)}
        self.state = state.Hello(self)
        # self.state = state.Awake(self)
        # self.state = state.Care(self)
        # self.state = state.Sleep(self)
        self.is_running = True
        self.kotbot = kotbot
        self.chat_id = start_message.chat.id_

        self.name = None
        self._satiety = INITAL_SATIETY
        self.times_cared = 0
        self.feeder = deque()
        self.feeder_max_capacity = FEEDER_SIZE

        iloop = ioloop.IOLoop.current()
        # iloop.call_later(SATIETY_TO_WAIT[self.satiety], self.kot_want_eat)
        iloop.call_later(60, self.kot_want_eat)
        # iloop.call_later(rnd.randint(*SLEEP_GAP), self.kot_want_sleep)
        iloop.call_later(180, self.kot_want_sleep)
        # iloop.call_later(rnd.randint(*CARE_GAP), self.kot_want_care)
        iloop.call_later(120, self.kot_want_care)

    # def __getitem__(self, item):
    #     pass
    #
    # def __setitem__(self, key, value):
    #     pass

    @gen.coroutine
    def send_message(self, text, *args, **kwargs):
        if isinstance(text, Template):
            return (yield self.kotbot.send_message(
                self.chat_id,
                text.safe_substitute(cat_name=self.name),
                parse_mode=api2.PARSE_MODE_HTML,
                *args, **kwargs
            ))
        else:
            return (yield self.kotbot.send_message(
                self.chat_id,
                Template(text).safe_substitute(cat_name=self.name),
                parse_mode=api2.PARSE_MODE_HTML,
                *args, **kwargs
            ))

    @gen.coroutine
    def send_photo(self, *args, **kwargs):
        yield self.kotbot.send_photo(self.chat_id, *args, **kwargs)

    def change_state(self, state_):
        # print("New state", state_.__name__)
        self.state.is_running = False
        self.state = state_(self)

    def stop(self):
        self.is_running = False
        self.state.is_running = False
        self.state = None

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
        print(self.times_cared, self.satiety, self.feeder, self.state)
        yield self.state.on_text(message)

    @gen.coroutine
    def kot_want_eat(self):
        while self.is_running:
            yield [self.state.kot_want_eat(), gen.sleep(SATIETY_TO_WAIT[self.satiety])]

    @gen.coroutine
    def kot_want_sleep(self):
        while self.is_running:
            yield [self.state.kot_want_sleep(), gen.sleep(rnd.randint(*CARE_GAP))]

    @gen.coroutine
    def kot_want_care(self):
        while self.is_running:
            yield [self.state.kot_want_care(), gen.sleep(rnd.randint(*SLEEP_GAP))]

    @gen.coroutine
    def add_to_feeder(self, message):
        command_text = message.text.split()
        new_food = " ".join(command_text[1::])
        user = message.from_
        if new_food.strip(string.punctuation):
            feeder_overflow = len(self.feeder) == self.feeder_max_capacity
            self.feeder.append(new_food)
            base_message = ADD_FOOD_TO_FEEDER_MESSAGE.safe_substitute(
                new_food=new_food,
                fname=user.first_name or "",
                sname=user.last_name or "",
            )
            if feeder_overflow:
                old_food = self.feeder.popleft()
                overflow_message = FEEDER_OVERFLOW_MESSAGE.safe_substitute(old_food=old_food)
            else:
                overflow_message = ""
            yield self.send_message(
                "".join([base_message, overflow_message])
            )
        else:
            yield self.send_message(
                FEEDER_NO_ADD_MESSAGE.safe_substitute(
                    fname=user.first_name or "",
                    sname=user.last_name or "",
                )
            )

    @gen.coroutine
    def kot_care(self, message):
        # if self.members[message.from_.id_].is_in_chat:
        yield self.state.kot_care(message)