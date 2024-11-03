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

def create_table_if_not_exists(conn):
    """userテーブルが存在しない場合に作成する"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id TEXT PRIMARY KEY,
            user_name TEXT UNIQUE NOT NULL,  -- UNIQUE制約を追加
            created_date TEXT
        )
    """)
    conn.commit()

def create_db_if_not_exists():
    """データベースファイルが存在しない場合に作成する"""
    db = f"{os.getcwd()}/{db_name}"
    if not os.path.exists(db):
        try:
            conn = sqlite3.connect(db)
            conn.close()
            print(f"データベースファイル {db} を作成しました。", file=sys.stderr) # デバッグ用に出力 (本番環境ではコメントアウト)
            log.add("db", f"データベースファイル {db} を作成しました。")
        except Exception as e:
            print(f"データベースの作成に失敗しました: {e}", file=sys.stderr)  # デバッグ用に出力
            log.add("db", f"データベースの作成に失敗しました: {e}")

def register_user(conn, username):
    """ユーザーを登録する。既に存在する場合はエラーを返す。"""
    result = False
    try:
        cursor = conn.cursor()

        user_id = str(uuid.uuid4())
        created_date = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        cursor.execute(f"INSERT INTO user (id, user_name, created_date) VALUES ('{user_id}', '{username}', '{created_date}')")
        conn.commit()
        # result = {"status": "success", "message": "登録成功"}
        result = True

    except sqlite3.IntegrityError:  # UNIQUE制約違反のエラーをキャッチ
        log.log("user", "USER unique error")
        log.log("user", result)
    except Exception as e:
        log.log("user", str(e))
        log.log("user", traceback.format_exc())        

    return result
    

def record(command, table, column, value):
    result = "false"
    db = f"{os.getcwd()}/{db_name}"
    try:
        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()
            if command == 'insert':
                pass
            elif command == 'delete':
                sql = f"DELETE FROM {table} WHERE {column} = '{value}'"
            log.log("user", sql)
            cursor.execute(sql)
            conn.commit()
            result = "true"
    except Exception as e:
        log.log("user", f"エラー: {traceback.format_exc()}")
    return result

if __name__ == '__main__':
    db = f"{os.getcwd()}/{db_name}"

    if path_info == '':
        result = {"status": "false", "message": f"command not found"}
        print("Content-Type: application/json\n")
        print(json.dumps(result))
    elif path_info == '/user/list':
        try:
            db_item = ['id', 'user_name', 'created_date']
            with sqlite3.connect(db) as conn:
                create_table_if_not_exists(conn) # テーブルが存在しない場合は作成
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
            with sqlite3.connect(db) as conn:
                create_table_if_not_exists(conn) # テーブルが存在しない場合は作成
                if username:
                    log.log("user", form)
                    if register_user(conn, username):
                        result = {"status": "true", "message": "Succcess"}
                    else:
                        result = {"status": "false", "message": "Registry fail"}
                else:
                    result = {"status": "false", "message": "User name not input"}

        except Exception as e:
            result = {"status": "false", "message": f"データベース接続エラー: {e}"}
        log.log("user", result)

        print("Content-Type: application/json\n")
        print(json.dumps(result))
    elif path_info == '/user/delete':
        status = "false"
        message = ""
        try:
            if user_id:
                status = record("delete", "user", "id", user_id)
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
