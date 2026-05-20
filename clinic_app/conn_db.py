"""conn_db.py
MariaDB への接続を行うモジュール。
環境変数（.env）から接続情報を読み込み、安全に接続を確立する。
"""

import mariadb
import os
from dotenv import load_dotenv
load_dotenv()

def get_db_connection():
    """MariaDB への接続を確立して connection オブジェクトを返す。

    Returns
    -------
    connection or None
        接続成功時は connection オブジェクトを返す。
        接続に失敗した場合は None を返す。
    """
    try:
        conn = mariadb.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return conn
    except mariadb.Error as e:
        print(f"[DB接続エラー] {e}")
        return None