# -*- coding: utf-8 -*-

import os
import datetime
import configparser

mypath = os.getcwd()
str_code = "utf-8"

def add(filename, text):
    """
    指定されたファイルにテキストを追記します。ファイルが存在しない場合は作成します。

    Args:
        filename: ファイル名 (文字列)。
        text: 追記するテキスト (文字列)。
    """

    config = configparser.ConfigParser()
    config.read('../config.ini', encoding=str_code)

    url = config['LOG']['URL']

    filefullname = f"{url}/{filename}.log"
    errorfilename = f"{url}/error.log"
    try:
        with open(filefullname, "a", encoding="utf-8") as f:  # "a" モードで開く
            f.write("["+datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")+"]\n")
            f.write(str(text)+"\n")
        # print(f"テキストを {filename} に追記しました。")

    except Exception as e:
        # print(f"エラーが発生しました: {e}")
        with open(errorfilename, "a", encoding="utf-8") as f:  # "a" モードで開く
            f.write("["+datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")+"]\n")
            f.write(str(e)+"\n")
