# -*- coding: utf-8 -*-
from telezombie import types
import io
__author__ = 'ecialo'


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
