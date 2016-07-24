# -*- coding: utf-8 -*-
import random as rnd
from tornado import (
    gen,
    ioloop,
    httpclient,
)
from telezombie2 import (
    types as types2
)
from catfig import *

__author__ = 'ecialo'


class State:

    def __init__(self, kotchat):
        self.kotchat = kotchat
        self.is_running = True

    @gen.coroutine
    def on_text(self, message):
        pass

    @gen.coroutine
    def send_message(self, *args, **kwargs):
        return (yield self.kotchat.send_message(*args, **kwargs))

    @gen.coroutine
    def send_photo(self, *args, **kwargs):
        yield self.kotchat.send_photo(*args, **kwargs)

    @gen.coroutine
    def kot_want_sleep(self):
        pass

    @gen.coroutine
    def kot_want_care(self):
        pass

    @gen.coroutine
    def kot_want_eat(self):
        pass

    @gen.coroutine
    def kot_care(self, message):
        pass


class Hello(State):

    @gen.coroutine
    def on_text(self, message):
        if not self.kotchat.name:
            if message:
                self.kotchat.name = message.text[0].upper() + message.text[1::]
                yield self.send_message(CAT_NAME_MESSAGE)
            else:
                self.kotchat.name = "Котяра"
                yield self.send_message(NO_NAME_CAT)
            self.kotchat.change_state(Awake)


class Regular(State):

    @gen.coroutine
    def on_text(self, message):
        iloop = ioloop.IOLoop.current()
        lotext = message.text.lower()
        # print(lotext)
        user = self.kotchat.members[message.from_.id_]
        carma = user.carma
        if user.is_in_chat:
            if any(((mew_trigger in lotext) for mew_trigger in MEW_TRIGGER)):
                self.kot_check_and_action(carma, self.kot_mew, message)
            if any(((eat_word in lotext) for eat_word in EAT_WORDS)):
                # print("AHA")
                self.kot_check_and_action(carma, self.kot_eat, message)
            elif SCARE_WORD in lotext:
                iloop.spawn_callback(self.kot_scare, message)       # ATTENTION
            elif any(((cat in lotext) for cat in CAT)):
                self.kot_check_and_action(carma, self.kot_cats_reaction, message)
        else:
            if lotext.count(HELLO_WORD) >= HELLO_COUNT:
                iloop.spawn_callback(self.kot_hello, message)

    def kot_check_and_action(self, carma, action, message):
        iloop = ioloop.IOLoop.current()
        if carma >= NORMAL_CARMA:
            iloop.spawn_callback(action, message)
        elif carma < BAD_CARMA:
            iloop.spawn_callback(self.kot_agressive, message)
        else:
            iloop.spawn_callback(self.kot_passive, message)

    def kot_want_sleep(self):
        pass

    def kot_want_care(self):
        pass

    def kot_want_eat(self):
        pass

    def kot_cats_reaction(self, message):
        pass

    def kot_scare(self, message):
        pass

    def kot_hello(self, message):
        pass

    def kot_eat(self, message):
        pass

    def kot_mew(self, message):
        pass

    def kot_agressive(self, message):
        pass

    def kot_passive(self, message):
        pass


class Awake(Regular):

    @gen.coroutine
    def kot_want_sleep(self):
        self.kotchat.change_state(Sleep)

    @gen.coroutine
    def kot_want_care(self):
        self.kotchat.change_state(Care)

    @gen.coroutine
    def kot_want_eat(self):
        self.kotchat.satiety -= 1
        feeder = self.kotchat.feeder
        if feeder:
            food = feeder.popleft()
            message = yield self.send_message(
                FEEDER_CONSUME_MESSAGE.safe_substitute(food=food),
            )
            yield self.kot_eat(message)
            if self.kotchat.satiety >= SATIETY_TO_FAT:
                self.kotchat.weight += 1
                yield self.send_message(FAT)
        else:
            yield self.kot_mew(None)
            if self.kotchat.satiety == SATIETY_TO_THIN:
                self.kotchat.weight -= 1
                thin = yield self.send_message(THIN)
                if self.kotchat.weight <= 0:
                    yield self.kotchat.kotbot.handle_stop(thin)

    @gen.coroutine
    def kot_cats_reaction(self, message):
        client = httpclient.AsyncHTTPClient()
        kotimg = yield client.fetch("http://thecatapi.com/api/images/get?type=jpg&size=small")
        img_to_send = types2.BufferFile(kotimg.buffer)
        yield self.send_photo(
            img_to_send,
            reply_to_message_id=message.message_id,
        )

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

    @gen.coroutine
    def kot_scare(self, message):
        self.kotchat.members[message.from_.id_].is_in_chat = False

    @gen.coroutine
    def kot_hello(self, message):
        self.kotchat.members[message.from_.id_].is_in_chat = True

    @gen.coroutine
    def kot_care(self, message):
        user = message.from_
        suc = rnd.randint(0, self.kotchat.times_cared)
        if suc > 5:
            self.kotchat.times_cared = 0
            yield self.send_message(
                BAD_CARE_MESSAGE.safe_substitute(
                    fname=user.first_name or "",
                    sname=user.last_name or "",
                )
            )
        else:
            self.kotchat.times_cared += 1
            yield self.send_message(
                CARE_MESSAGE.safe_substitute(
                    fname=user.first_name or "",
                    sname=user.last_name or "",
                )
            )

    @gen.coroutine
    def kot_eat(self, message):
        # print("EAT")
        userid = message.from_.id_
        username = message.from_.username
        fname = message.from_.first_name
        sname = message.from_.last_name
        rmessage = []
        if userid not in self.kotchat.members:
            rmessage.append(SATIETY_TO_MESSAGE[self.kotchat.satiety])
            self.kotchat.satiety += 1
        else:
            rmessage.append(SATIETY_TO_MESSAGE[self.kotchat.satiety])
            if self.kotchat.satiety < MAX_SATIETY:
                self.kotchat.satiety += 1
                self.kotchat.members[userid].carma += 1
            else:
                rmessage.append(
                    VOMIT_MESSAGE.safe_substitute(
                        fname=fname or "",
                        sname=sname or "",
                    )
                )
                self.kotchat.members[userid].carma -= 2
                self.kotchat.weight = int(self.kotchat.weight*0.9)
        if rmessage:
            yield self.send_message(
                "".join(rmessage),
                reply_to_message_id=message.message_id,
            )


class Care(Awake):

    def __init__(self, kotchat):
        super().__init__(kotchat)
        self.target_for_care = rnd.choice([user[0] for user in kotchat.members.items() if user[1].is_in_chat])
        self.is_cared = False
        self.times_not_cared = 0
        target = kotchat.members[self.target_for_care].user
        loop = ioloop.IOLoop.current()
        loop.spawn_callback(
            self.send_message,
            WANT_CARE_MESSAGE.safe_substitute(
                fname=target.first_name or "",
                sname=target.last_name or "",
            ),
        )
        loop.call_later(rnd.randint(*CARE_TIMEOUT), self.care_the_cat_suka)

    @gen.coroutine
    def kot_care(self, message):
        user = message.from_
        userid = user.id_
        suc = rnd.randint(0, self.kotchat.times_cared)
        if not self.is_cared:
            self.is_cared = True
            if self.times_not_cared == 0 and userid == self.target_for_care:
                self.kotchat.members[message.from_.id_].carma += 1
                yield self.send_message(
                    TARGET_CARE_MESSAGE.safe_substitute(
                        fname=user.first_name or "",
                        sname=user.last_name or "",
                    )
                )
            else:
                yield self.send_message(
                    DISAPPOINTED_CARE_MESSAGE.safe_substitute(
                        fname=user.first_name or "",
                        sname=user.last_name or "",
                    )
                )
            self.kotchat.change_state(Awake)
        elif suc > 5:
            self.kotchat.times_cared = 0
            yield self.send_message(
                BAD_CARE_MESSAGE.safe_substitute(
                    fname=user.first_name or "",
                    sname=user.last_name or "",
                )
            )
        else:
            self.kotchat.times_cared += 1
            yield self.send_message(
                CARE_MESSAGE.safe_substitute(
                    fname=user.first_name or "",
                    sname=user.last_name or "",
                )
            )

    @gen.coroutine
    def kot_want_care(self):
        pass

    @gen.coroutine
    def care_the_cat_suka(self):
        while self.is_running and not self.is_cared:
            if self.times_not_cared >= 3:
                for user in self.kotchat.members.values():
                    user.carma -= 1
                self.kotchat.change_state(Awake)
                yield self.send_message(SAD_CAT_MESSAGE)
            else:
                self.times_not_cared += 1
                yield [self.send_photo(types2.BufferFile(CARE_IMG)), gen.sleep(rnd.randint(*CARE_TIMEOUT))]


def check_loudness(text):
    return text.upper() == text


class Sleep(Regular):

    def __init__(self, kotchat):
        super().__init__(kotchat)
        loop = ioloop.IOLoop.current()
        loop.spawn_callback(
            self.send_message,
            SLEEP_MESSAGE
        )
        loop.call_later(rnd.randint(*SLEEP_DURATION), self.kot_wake_up, None)

    @gen.coroutine
    def on_text(self, message):
        text = message.text
        if text.endswith(LOUD) or check_loudness(text):
            yield self.kot_wake_up(message)
            yield self.kotchat.on_text(message)
        else:
            yield super().on_text(message)

    def kot_check_and_action(self, _, __, message):
        iloop = ioloop.IOLoop.current()
        iloop.spawn_callback(self.kot_sleep, message)

    @gen.coroutine
    def kot_want_eat(self):
        self.kotchat.satiety -= 1

    @gen.coroutine
    def kot_want_sleep(self):
        pass

    @gen.coroutine
    def kot_want_care(self):
        pass

    @gen.coroutine
    def kot_wake_up(self, reason):
        if self.is_running:
            self.kotchat.change_state(Awake)
            if reason is None:
                yield self.send_message(WAKEUP_MESSAGE)
            else:
                userid = reason.from_.id_
                if userid in self.kotchat.members:
                    self.kotchat.members[reason.from_.id_].carma -= 1
                    yield self.kot_agressive(reason)

    @gen.coroutine
    def kot_sleep(self, message):
        yield self.send_message(
            rnd.choice(SLEEP_MESSAGES),
            reply_to_message_id=message.message_id,
        )

    @gen.coroutine
    def kot_care(self, message):
        user = message.from_
        yield self.send_message(
            SLEEP_CARE_MESSAGE.safe_substitute(
                fname=user.first_name or "",
                sname=user.last_name or "",
            )
        )

    @gen.coroutine
    def kot_scare(self, message):
        yield self.kot_sleep(message)

    @gen.coroutine
    def kot_hello(self, message):
        yield self.kot_sleep(message)

    @gen.coroutine
    def kot_agressive(self, message):
        yield self.send_message(
            rnd.choice(AGRESSIVE_MESSAGES),
            reply_to_message_id=message.message_id,
        )