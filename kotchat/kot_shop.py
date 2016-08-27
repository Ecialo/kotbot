# -*- coding: utf-8 -*-
from tornado import gen
from catfig import *

__author__ = 'ecialo'


class KotShop:

    def __init__(self, kotchat):
        self.kotchat = kotchat
        self._mewney = INITAL_MEWNEY
        self._items = {
            FEEDER: self.buy_feeder
        }

    @gen.coroutine
    def send_message(self, *args, **kwargs):
        return (yield self.kotchat.send_message(*args, **kwargs))

    @gen.coroutine
    def buy_feeder(self):
        if self._mewney >= self.kotchat.feeder_max_capacity + 1:
            self._mewney -= self.kotchat.feeder_max_capacity + 1
            self.kotchat.feeder_max_capacity += 1
            yield self.send_message(FEEDER_EXTENDED)
        else:
            yield self.send_message(NOT_ENOUGH_MEWNEY)

    @gen.coroutine
    def buy_help(self):
        yield self.send_message(BUY)

    def add_mewney(self, number):
        self._mewney += number

    @gen.coroutine
    def buy(self, item):
        yield self._items.get(item, self.buy_help)()