"""vaccine_status.py
子どもの予防接種スケジュールと接種状況を取得するモジュール。
"""

import mariadb
from datetime import date
from dotenv import load_dotenv
import os

load_dotenv()


# -----------------------------
# 年齢計算（○歳○ヶ月）
# -----------------------------
def format_age(birthdate, target_date=None):
    """誕生日と対象日から「X歳Yヶ月」を返す。"""
    if target_date is None:
        target_date = date.today()
    years = target_date.year - birthdate.year
    months = target_date.month - birthdate.month
    # 誕生日の「日」がまだ来ていなければ1ヶ月引く
    if target_date.day < birthdate.day:
        months -= 1
    # 月がマイナスになったら年を調整
    if months < 0:
        years -= 1
        months += 12
    return f"{years}歳{months}ヶ月"


# -----------------------------
# 月齢計算（何ヶ月か）
# -----------------------------
def calculate_months(birthdate):
    """誕生日から今日までの月齢を返す。"""
    today = date.today()
    return (
        (today.year - birthdate.year) * 12
        + (today.month - birthdate.month)
        - (1 if today.day < birthdate.day else 0)
    )


# -----------------------------
# 予防接種ステータス取得
# -----------------------------
def get_vaccine_status(user_id):
    """ユーザーの予防接種スケジュールと接種状況を返す。"""
    try:
        conn = mariadb.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()
        
        # --- 誕生日取得 ---
        cursor.execute("SELECT birth_date FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()

        if not result:
            print("ユーザー情報が見つかりません")
            return []

        birthdate = result[0]
        age_in_months = calculate_months(birthdate)
        
        # --- スケジュール + 接種履歴取得 ---
        cursor.execute("""
            SELECT
                vs.id,
                vt.vaccine_name,
                vs.note,
                vs.min_age_months,
                vs.max_age_months,
                vr.date_given
            FROM vaccine_schedule vs
            JOIN vaccine_type vt ON vs.vac_type_id = vt.id
            LEFT JOIN vaccine_record vr
                ON vr.vac_type_id = vt.id AND vr.user_id = %s
            ORDER BY vs.id
        """, (user_id,))
        
        records = []

        for row in cursor.fetchall():
            schedule_id, vaccine_name, note, min_age, max_age, date_given = row
            
            # --- 接種済み ---
            if date_given:
                status = f"接種済み({date_given})"
                display_date = date_given.strftime("%Y-%m-%d")
                age_at = format_age(birthdate, date_given)

            # --- 接種可能 ---
            elif min_age <= age_in_months <= max_age:
                status = "接種可能"
                display_date = "接種可能"
                age_at = "-"
                
            # --- 未接種 ---
            else:
                status = "未接種"
                display_date = "未接種"
                age_at = "-"
                
            records.append({
                "vaccine_name": vaccine_name, 
                "note": note,
                "status": status,
                "age_range": f"{min_age}～{max_age}ヶ月",
                "date": display_date,
                "age_at": age_at
            })

        conn.close()
        return records

    except mariadb.Error as e:
        print(f"データ取得エラー: {e}")
        return []           