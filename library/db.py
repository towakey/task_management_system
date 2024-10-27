# -*- coding: utf-8 -*-
import os
import sys
import cgi
import cgitb
import json
import sqlite3
import datetime
import uuid
import configparser
import traceback

sys.path.append('../')
import log

str_code = "utf-8"
config = configparser.ConfigParser()
config.read('config.ini', encoding=str_code)

db_name = config['DB']['TMS']
def get_user_list():
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()

            # 既に同じuser_nameが存在するか確認
            cursor.execute(f"SELECT * FROM user")
            result = cursor.fetchone()
    except Exception as e:
        result = {"status": "error", "message": f"データベース接続エラー: {e}"}
        log.add("db", str(result))
        log.add("db", f"エラー発生場所: {traceback.format_exc()}")        
    return result
