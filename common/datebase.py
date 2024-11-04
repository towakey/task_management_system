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

str_code = "utf-8"
config = configparser.ConfigParser()
config.read('./config.ini', encoding=str_code)

db_name = config['DB']['NAME']

class datebase():
    def __init__(self) -> None:
        db = f"{os.getcwd()}/{db_name}"
        log.log("db", db)
        if not os.path.exists(db):
            try:
                conn = sqlite3.connect(db)
                conn.close()
                print(f"データベースファイル {db} を作成しました。", file=sys.stderr) # デバッグ用に出力 (本番環境ではコメントアウト)
                log.log("db", f"データベースファイル {db} を作成しました。")


            except Exception as e:
                print(f"データベースの作成に失敗しました: {e}", file=sys.stderr)  # デバッグ用に出力
                log.log("db", f"データベースの作成に失敗しました: {e}")

        conn = sqlite3.connect(db)

        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id TEXT PRIMARY KEY,
                user_name TEXT UNIQUE NOT NULL,  -- UNIQUE制約を追加
                created_date TEXT
            )
        """)
        conn.commit()

        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task (
                id TEXT PRIMARY KEY,
                title TEXT,
                contents TEXT,
                created_date TEXT,
                updated_date TEXT
            )
        """)
        conn.commit()

        conn.close()

    def record(command, table, dict):
        result = "false"
        db_path = f"{os.getcwd()}/{db_name}"
        log.log("db", dict)
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                if command == 'insert':
                    item = ""
                    val = ""
                    for key in dict:
                        item += f"{key},"
                        val += f"'{dict[key]}',"
                    item = item[:-1]
                    val = val[:-1]
                    sql = f"INSERT INTO {table} ({item}) VALUES ({val})"
                    log.log("db", sql)
                    cursor.execute(sql)
                    conn.commit()
                elif command == 'delete':
                    for key in dict:
                        log.log("db", key)
                        sql = f"DELETE FROM {table} WHERE {key} = '{dict[key]}'"
                        log.log("db", sql)
                        cursor.execute(sql)
                        conn.commit()
                result = "true"
        except Exception as e:
            log.log("db", f"エラー: {traceback.format_exc()}")
        return result
