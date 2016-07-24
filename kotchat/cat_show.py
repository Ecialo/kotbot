# -*- coding: utf-8 -*-
from tornado import (
    gen,
)
from telezombie import types
__author__ = 'ecialo'


class CatShow:

    def __init__(self):
        self.cats = {}

    @gen.coroutine
    def add_cat(self, message, cat_name, weight):
        chat_id = message.chat.id_
        user = message.from_
        chat = message.chat
        owner_name = (user.first_name or "", user.last_name or "")
        org_name = chat.title if isinstance(chat, types.GroupChat) else None
        self.cats[chat_id] = (weight, cat_name, owner_name, org_name, chat_id)

    @gen.coroutine
    def get_cat(self, message):
        target_cat = message.chat.id_
        cats_rate = enumerate(sorted(self.cats.values(), key=lambda x: x[0]), 1)
        top10 = []
        target_pos = None
        for cat_pos, cat in cats_rate:
            if cat[-1] == target_cat:
                target_pos = cat_pos
            if len(top10) < 10:
                top10.append((cat_pos,) + cat)
        return top10, target_pos


