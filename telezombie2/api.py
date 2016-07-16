# -*- coding: utf-8 -*-
from tornado import (
    gen,
)
from telezombie import (
    api,
    types,
)
__author__ = 'ecialo'

PARSE_MODE_HTML = "HTML"


class TeleZombie(api.TeleZombie):

    @gen.coroutine
    def send_message(
            self,
            chat_id,
            text,
            disable_web_page_preview=None,
            reply_to_message_id=None,
            reply_markup=None,
            parse_mode=None,
            pinned_message=None,
    ):
        args = {
            'chat_id': chat_id,
            'text': text,
        }
        if disable_web_page_preview is not None:
            args['disable_web_page_preview'] = disable_web_page_preview
        if reply_to_message_id is not None:
            args['reply_to_message_id'] = reply_to_message_id
        if reply_markup is not None:
            args['reply_markup'] = str(reply_markup)
        if parse_mode is not None:
            args['parse_mode'] = parse_mode

        data = yield self._get('sendMessage', args)
        return types.Message(data)


class TeleLich(api.TeleLich):

    @gen.coroutine
    def send_message(
            self,
            chat_id,
            text,
            disable_web_page_preview=None,
            reply_to_message_id=None,
            reply_markup=None,
            parse_mode=None,
            pinned_message=None,
    ):

        return (yield self._api.send_message(
            chat_id,
            text,
            disable_web_page_preview,
            reply_to_message_id,
            reply_markup,
            parse_mode,
            pinned_message,
        ))

    @gen.coroutine
    def listen(self, hook_url, cert=None):
        yield self._api.set_webhook(url=hook_url)
