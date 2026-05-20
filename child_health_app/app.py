"""child_health_app/app.py
子ども側の予防接種閲覧アプリ。
ログイン → マイページ → 接種履歴 の流れを管理する。
"""

from flask import Flask, request, redirect, url_for, render_template, session
from dotenv import load_dotenv
import mariadb
import os
from datetime import date

# 独自モジュール
import vaccine_status  # format_age, get_vaccine_status を使用

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("CHILD_APP_SECRET_KEY", "dev_secret_key")


def get_user_info(user_id):
    """ユーザー情報をDBから取得して辞書で返す。"""
    try:
        conn = mariadb.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, birth_date, gender, furigana FROM users WHERE id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        birthdate = result[1]
        
        return {
            "name": result[0],
            "birth_date": birthdate,
            "gender": result[2],
            "furigana": result[3],
            "age": vaccine_status.format_age(birthdate),
            "id": user_id
        }
        
    except mariadb.Error as e:
        print(f"[DB接続エラー] {e}")
        return None


@app.route("/", methods=["GET", "POST"])
def login():
    """ログイン画面（子ども側）"""
    error = ""
    
    if request.method == "POST":
        user_id = request.form["user_id"]
        password = request.form["password"]

        user = get_user_info(user_id)

        if user and password == "pass123":
            session["user_id"] = user_id
            return redirect(url_for("mypage"))
        else:
            error = "ユーザーIDまたはパスワードが違います"

    return render_template("login.html", error=error)

    
@app.route("/mypage")
def mypage():
    """マイページ（基本情報表示）"""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    user = get_user_info(user_id)
    if not user:
        return "ユーザーが見つかりません", 404

    return render_template("mypage.html", user=user)

                                                       
@app.route("/vaccination")
def vaccination():
    """予防接種履歴の一覧表示（フィルター付き）"""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    user = get_user_info(user_id)
    if not user:
        return "ユーザーが見つかりません", 404
    
    all_records = vaccine_status.get_vaccine_status(user_id)

    filter_type = request.args.get("filter", "all")

    if filter_type == "接種済み":
        records = [r for r in all_records if r["status"].startswith("接種済み")]
    elif filter_type == "接種可能":
        records = [r for r in all_records if r["status"] == "接種可能"]
    elif filter_type == "未接種":
        records = [r for r in all_records if r["status"] == "未接種"]
    else:
        records = all_records
        
    return render_template(
        "vaccination.html",
        user=user,
        records=records,
        filter_type=filter_type
    )


@app.route("/logout")
def logout():
    """ログアウト処理"""
    session.pop("user_id", None)
    return redirect(url_for("login"))  

    
if __name__ == '__main__':
    app.run(debug=True)