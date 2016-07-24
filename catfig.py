# -*- coding: utf-8 -*-
import re
import io
from string import Template
__author__ = 'ecialo'

KOTYARABOT = "kotyarabot"

SECONDS_IN_MINUTE = 60

CAT = ["кот", "кис"]

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
HELLO_MESSAGE = "Мур-мур-мур..."

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
SATIETY_TO_WAIT = {i: SECONDS_IN_MINUTE*(i+1) for i in range(11)}

SATIETY_TO_FAT = 5
SATIETY_TO_THIN = 0

VOMIT_MESSAGE = Template("""
<i>Котяра съел слишком много и его стошнило. В этом явно виноват $fname $sname</i>
""")

START_MESSAGE = Template("""
<i>У вас завелся котяра. Сейчас он тихо сидит в уголке.
Как его зовут?</i>
""")

ALREADY_CAT_MESSAGE = Template("""
<i>У вас уже есть котик!</i>
""")

CAT_NAME_MESSAGE = Template("""
<i>Котику нравится имя $cat_name</i>
""")

NO_NAME_CAT = Template("""
<i>Котик решил, что будет зваться $cat_name!</i>
""")

HELP_MESSAGE = Template("""
Это котик в телеграме.
Чтобы лично познакомиться с котиком поманите его напечатав "кис-кис" или что-то вроде.
Пока вы этого не сделаете, котяра будет вас по большей части игнорировать.
Котик любит кушать, иногда ложится спать и лезет играть.
/start чтобы завести котика
/stop если котик больше не нужен
/care чтобы погладить Котяру
/add_to_feeder <какая нибудь еда> чтобы положить еду в кормушку
""")

STOP_MESSAGE = Template("""
<i>Котяра выпрыгнул с балкона и убежал.</i>
""")

FEEDER_SIZE = 5
ADD_FOOD_TO_FEEDER_MESSAGE = Template("""
<i>$fname $sname добавил</i> <b>$new_food</b> <i>в кормушку.</i>
""")
FEEDER_OVERFLOW_MESSAGE = Template("""
<i>Так как кормушка была переполнена из неё вывалился недоеденный корм, а именно</i> <b>{old_food}</b>
""")
FEEDER_CONSUME_MESSAGE = Template("""
<i>$cat_name съедает из кормушки</i> <b>$food</b>
""")
FEEDER_NO_ADD_MESSAGE = Template("""
<i>$fname $sname ничего не добавил в кормушку</i>
""")

SLEEP_DURATION = 5*SECONDS_IN_MINUTE, 10*SECONDS_IN_MINUTE
# SLEEP_DURATION = 5, 10
SLEEP_GAP = 30*SECONDS_IN_MINUTE, 60*SECONDS_IN_MINUTE
SLEEP_MESSAGES = [
    "Хрррр-Хрррр",
    "Хр-Хр-Хр",
    "ХРРРРРРРРРР!",
    "Хрррхррвап...",
    "ХррХррр",
]
SLEEP_MESSAGE = Template("""
<i>$cat_name ложится спать</i>
""")

WAKEUP_MESSAGE = Template("""
Миявввв...
""")

# CARE_TIMEOUT = SECONDS_IN_MINUTE, 2*SECONDS_IN_MINUTE
CARE_TIMEOUT = 10, 15
CARE_GAP = 5*SECONDS_IN_MINUTE, 60*SECONDS_IN_MINUTE
WANT_CARE_MESSAGE = Template("""
<i>$cat_name трется о ногу $fname $sname и мурчит.</i>
""")
CARE_IMG = io.BytesIO(open("pet.jpg", 'rb').read())
# CARE_IMG = "pet.jpg"
CARE_MESSAGE = Template("""
<i>$fname $sname погладил котяру.</i>
""")
SLEEP_CARE_MESSAGE = Template("""
<i>$fname $sname погладил спящего котика.</i>
""")
TARGET_CARE_MESSAGE = Template("""
<i>$fname $sname погладил котика.</i>
Мурррррррр.
""")
DISAPPOINTED_CARE_MESSAGE = Template("""
<i>$fname $sname погладил котеку.</i>
Мур.
""")
SAD_CAT_MESSAGE = Template("""
Мямямяууууу...
""")
BAD_CARE_MESSAGE = Template("""
<i>$cat_name недоволен и цапает $fname $sname за палец.</i>
ШШШШ.
""")

# SLEEP_HUNGER = Template("""
# <i> У котик
# """)

AGRESSIVE_MESSAGES = [
    "ШШШшШшШ!!!",
    "ШшШшШшШшшшшш!",
    "МмшшшШШШШ!",
    "Шшшшшшшшшшшшш....",
]

MEW = [
    "МЯУ!",
    "Мяу!",
    "Мяяяяу",
    "Мияу",
    "Меяу",
]
MEW_TRIGGER = ["мяу", "ня"]

INITAL_WEIGHT = 5

CAT_HUG = Template("""<i>
$fname $sname обнимает котика.
$cat_name ${cat_action}. На вскидку котейка весит </i><b> ${weight} </b><i>кило и, кажется, $weight_action
</i>""")
HUG_GOOD_CARMA = "радостно мурчит"
HUG_BAD_CARMA = "шипит и вырывается"
HUG_NO_CARMA = "недоуменно мяукает"
CAT_FAT = "продолжает толстеть."
CAT_THIN = "продолжает худеть."
CAT_NORMAL = "вполне этим доволен."

FAT = Template("<i>$cat_name толстеет.</i>")
THIN = Template("<i>$cat_name худеет.</i>")


SHOW_MESSAGE = Template("""<i>
$fname $sname поехал с котиком на выставку
</i>""")

OUR_RANK = Template("""
<i>$cat_name занял</i> <b>$pos</b> <i>место с</i> <b>$weight</b> <i>кило</i>
""")
FULL_TABLE_MESSAGE = "<i>Верх таблицы выглядит так </i>"
TABLE_ROW = Template("""<pre>
$pos - $cat_name весом $weight c хозяином $fname $sname представляющим $org_name
</pre>
""")
