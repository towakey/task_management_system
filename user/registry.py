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

cgitb.enable() # デバッグ用にエラー表示を有効化

str_code = "utf-8"
config = configparser.ConfigParser()
config.read('../config.ini', encoding=str_code)

db_name = config['DB']['TMS']

form = cgi.FieldStorage()
username = form.getvalue("user_name", "") # user_nameパラメータを取得

def create_db_if_not_exists():
    """データベースファイルが存在しない場合に作成する"""
    if not os.path.exists(db_name):
        try:
            conn = sqlite3.connect(db_name)
            conn.close()
            print(f"データベースファイル {db_name} を作成しました。", file=sys.stderr) # デバッグ用に出力 (本番環境ではコメントアウト)
            log.add("db", f"データベースファイル {db_name} を作成しました。")
        except Exception as e:
            print(f"データベースの作成に失敗しました: {e}", file=sys.stderr)  # デバッグ用に出力
            log.add("db", f"データベースの作成に失敗しました: {e}")

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
            log.add("db", str(result))
            return result

        user_id = str(uuid.uuid4())
        created_date = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        cursor.execute(f"INSERT INTO user (id, user_name, created_date) VALUES ('{user_id}', '{username}', '{created_date}')")
        conn.commit()
        result = {"status": "success", "message": "登録成功"}
        log.add("db", str(result))
        return result

    except sqlite3.IntegrityError:  # UNIQUE制約違反のエラーをキャッチ
        result = {"status": "error", "message": "既に登録されているユーザー名です。"}
        log.add("db", result)
        return result
    except Exception as e:
        result = {"status": "error", "message": f"データベースエラー: {e}"}
        log.add("db", str(result))
        # print(f"エラー発生場所: {traceback.format_exc()}")        
        log.add("db", f"エラー発生場所: {traceback.format_exc()}")        
        return result


# print('Content-type: text/html; charset=UTF-8\r\n')

create_db_if_not_exists() # データベースファイルの存在確認と作成

try:
    with sqlite3.connect(db_name) as conn:
        create_table_if_not_exists(conn) # テーブルが存在しない場合は作成
        if username:
            result = register_user(conn, username)
        else:
            result = {"status": "error", "message": "ユーザー名が入力されていません。"}

except Exception as e:
    result = {"status": "error", "message": f"データベース接続エラー: {e}"}


log.add("db", result)
print("Content-Type: application/json\n")
print(json.dumps(result))







# if username:
#     if not os.path.exists(db_name):
#         try:
#             conn = sqlite3.connect(db_name)
#             conn.close()
#             log.add("db","データベースファイルの作成")
#         except Exception as e:
#             # log.add("db",f"データベースファイルの作成に失敗{e}")
#             result = {"status": "error", "message": "データベースの作成に失敗"} # JSONデータを作成
#             print("Content-Type: application/json\n") # Content-Typeをapplication/jsonに設定
#             print(json.dumps(result)) # JSONデータを出力

#     result = {"status": "success", "message": "登録成功"} # JSONデータを作成
#     print("Content-Type: application/json\n") # Content-Typeをapplication/jsonに設定
#     print(json.dumps(result)) # JSONデータを出力

# else:
#     result = {"status": "error", "message": "ユーザー名が入力されていません。"} # エラー時のJSONデータ
#     print("Content-Type: application/json\n")
#     print(json.dumps(result))
