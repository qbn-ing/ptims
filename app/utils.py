import csv
import io
import os
import random


def get_random_color():
    letters = '0123456789ABCDEF'
    color = '#'
    for i in range(6):
        color += letters[random.randint(0, 15)]
    return color




