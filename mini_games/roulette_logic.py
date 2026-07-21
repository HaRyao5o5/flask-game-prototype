import random

# ヨーロピアンルーレットの実際の色配置（0は緑）
RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}

def get_color(number):
    """指定した数字の色を返す（"red" / "black" / "green"）"""
    if number == 0:
        return "green"
    return "red" if number in RED_NUMBERS else "black"

def spin():
    """0〜36のどれかをランダムに返す"""
    return random.randint(0, 36)

def judge(number, bet_type, bet_value=None):
    """
    出た数字(number)に対して、賭け方(bet_type)が的中したかどうかを判定する。
    bet_type: "number" / "color" / "parity"
    bet_value:
      "number"の場合 → 賭けた数字(int)
      "color"の場合  → "red" または "black"
      "parity"の場合 → "even" または "odd"
    戻り値: (的中したかどうか(bool), 配当倍率(int))
    """
    if bet_type == "number":
        return (number == bet_value), 36

    if bet_type == "color":
        return (get_color(number) == bet_value), 2

    if bet_type == "parity":
        if number == 0:
            return False, 2  # 0は偶数にも奇数にも賭けの対象として認めない
        is_even = (number % 2 == 0)
        guessed_even = (bet_value == "even")
        return (is_even == guessed_even), 2

    return False, 0