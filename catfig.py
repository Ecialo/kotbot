# -*- coding: utf-8 -*-
import re
import io
__author__ = 'ecialo'

KOTYARABOT = "kotyarabot"

SECONDS_IN_MINUTE = 60

CAT = "кот"

COMMAND = re.compile(r"/\w+")
COMMAND_START = "/start"
COMMAND_SYM = "/"

INITAL_CARMA = 3
(
    VERY_BAD_CARMA,
    BAD_CARMA,
    NORMAL_CARMA,
) = range(3)
MAX_CARMA = 10

INITAL_SATIETY = 3
MAX_SATIETY = 10

HELLO_WORD = "кис"
HELLO_COUNT = 2
HELLO_MESSAGE = "Мур-мур-мур"

SCARE_WORD = "брысь"

LOUD = "!"

EAT_WORDS = ["куш", "съе"]
SATIETY_TO_MESSAGE = {
    10: "Няяяям-Няяяяям",
    9: "Няяяям-Няяяяям",
    8: "Няяяям-Няяяяям",
    7: "Няяяям-Няяяяям",
    6: "Няяяям-Няяяяям",
    5: "Няяяям-Няяяяям",
    4: "Ням-Ням-Ням",
    3: "Омномном",
    2: "Омномномномном",
    1: "Омномномчавкхлюп",
    0: "ОМНОМНОМЧАВКНОМХЛЮПЧАВКНОМ"
}
SATIETY_TO_WAIT = {i: SECONDS_IN_MINUTE*i for i in range(11)}

VOMIT_MESSAGE = """
<i>Котяра съел слишком много и его стошнило. В этом явно виноват {fname} {sname}</i>
"""

START_MESSAGE = """
<i>У вас завелся котяра. Сейчас он тихо сидит в уголке.</i>
"""

HELP_MESSAGE = """
Это котик в телеграме.
Чтобы познакомиться с котиком поманите его напечатав "кис-кис" или что-то вроде
Котик любит кушать, иногда ложится спать и лезет играть.
/start чтобы завести котика
/stop если котик больше не нужен
/care чтобы погладить Котяру
/add_to_feeder <какая нибудь еда> чтобы положить еду в кормушку
"""

STOP_MESSAGE = """
<i>Котяра выпрыгнул с балкона и убежал.</i>
"""

FEEDER_SIZE = 1
ADD_FOOD_TO_FEEDER_MESSAGE = """
<i>{fname} {sname} добавил</i> <b>{new_food}</b> <i>в кормушку.</i>
"""
FEEDER_OVERFLOW_MESSAGE = """
<i>Так как кормушка была переполнена из неё вывалился недоеденный корм, а именно</i> <b>{old_food}</b>
"""
FEEDER_CONSUME_MESSAGE = """
<i>Котяра съедает из кормушки</i> <b>{food}</b>
"""

SLEEP_DURATION = 5*SECONDS_IN_MINUTE, 10*SECONDS_IN_MINUTE
SLEEP_GAP = 30*SECONDS_IN_MINUTE, 60*SECONDS_IN_MINUTE
SLEEP_MESSAGES = [
    "Хрррр-Хрррр",
    "Хр-Хр-Хр",
    "ХРРРРРРРРРР!",
    "Хрррхррвап...",
    "ХррХррр",
]
SLEEP_MESSAGE = """
<i>Котяра ложится спать</i>
"""

WAKEUP_MESSAGE = """
Миявввв...
"""

CARE_TIMEOUT = SECONDS_IN_MINUTE, 2*SECONDS_IN_MINUTE
CARE_GAP = 5*SECONDS_IN_MINUTE, 60*SECONDS_IN_MINUTE
WANT_CARE_MESSAGE = """
<i>Котяра трется о ногу {fname} {sname} и мурчит.</i>
"""
CARE_IMG = io.BytesIO(open("pet.jpg", 'rb').read())
CARE_MESSAGE = """
<i>{fname} {sname} погладил котяру.</i>
"""
SLEEP_CARE_MESSAGE = """
<i>{fname} {sname} <i>погладил спящего котика.</i>
"""
TARGET_CARE_MESSAGE = """
<i>{fname} {sname} погладил котяру.</i>
Мурррррррр.
"""

AGRESSIVE_MESSAGES = [
    "ШШШшШшШ!!!",
    "ШшШшШшШшшшшш!",
    "МмшшшШШШШ!",
    "Шшшшшшшшшшшшш....",
]

MEW = "МЯУ!"
