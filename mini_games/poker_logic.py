import random
from collections import Counter

RANK_ORDER = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
SUITS = ["♠", "♥", "♦", "♣"]

PAYTABLE = {
    "royal_flush": 250,
    "straight_flush": 50,
    "four_of_a_kind": 25,
    "full_house": 9,
    "flush": 6,
    "straight": 4,
    "three_of_a_kind": 3,
    "two_pair": 2,
    "jacks_or_better": 1,
    "nothing": 0,
}

HAND_LABELS = {
    "royal_flush": "ロイヤルフラッシュ",
    "straight_flush": "ストレートフラッシュ",
    "four_of_a_kind": "フォーカード",
    "full_house": "フルハウス",
    "flush": "フラッシュ",
    "straight": "ストレート",
    "three_of_a_kind": "スリーカード",
    "two_pair": "ツーペア",
    "jacks_or_better": "ワンペア（J以上）",
    "nothing": "役なし",
}

def create_deck():
    """1組52枚のトランプを作り、シャッフルして返す"""
    deck = [{"rank": rank, "suit": suit} for suit in SUITS for rank in RANK_ORDER]
    random.shuffle(deck)
    return deck

def card_label(card):
    """カード1枚を表示用の文字列にする（例: "A♠"）"""
    return f"{card['rank']}{card['suit']}"

def _rank_value(rank):
    """ランクを2〜14の数値に変換する（A=14）"""
    return RANK_ORDER.index(rank) + 2

def evaluate_hand(hand):
    """
    5枚の手札から役を判定する。
    戻り値: 役のキー（PAYTABLEやHAND_LABELSのキーと対応）
    """
    ranks = [card["rank"] for card in hand]
    suits = [card["suit"] for card in hand]
    values = sorted(_rank_value(r) for r in ranks)

    is_flush = len(set(suits)) == 1

    distinct_values = sorted(set(values))
    is_straight = False
    if len(distinct_values) == 5:
        if distinct_values[4] - distinct_values[0] == 4:
            is_straight = True
        elif distinct_values == [2, 3, 4, 5, 14]:  # A-2-3-4-5（ホイール）も許可
            is_straight = True

    counts = Counter(ranks)
    count_pattern = sorted(counts.values(), reverse=True)

    if is_straight and is_flush:
        if distinct_values == [10, 11, 12, 13, 14]:
            return "royal_flush"
        return "straight_flush"

    if count_pattern == [4, 1]:
        return "four_of_a_kind"

    if count_pattern == [3, 2]:
        return "full_house"

    if is_flush:
        return "flush"

    if is_straight:
        return "straight"

    if count_pattern == [3, 1, 1]:
        return "three_of_a_kind"

    if count_pattern == [2, 2, 1]:
        return "two_pair"

    if count_pattern == [2, 1, 1, 1]:
        pair_rank = [r for r, c in counts.items() if c == 2][0]
        if pair_rank in ["J", "Q", "K", "A"]:
            return "jacks_or_better"
        return "nothing"

    return "nothing"

def get_multiplier(hand_key):
    """役のキーから配当倍率を返す"""
    return PAYTABLE.get(hand_key, 0)

def get_label(hand_key):
    """役のキーから日本語の表示名を返す"""
    return HAND_LABELS.get(hand_key, "役なし")