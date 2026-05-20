"""child_info.py
対象者（子ども）の情報を取得するモジュール。
検索画面で user_id とフリガナを照合して存在確認を行う。
"""

import conn_db

def get_child_info(user_id, name):
    """指定された user_id とフリガナに一致するユーザーが存在するか確認する。

    Parameters
    ----------
    user_id : str
        入力されたユーザーID（接種対象者ID）
    name : str
        入力されたフリガナ

    Returns
    -------
    bool
        該当ユーザーが存在すれば True、存在しなければ False。
    """
    conn = conn_db.get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE id = %s AND furigana = %s",
            (user_id, name)
        )
        result = cursor.fetchone()
    finally:
        conn.close()
    return result is not None