# -*- coding: utf-8 -*-
import random as rnd
from string import Template
__author__ = 'ecialo'

COMMENTARY = "//"
MARK = "#"
KEY = "@"


class Mews:

    def __init__(self, mew_path):
        self._mews = {}
        self.load_mews(mew_path)

    def load_mews(self, mew_path):
        mew = []
        mew_name = None
        with open(mew_path) as mew_file:
            for line in mew_file:
                valline = line.split(COMMENTARY)[0].strip("\n")
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
            value = Template(value)
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


if __name__ == '__main__':
    m = Mews("./mew.txt")
    print(m._mews)
    # print(m[("AZAZA", 2)])
    # print(m[("AZAZA", 2)])
    # print(m[("AZAZA", 2)])
    # print(m[("AZAZA", 2)])
