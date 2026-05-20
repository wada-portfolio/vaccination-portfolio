"""clinic_info.py
医療機関（クリニック）の情報を取得するモジュール。
ログイン時に clinic_id をもとにクリニック名を取得する。
"""

import conn_db

def get_clinic_info(clinic_id):
    """指定された clinic_id のクリニック情報を取得する。

    Parameters
    ----------
    clinic_id : str
        ログインフォームで入力されたクリニックID

    Returns
    -------
    dict or None
        {"name": クリニック名} を返す。
        該当がなければ None を返す。
    """
    conn = conn_db.get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM clinics WHERE id = %s", (clinic_id,))
        result = cursor.fetchone()
    finally:
        conn.close()
    if result:
        return {"name": result[0]}
    return None