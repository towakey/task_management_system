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
id = form.getvalue("id", "") # user_nameパラメータを取得

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

def delete_user(conn, id):
    if id:
        try:
            with sqlite3.connect(db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM user WHERE id = '{id}'")
                conn.commit()
                result = {"status": "success", "message": "ユーザーを削除しました。"}
        except Exception as e:
            result = {"status": "error", "message": f"データベースエラー: {e}"}
            log.add("db", str(result))
            log.add("db", f"エラー発生場所: {traceback.format_exc()}")        
    else:
        result = {"status": "error", "message": "ユーザーIDが指定されていません。"}
    return result


create_db_if_not_exists() # データベースファイルの存在確認と作成

try:
    with sqlite3.connect(db_name) as conn:
        create_table_if_not_exists(conn) # テーブルが存在しない場合は作成
        if id:
            result = delete_user(conn, id)
        else:
            result = {"status": "error", "message": "ユーザー名が入力されていません。"}

except Exception as e:
    result = {"status": "error", "message": f"データベース接続エラー: {e}"}
    log.add("db", str(result))
    log.add("db", f"エラー発生場所: {traceback.format_exc()}")        


log.add("db", result)
print("Content-Type: application/json\n")
print(json.dumps(result))
