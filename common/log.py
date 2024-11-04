# -*- coding: utf-8 -*-

import os
import io
import sys
import datetime
import configparser
import cgi
import cgitb
import uuid
import shutil
import sqlite3
import json
import traceback

cgitb.enable(display=1, logdir=None, context=5, format='html')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

str_code = "utf-8"
config = configparser.ConfigParser()
config.read('./config.ini', encoding=str_code)

log_file_url = os.getcwd()

def log(filename, text):

    filefullname = f"{log_file_url}/log/{filename}.log"
    try:
        with open(filefullname, "a", encoding="utf-8") as f:  # "a" モードで開く
            f.write("["+datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")+"]\n")
            f.write(str(text)+"\n")

    except Exception as e:
        with open(filefullname, "a", encoding="utf-8") as f:  # "a" モードで開く
            f.write("["+datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")+"]\n")
            f.write(str(e)+"\n")
