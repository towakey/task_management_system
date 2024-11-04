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
from common import log
from common import datebase as db

cgitb.enable(display=1, logdir=None, context=5, format='html')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

form = cgi.FieldStorage()
path_info = os.environ.get('PATH_INFO', '')

str_code = "utf-8"
config = configparser.ConfigParser()
config.read('./config.ini', encoding=str_code)

db_name = config['DB']['NAME']

# form = cgi.FieldStorage()
username = form.getvalue("user_name", "") # user_nameパラメータを取得
user_id = form.getvalue("user_id", "") # user_nameパラメータを取得
    

if __name__ == '__main__':
    db_path = f"{os.getcwd()}/{db_name}"
    db.datebase()

    if path_info == '':
        result = {"status": "false", "message": f"command not found"}
        print("Content-Type: application/json\n")
        print(json.dumps(result))
    elif path_info == '/task/list':
        try:
            db_item = ['id', 'title', 'contents', 'created_date' 'updated_date']
            with sqlite3.connect(db_path) as conn:
                
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM task")
                result_db = cursor.fetchall()
                result_list = [dict(zip(db_item, item)) for item in result_db]
            result = {"status": "true", "data": result_list} # 成功時はデータを返す
        except Exception as e:
            log.log("user", f"エラー発生場所: {traceback.format_exc()}")
            result = {"status": "false", "message": f"データベースエラー: {e}"}        
        log.log("task", result)

        print("Content-Type: application/json\n")
        print(json.dumps(result))

    elif path_info == '/task/registry':
        try:
            title = form.getvalue("title", "") # user_nameパラメータを取得
            contents = form.getvalue("contents", "") # user_nameパラメータを取得
            with sqlite3.connect(db_path) as conn:
                if title:
                    val = {}
                    # created_date = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                    # updated_date = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                    val["id"] = str(uuid.uuid4())
                    val["title"] = title
                    val["contents"] = contents
                    val["created_date"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                    val["updated_date"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                    log.log("task", val)

                    if db.datebase.record("insert", "task", val):
                        result = {"status": "true", "message": "Succcess"}
                    else:
                        result = {"status": "false", "message": "Registry fail"}
                else:
                    result = {"status": "false", "message": "User name not input"}
        except Exception as e:
            log.log("user", f"Error: {traceback.format_exc()}")
            result = {"status": "false", "message": f"データベース接続エラー: {e}"}
        log.log("user", result)

        print("Content-Type: application/json\n")
        print(json.dumps(result))

    elif path_info == '/user/list':
        try:
            db_item = ['id', 'user_name', 'created_date']
            with sqlite3.connect(db_path) as conn:
                
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user")
                result_db = cursor.fetchall()
                result_list = [dict(zip(db_item, item)) for item in result_db]
            result = {"status": "true", "data": result_list} # 成功時はデータを返す
        except Exception as e:
            log.log("user", f"エラー発生場所: {traceback.format_exc()}")
            result = {"status": "false", "message": f"データベースエラー: {e}"}        
        log.log("user", result)

        print("Content-Type: application/json\n")
        print(json.dumps(result))
    elif path_info == '/user/registry':
        try:
            with sqlite3.connect(db_path) as conn:
                if username:
                    val = {}
                    created_date = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                    val["id"] = str(uuid.uuid4())
                    val["user_name"] = username
                    val["created_date"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                    log.log("user", val)

                    if db.datebase.record("insert", "user", val):
                        result = {"status": "true", "message": "Succcess"}
                    else:
                        result = {"status": "false", "message": "Registry fail"}
                else:
                    result = {"status": "false", "message": "User name not input"}

        except Exception as e:
            log.log("user", f"Error: {traceback.format_exc()}")
            result = {"status": "false", "message": f"データベース接続エラー: {e}"}
        log.log("user", result)

        print("Content-Type: application/json\n")
        print(json.dumps(result))
    elif path_info == '/user/delete':
        status = "false"
        message = ""
        try:
            if user_id:
                val = {}
                val["id"] = user_id
                status = db.datebase.record("delete", "user", val)
                message = "ID delete complete"
            else:
                status = "false"
                message = "ID not found"

        except Exception as e:
            message = "Error"
            log.log("user", f"エラー: {traceback.format_exc()}")        


        result = {"status": status, "message": message}
        log.log("user", str(result))

        print("Content-Type: application/json\n")
        print(json.dumps(result))
