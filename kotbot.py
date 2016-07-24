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
from kotchat import (
    kotchat,
    cat_show,
)
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


def struct_to_row(struct):
    s = struct
    # print(s)
    return TABLE_ROW.safe_substitute(
        pos=s[0],
        weight=s[1],
        cat_name=s[2],
        fname=s[3][0],
        sname=s[3][1],
        org_name=("группу " + s[4] if s[4] else "самого себя")
    )


class KotBot(api2.TeleLich):

    def __init__(self, token):
        super().__init__(token)
        self.kot_chats = {}
        self.commands = {
            "/start": self.handle_start,
            "/help": self.handle_help,
            "/stop": self.handle_stop,
            "/add_to_feeder": self.handle_add_to_feeder,
            "/care": self.handle_care,
            # '/hunger': self.handle_hunger,
            # '/sleep': self.handle_sleep,
            # '/play': self.handle_play,
            '/hug': self.handle_hug,
            '/to_show': self.handle_show,

        }

        self.show = cat_show.CatShow()

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
        if chat_id not in self.kot_chats:
            self.kot_chats[chat_id] = kotchat.KotChat(message, self)
            yield self.send_message(
                chat_id,
                START_MESSAGE.safe_substitute(),
                parse_mode=api2.PARSE_MODE_HTML
            )
        else:
            yield self.send_message(
                chat_id,
                ALREADY_CAT_MESSAGE.safe_substitute(),
                parse_mode=api2.PARSE_MODE_HTML
            )

    @gen.coroutine
    def handle_help(self, message):
        yield self.send_message(
            message.chat.id_,
            HELP_MESSAGE.safe_substitute()
        )

    @gen.coroutine
    def handle_stop(self, message):
        chat_id = message.chat.id_
        self.kot_chats[chat_id].stop()
        self.kot_chats.pop(message.chat.id_)
        yield self.send_message(
            chat_id,
            STOP_MESSAGE.safe_substitute(),
            parse_mode=api2.PARSE_MODE_HTML
        )

    @gen.coroutine
    def handle_add_to_feeder(self, message):
        chat_id = message.chat.id_
        yield self.kot_chats[chat_id].add_to_feeder(message)

    @gen.coroutine
    def handle_care(self, message):
        chat_id = message.chat.id_
        yield self.kot_chats[chat_id].kot_care(message)

    @gen.coroutine
    def handle_hug(self, message):
        chat_id = message.chat.id_
        yield self.kot_chats[chat_id].kot_hug(message)

    @gen.coroutine
    def handle_show(self, message):
        chat_id = message.chat.id_
        cat = self.kot_chats[chat_id]
        fname = message.from_.first_name or ""
        sname = message.from_.last_name or ""
        yield self.send_message(
            chat_id,
            SHOW_MESSAGE.safe_substitute(
                fname=fname,
                sname=sname,
            ),
            parse_mode=api2.PARSE_MODE_HTML
        )
        yield self.show.add_cat(message, cat.name or "", cat.weight)
        top10, our_res = yield self.show.get_cat(message)
        yield self.send_message(
            chat_id,
            OUR_RANK.safe_substitute(
                cat_name=cat.name,
                weight=cat.weight,
                pos=our_res,
                fname=fname,
                sname=sname,
            ),
            parse_mode=api2.PARSE_MODE_HTML
        )
        full_table = "".join(map(struct_to_row, top10))
        yield self.send_message(
            chat_id,
            FULL_TABLE_MESSAGE,
            parse_mode=api2.PARSE_MODE_HTML
        )
        yield self.send_message(
            chat_id,
            full_table,
            parse_mode=api2.PARSE_MODE_HTML)

    @gen.coroutine
    def handle_hunger(self, message):
        chat_id = message.chat.id_
        yield self.kot_chats[chat_id].state.kot_want_eat()

    @gen.coroutine
    def handle_sleep(self, message):
        chat_id = message.chat.id_
        yield self.kot_chats[chat_id].state.kot_want_sleep()

    @gen.coroutine
    def handle_play(self, message):
        chat_id = message.chat.id_
        yield self.kot_chats[chat_id].state.kot_want_care()

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
