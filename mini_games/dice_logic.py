import random

def roll_dice():
    """サイコロを2つ振って、その目をタプルで返す（例: (3, 5)）"""
    return random.randint(1, 6), random.randint(1, 6)

def judge_cho_han(dice):
    """
    2つの目の合計が偶数(丁)か奇数(半)かを判定する。
    戻り値: "cho"（丁）または "han"（半）
    """
    total = sum(dice)
    return "cho" if total % 2 == 0 else "han"

def is_win(dice, bet_choice):
    """
    プレイヤーの予想(bet_choice: "cho" または "han")が当たったかどうか
    """
    return judge_cho_han(dice) == bet_choice