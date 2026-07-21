import random

# 絵柄ごとの「出現ウェイト」と「3つ揃った時の配当倍率」
# ウェイトが小さいほどレア、レアな絵柄ほど配当を高くしてバランスを取る
SYMBOLS = [
    {"symbol": "🍒", "weight": 40, "triple_multiplier": 3},
    {"symbol": "🍋", "weight": 30, "triple_multiplier": 5},
    {"symbol": "🔔", "weight": 18, "triple_multiplier": 10},
    {"symbol": "💎", "weight": 9,  "triple_multiplier": 25},
    {"symbol": "7️⃣", "weight": 3,  "triple_multiplier": 50},
]

# 2つだけ揃った場合の配当倍率（絵柄の種類を問わず一律）
DOUBLE_MULTIPLIER = 1.5

def _weighted_choice():
    """SYMBOLSの重みに応じて1つの絵柄を選ぶ"""
    symbols = [s["symbol"] for s in SYMBOLS]
    weights = [s["weight"] for s in SYMBOLS]
    return random.choices(symbols, weights=weights, k=1)[0]

def spin():
    """3つのリールの絵柄を決めて、リストで返す（例: ["🍒", "🍒", "🔔"]）"""
    return [_weighted_choice() for _ in range(3)]

def _triple_multiplier(symbol):
    """指定した絵柄の3つ揃い配当倍率を返す"""
    for s in SYMBOLS:
        if s["symbol"] == symbol:
            return s["triple_multiplier"]
    return 0

def judge(reels):
    """
    3つのリールの結果を判定し、配当倍率を返す。
    戻り値: (multiplier, result_type)
    result_type: "triple" / "double" / "lose"
    """
    if reels[0] == reels[1] == reels[2]:
        return _triple_multiplier(reels[0]), "triple"

    if reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]:
        return DOUBLE_MULTIPLIER, "double"

    return 0, "lose"