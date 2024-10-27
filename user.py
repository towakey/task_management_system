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

import header
import footer
import log

cgitb.enable(display=1, logdir=None, context=5, format='html')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

form = cgi.FieldStorage()
mode = form.getfirst("mode", '')

db_name = "tms.db"

def init():
    if not os.path.exists(db_name):
        try:
            conn = sqlite3.connect(db_name)
            conn.close()
            log.add("db","データベースファイルの作成")
        except Exception as e:
            log.add("db",f"データベースファイルの作成に失敗{e}")

if __name__ == '__main__':
    init()
    print('Content-type: text/html; charset=UTF-8\r\n')
    header.header()
    if mode == "":
        print(f"""
<div class="container">
    <div class="card">
        <div class="card-body">
            <div class="card-title">ユーザー操作</div>
            <div class="card-text">
                <ul class="list-group">
                    <a href="./user.py?mode=registry"><li class="list-group-item">ユーザー登録</li></a>
                    <a href="./user.py?mode=delete"><li class="list-group-item">ユーザー削除</li></a>
                </ul>
            </div>
        </div>
    </div
</div>
""")
    elif mode == "registry":
        print("""
    <script>
        function submitForm() {
            const username = document.getElementById("username").value;

            // フォームデータを作成
            const formData = new FormData();
            formData.append("user_name", username);


            // AJAXリクエストを送信
            fetch("user/registry.py", {
                method: "POST",
                body: formData
            })
            .then(response => response.json()) // レスポンスをJSONとしてパース
            .then(data => {
                if (data.status === "success") {
                    // 成功時の処理 (例: リダイレクト)
                    window.location.href = "user.py"; // または他のページへ
                } else {
                    // エラー時の処理
                    alert(data.message);
                }
            })
            .catch(error => {
                // ... (エラー処理)
            });

        }

    </script>
""")
        print(f"""
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
""")
    elif mode == "delete":
        print(f"""
<div class="container">
    <div class="card">
        <div class="card-body">
            <div class="card-title">ユーザー削除</div>
            <div class="card-text">
            </div>
        </div>
    </div
</div>
""")

    footer.footer()