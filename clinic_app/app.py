# clinic_app: 医療機関側の接種記録管理アプリ
# ログイン → 対象者検索 → 接種記録更新 の流れで動作

from flask import Flask, request, redirect, url_for, render_template, session
import vaccination_data
import clinic_info
import child_info
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

DEFAULT_PASSWORD = "pass456"

@app.route("/", methods=["GET", "POST"])
def login():
    """医療機関ログイン画面"""
    error = ""
    if request.method == "POST":
        clinic_id = request.form["clinic_id"]
        password = request.form["password"]
        user = clinic_info.get_clinic_info(clinic_id)
        if user:
            if password == DEFAULT_PASSWORD:
                session["clinic_id"] = clinic_id
                return redirect(url_for("search"))
            else:
                error = "パスワードが違います"
        else:
            error = "ユーザーIDが見つかりません"
    return render_template("login.html", error=error)      


@app.route("/search", methods=["GET", "POST"])
def search():
    """対象者検索画面"""
    error = ""
    if request.method == "POST":
        user_id = request.form["user_id"]
        name = request.form["name"]
        if child_info.get_child_info(user_id, name):
            session["user_id"] = user_id
            return redirect(url_for("vaccination_page"))
        else:
            error = "対象者が見つかりません"
    return render_template("search.html", error=error)


@app.route("/vaccination", methods=["GET", "POST"])
def vaccination_page():
    """接種記録管理画面"""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("search"))
    
    if request.method == "POST":
        action = request.form.get("action")
        selected_index = request.form.get("selected_record")
        
        if selected_index is not None:
            index = int(selected_index) - 1  # Jinja2のloop.indexは1始まり
            new_date = request.form.get(f"new_date_{selected_index}")
            
            if action == "add" and new_date:
                vaccination_data.update_record(user_id, index, new_date)
                
            elif action == "delete":
                vaccination_data.delete_record(user_id, index)
                
        user_info, records = vaccination_data.get_vac_record(user_id)
        return render_template("vaccination.html", user=user_info, records=records, today=date.today().isoformat())
    
    user_info, records = vaccination_data.get_vac_record(user_id)
    return render_template("vaccination.html", user=user_info, records=records, today=date.today().isoformat())


if __name__ == '__main__':
    app.run(debug=True)          