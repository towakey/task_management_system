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

form = cgi.FieldStorage()
path_info = os.environ.get('PATH_INFO', '')

str_code = "utf-8"
config = configparser.ConfigParser()
config.read('./config.ini', encoding=str_code)

db_name = config['DB']['TMS']
log_file_url = config['LOG']['URL']

# form = cgi.FieldStorage()
username = form.getvalue("user_name", "") # user_nameパラメータを取得
user_id = form.getvalue("user_id", "") # user_nameパラメータを取得

def log(filename, text):

    filefullname = f"{log_file_url}/{filename}.log"
    # errorfilename = f"{url}/error.log"
    try:
        with open(filefullname, "a", encoding="utf-8") as f:  # "a" モードで開く
            f.write("["+datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")+"]\n")
            f.write(str(text)+"\n")
        # print(f"テキストを {filename} に追記しました。")

    except Exception as e:
        # print(f"エラーが発生しました: {e}")
        with open(filefullname, "a", encoding="utf-8") as f:  # "a" モードで開く
            f.write("["+datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")+"]\n")
            f.write(str(e)+"\n")

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

def register_user(conn, username):
    """ユーザーを登録する。既に存在する場合はエラーを返す。"""
    try:
        cursor = conn.cursor()

        # 既に同じuser_nameが存在するか確認
        cursor.execute(f"SELECT * FROM user WHERE user_name = '{username}'")
        existing_user = cursor.fetchone()

        if existing_user:
            result = {"status": "error", "message": "既に登録されているユーザー名です。"}
            log("user", str(result))
            return result

        user_id = str(uuid.uuid4())
        created_date = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        cursor.execute(f"INSERT INTO user (id, user_name, created_date) VALUES ('{user_id}', '{username}', '{created_date}')")
        conn.commit()
        result = {"status": "success", "message": "登録成功"}
        log("user", str(result))
        return result

    except sqlite3.IntegrityError:  # UNIQUE制約違反のエラーをキャッチ
        result = {"status": "error", "message": "既に登録されているユーザー名です。"}
        log("user", result)
        return result
    except Exception as e:
        result = {"status": "error", "message": f"データベースエラー: {e}"}
        log("user", str(result))
        # print(f"エラー発生場所: {traceback.format_exc()}")        
        log("user", f"エラー発生場所: {traceback.format_exc()}")        
        return result

def delete_record(table, column, value):
    result = False
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            log("user", f"DELETE FROM {table} WHERE {column} = '{value}'")
            cursor.execute(f"DELETE FROM {table} WHERE {column} = '{value}'")
            conn.commit()
            result = "success"
    except Exception as e:
        log("user", f"エラー: {traceback.format_exc()}")
    return result

if __name__ == '__main__':

    if path_info == '':
        result = {"status": "error", "message": f"データベース接続エラー"}
        print("Content-Type: application/json\n")
        print(json.dumps(result))
    elif path_info == '/user/registry':
        try:
            with sqlite3.connect(db_name) as conn:
                create_table_if_not_exists(conn) # テーブルが存在しない場合は作成
                if username:
                    log("user", form)
                    result = register_user(conn, username)
                else:
                    result = {"status": "error", "message": "ユーザー名が入力されていません。"}

        except Exception as e:
            result = {"status": "error", "message": f"データベース接続エラー: {e}"}

        # result = {"status": "success", "message": f"user registry"}
        print("Content-Type: application/json\n")
        print(json.dumps(result))
    elif path_info == '/user/delete':
        try:
            status = "False"
            if user_id:
                status = delete_record("user", "id", user_id)
                message = "ユーザーが削除されました"
            else:
                status = "False"
                message = "IDがありません"

        except Exception as e:
            status = "False"
            message = "エラーが発生しました"
            # log.add("user/delete", f"エラー: {traceback.format_exc()}")        


        result = {"status": status, "message": message}
        log("user", str(result))

        print("Content-Type: application/json\n")
        print(json.dumps(result))
