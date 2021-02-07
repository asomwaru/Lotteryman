import random

import discord
import pymongo
from pymongo import MongoClient


def rand_col() -> int:
    r = lambda: random.randint(0, 255)
    color = '%02X%02X%02X' % (r(), r(), r())

    return int(color, 16)

def format_num(num:int) -> str:
    if num >= 1000:
        num = f"{str(num)[:-3]},{str(num)[-3:]}"
    else:
        num = str(num)

    return num