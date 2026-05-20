"""vaccination_data.py
予防接種記録の取得・更新・削除を行うモジュール。
"""

import conn_db
import cal_age
from datetime import date, datetime

# 表示順を固定するためのワクチン一覧
# ※ vaccine_type テーブルの vaccine_name と一致している必要がある
VACCINE_TYPES = [
    "五種混合1回目", "五種混合2回目", "五種混合3回目", "五種混合4回目",
    "麻疹風疹（MR）1期", "麻疹風疹（MR）2期",
    "日本脳炎1期1回目", "日本脳炎1期2回目", "日本脳炎1期3回目", "日本脳炎2期",
    "HPVワクチン1回目", "HPVワクチン2回目"
]


def get_vac_record(user_id):
    """指定された user_id のユーザー情報と接種履歴を取得する。

    Parameters
    ----------
    user_id : str
        接種対象者のID

    Returns
    -------
    tuple
        (user_info: dict, records: list)
        user_info が None の場合は対象者が存在しない。
    """
    conn = conn_db.get_db_connection()
    if not conn:
        return None, []
    try:
        cursor = conn.cursor()        
        # ユーザー情報の取得
        cursor.execute(
            "SELECT name, furigana, id, birth_date FROM users WHERE id = %s",
            (user_id,)
        )
        user_row = cursor.fetchone()
        if not user_row:
            return None, []
        user_info = {
            "name": user_row[0],
            "furigana": user_row[1],
            "id": user_row[2],
            "birth_date": user_row[3],
            "age": cal_age.calculate_age(user_row[3], date.today())
        }        
        # 接種履歴の取得
        cursor.execute("""
            SELECT date_given, vaccine_name
            FROM vaccine_record
            INNER JOIN vaccine_type ON vaccine_record.vac_type_id = vaccine_type.id
            WHERE user_id = %s
        """, (user_id,))
        result = cursor.fetchall()
    finally:
        conn.close()
    
    # ワクチン一覧順に整形
    records = []
    for vac_name in VACCINE_TYPES:
        matched = [row for row in result if row[1] == vac_name]
        if matched:
            date_given = matched[0][0]
            age = cal_age.calculate_age(user_info["birth_date"], date_given)
        else:
            date_given = ""
            age = ""
        records.append({
            "vaccine_name": vac_name,
            "date_given": date_given,
            "age_at": age
        })
    return user_info, records
    
    
def update_record(user_id, index, new_date):
    """接種記録を更新または新規追加する。"""
     # 日付形式チェック
    try:
        new_date_obj = datetime.strptime(new_date, "%Y-%m-%d").date()
    except ValueError:
        print("日付形式が不正です")
        return False
    
    conn = conn_db.get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        vaccine_name = VACCINE_TYPES[index]
        # ワクチン種別ID取得
        cursor.execute(
            "SELECT id FROM vaccine_type WHERE vaccine_name = %s",
            (vaccine_name,)
        )
        vac_type_row = cursor.fetchone()
        if not vac_type_row:
            print("該当するワクチン種別が見つかりません")
            return False
        vac_type_id = vac_type_row[0]
        
        # 既存レコード確認
        cursor.execute("""
            SELECT id FROM vaccine_record
            WHERE user_id = %s AND vac_type_id = %s
        """, (user_id, vac_type_id))
        existing = cursor.fetchone()
        
        if existing:
            # 更新
            cursor.execute("""
                UPDATE vaccine_record
                SET date_given = %s
                WHERE user_id = %s AND vac_type_id = %s
            """, (new_date_obj, user_id, vac_type_id))
        else:
            # 新規追加
            cursor.execute("""
                INSERT INTO vaccine_record (user_id, vac_type_id, date_given)
                VALUES (%s, %s, %s)
            """, (user_id, vac_type_id, new_date_obj))
            
        conn.commit()
        return True
    
    finally:
        conn.close()
        

def delete_record(user_id, index):
    """接種記録を削除する。"""
    conn = conn_db.get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        vaccine_name = VACCINE_TYPES[index]
        
        # ワクチン種別ID取得
        cursor.execute(
            "SELECT id FROM vaccine_type WHERE vaccine_name = %s",
            (vaccine_name,)
        )
        vac_type_row = cursor.fetchone()
        if not vac_type_row:
            print("該当するワクチン種別が見つかりません")
            return False
        vac_type_id = vac_type_row[0]
        
        # 削除対象確認
        cursor.execute("""
            SELECT id FROM vaccine_record
            WHERE user_id = %s AND vac_type_id = %s
        """, (user_id, vac_type_id))
        if not cursor.fetchone():
            print("削除対象のレコードが存在しません")
            return False
        
        # 削除
        cursor.execute("""
            DELETE FROM vaccine_record
            WHERE user_id = %s AND vac_type_id = %s
        """, (user_id, vac_type_id))

        conn.commit()
        return True
    
    finally:
        conn.close()