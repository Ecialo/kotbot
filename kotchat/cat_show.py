# -*- coding: utf-8 -*-
from tornado import (
    gen,
)
import pymongo
# from motor import (
#     motor_tornado as mt
# )
from telezombie import types
__author__ = 'ecialo'


class CatShow:

    def __init__(self, cats_db):
        self.cats_db = cats_db
        # self.cats = {}

    # @gen.coroutine
    # def add_cat(self, message, cat_name, weight):
    #     chat_id = message.chat.id_
    #     user = message.from_
    #     chat = message.chat
    #     owner_name = (user.first_name or "", user.last_name or "")
    #     org_name = chat.title if isinstance(chat, types.GroupChat) else None
    #     self.cats[chat_id] = (weight, cat_name, owner_name, org_name, chat_id)

    @gen.coroutine
    def add_cat(self, message, cat_name, weight):
        chat_id = message.chat.id_
        user = message.from_
        chat = message.chat
        owner_name = [user.first_name or "", user.last_name or ""]
        org_name = chat.title if isinstance(chat, types.GroupChat) else None

        cat = {
            "_id": chat_id,
            "cat_name": cat_name,
            "weight": weight,
            "owner_name": owner_name,
            "org_name": org_name,
        }
        yield self.cats_db.save(cat)
        return cat
        # self.cats[chat_id] = (weight, cat_name, owner_name, org_name, chat_id)

    # @gen.coroutine
    # def get_cat(self, message):
    #     target_cat = message.chat.id_
    #     cats_rate = enumerate(sorted(self.cats.values(), key=lambda x: x[0], reverse=True), 1)
    #     top10 = []
    #     target_pos = None
    #     for cat_pos, cat in cats_rate:
    #         if cat[-1] == target_cat:
    #             target_pos = cat_pos
    #         if len(top10) < 10:
    #             top10.append((cat_pos,) + cat)
    #     return top10, target_pos

    @gen.coroutine
    def get_pos_and_top(self, cat):
        # cat_id = message.chat.id_
        # target_cat = yield self.cats_db.find_one({"_id": cat_id})
        target_cat_pos = yield self.cats_db.find({"weight": {"$gt": cat["weight"]}}).count()
        top = yield self.cats_db.find().sort("weight", pymongo.DESCENDING).to_list(10)
        top10 = []
        for pos, top_cat in enumerate(top):
            top10.append(
                (
                    pos+1,
                    top_cat['weight'],
                    top_cat['cat_name'],
                    top_cat['owner_name'],
                    top_cat['org_name'],
                    top_cat['_id']
                )
            )
        return top10, target_cat_pos+1

    # def dump(self):
    #     pass
    #
    # def load(self, struct):
    #     pass
        # self.cats = {catid:tuple(cat) for catid struct}

