"""cal_age.py
誕生日と基準日から「○歳○ヶ月」を計算するモジュール。
"""

from datetime import date

def calculate_age(birthdate, target_date):
    """誕生日と基準日から年齢（歳・ヶ月）を計算する。

    Parameters
    ----------
    birthdate : date
        生年月日
    target_date : date
        年齢を計算する基準日

    Returns
    -------
    str
        「X歳Yヶ月」の形式で返す。
    """
    years = target_date.year - birthdate.year
    months = target_date.month - birthdate.month
    
    # 日付がまだ来ていない場合は1ヶ月引く
    if target_date.day < birthdate.day:
        months -= 1
        
    # 月がマイナスなら前年に戻す
    if months < 0:
        years -= 1
        months += 12
        
    return f"{years}歳{months}ヶ月"