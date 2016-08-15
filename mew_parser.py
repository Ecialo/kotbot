# -*- coding: utf-8 -*-
import random as rnd
from string import Template
import json
__author__ = 'ecialo'

COMMENTARY = "//"
MARK = "#"
KEY = "@"


class Mews:

    def __init__(self, mew_path, dev=False):
        self._mews = {}
        self._dev = dev
        self.load_mews(mew_path)
        # print(self._dev)

    def load_mews(self, mew_path):
        mew = []
        mew_name = None
        with open(mew_path) as mew_file:
            for line in mew_file:
                valline = line.split(COMMENTARY)[0].strip(" \t\n")
                if valline:
                    if valline.startswith(MARK):
                        self[mew_name] = "\n".join(mew)
                        mew_name = valline
                        mew = []
                    else:
                        mew.append(valline)
            else:
                self[mew_name] = "\n".join(mew)

    def __getitem__(self, item):
        if isinstance(item, tuple):
            return rnd.choice(self._mews[item[0]][str(item[1])])
        else:
            return rnd.choice(self._mews[item])

    def __setitem__(self, key, value):
        if key:
            value = Template(value) if not self._dev else value
            mark_key = key.strip(MARK).split(KEY)
            if len(mark_key) > 1 and mark_key[-1]:
                mark, key = mark_key
                if mark not in self._mews:
                    self._mews[mark] = {}
                if key not in self._mews[mark]:
                    self._mews[mark][key] = []
                self._mews[mark][key].append(value)
            else:
                mark = mark_key[0]
                if mark not in self._mews:
                    self._mews[mark] = []
                self._mews[mark].append(value)

    def dump(self):
        if self._dev:
            return json.dumps(self._mews)


if __name__ == '__main__':
    m = Mews("./mew.txt", True)
    print(m.dump())
    # print(m[("AZAZA", 2)])
    # print(m[("AZAZA", 2)])
    # print(m[("AZAZA", 2)])
    # print(m[("AZAZA", 2)])
