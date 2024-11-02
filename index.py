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
import traceback

cgitb.enable(display=1, logdir=None, context=5, format='html')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

form = cgi.FieldStorage()
path_info = os.environ.get('PATH_INFO', '')

str_code = "utf-8"
config = configparser.ConfigParser()
config.read('config.ini', encoding=str_code)

db_name = config['DB']['TMS']

def log(filename, text):
    str_code = "utf-8"
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

def get_user_list():
    try:
        db_item = ['id', 'user_name', 'created_date']
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()

            # 既に同じuser_nameが存在するか確認
            cursor.execute(f"SELECT * FROM user")
            result = []
            result_db = cursor.fetchall()
            for item in result_db:
                result.append(dict(zip(db_item, item)))
    except Exception as e:
        result = {"status": "error", "message": f"データベース接続エラー: {e}"}
        log("user", str(result))
        log("user", f"エラー発生場所: {traceback.format_exc()}")        
    return result

def header(hierarchy):
    place = "./"
    for i in range(hierarchy):
        place += "../"
    print(f"""
<html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>TaskManagementSystem</title>
        <link rel="stylesheet" href="{place}css/bootstrap.css">
        <script src="{place}js/bootstrap.bundle.js"></script>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-light bg-light">
            <div class="container-fluid">
                <a class="navbar-brand" href="{place}index.py">TaskManagementSystem</a>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav">
                        <li class="nav-item">
                            <a class="nav-link" href="{place}index.py/user">ユーザー</a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
""")

def footer():
    print("""
    </body>
</html>
""")

if __name__ == '__main__':
    print('Content-type: text/html; charset=UTF-8\r\n')
    if path_info == '':
        header(0)
        print(path_info)
        footer()
    elif path_info == '/user':
        header(1)
        print(f"""
<div class="container">
    <div class="card">
        <div class="card-body">
            <div class="card-title">ユーザー操作</div>
            <div class="card-text">
                <ul class="list-group">
                    <a href="./user/registry"><li class="list-group-item">ユーザー登録</li></a>
                    <a href="./user/delete"><li class="list-group-item">ユーザー削除</li></a>
                </ul>
            </div>
        </div>
    </div
</div>
""")
        footer()
    elif path_info == '/user/registry':
        header(2)
        print("""
<div class="container">
    <div class="card">
        <div class="card-body">
            <div class="card-title">ユーザー登録</div>
            <div class="card-text">
                <div class="input-group mb-3">
                    <input type="text" id="username" class="form-control" placeholder="ユーザー名を入力してください" aria-label="Username" aria-describedby="basic-addon1">
                </div>
                <div class="d-grid gap-2">
                    <button class="btn btn-outline-primary" type="button" onclick="submitForm()">送信</button>
                </div>
            </div>
        </div>
    </div
</div>
    <script>
        function submitForm() {
            const username = document.getElementById("username").value;

            // フォームデータを作成
            const formData = new FormData();
            formData.append("user_name", username);
              
            console.log(formData)


            // AJAXリクエストを送信
            fetch("./../../api.py/user/registry", {
                method: "POST",
                body: formData
            })
            .then(response => response.json()) // レスポンスをJSONとしてパース
            .then(data => {
                if (data.status === "success") {
                    // 成功時の処理 (例: リダイレクト)
                    window.location.href = "../user"; // または他のページへ
                } else {
                    // エラー時の処理
                    alert(data.message);
                }
            })
            .catch(error => {
                // エラー時の処理
                alert(error);
            });

        }

    </script>
""")
        footer()

    elif path_info == '/user/delete':
        header(2)
        print(f"""
<div class="container">
    <div class="card">
        <div class="card-body">
            <div class="card-title">ユーザー削除</div>
            <div class="card-text">
                <ul class="list-group" id="user-list">
""")
        for item in get_user_list():
            print(f"""
                    <li class="list-group-item d-flex justify-content-between align-items-center" data-userid="{item['id']}">
                        {item['user_name']}
                        <button class="btn btn-danger delete-button" data-userid="{item['id']}">削除</button>
                    </li>
""")
        # print(str(db.get_user_list()))
        print(f"""
                </ul>
            </div>
        </div>
    </div
</div>
<script>
    const userList = document.getElementById('user-list');
    userList.addEventListener('click', (event) => {{
        if (event.target.classList.contains('delete-button')) {{
            const userId = event.target.dataset.userid;
            // フォームデータを作成
            const formData = new FormData();
            formData.append("user_id", userId);

            fetch(`./../../api.py/user/delete`, {{ method: 'POST', body: formData }})
            .then(response => response.json())
            .then(data => {{
                if (data.status === "success") {{
                    // 削除成功時の処理
                    //alert('ユーザーを削除しました。');
                    //event.target.closest('li').remove(); // 削除したユーザーをリストから削除
                    // またはページ全体をリロード: location.reload();
                    window.location.href = "../user";
                }} else {{
                    alert(data.message);
                }}
            }})
            .catch(error => {{
                console.error('Error:', error);
                alert('エラーが発生しました。');
            }});
        }}
    }});
</script>
""")
        footer()
