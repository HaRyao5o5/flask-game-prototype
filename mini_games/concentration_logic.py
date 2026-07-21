import random

VALUES = ["🍎", "🍌", "🍇", "🍉", "🍒", "🍑", "🍓", "🥝"]  # 8種類 × 2枚 = 16枚

def create_deck():
    """絵文字8種類を2枚ずつ、計16枚をシャッフルして返す"""
    deck = VALUES * 2
    random.shuffle(deck)
    return deck

def is_all_matched(matched):
    """全カードがペア成立済みかどうか"""
    return all(matched)

def cpu_choose_first(matched, memory, difficulty="easy"):
    """
    CPUが1枚目にめくるカードを選ぶ。
    normalの場合、記憶の中にペアが揃っている絵柄があれば、そのうち1枚を狙う。
    """
    unmatched_indices = [i for i, m in enumerate(matched) if not m]

    if difficulty == "normal":
        value_to_indices = {}
        for key, value in memory.items():
            idx = int(key)
            if idx in unmatched_indices:
                value_to_indices.setdefault(value, []).append(idx)
        for value, indices in value_to_indices.items():
            if len(indices) >= 2:
                return indices[0]

    return random.choice(unmatched_indices)

def cpu_choose_second(first_index, matched, memory, cards, difficulty="easy"):
    """
    CPUが2枚目にめくるカードを選ぶ。
    normalの場合、1枚目と同じ絵柄を記憶していればそこを狙う。
    """
    unmatched_indices = [i for i, m in enumerate(matched) if not m and i != first_index]

    if difficulty == "normal":
        first_value = cards[first_index]
        for idx in unmatched_indices:
            if memory.get(str(idx)) == first_value:
                return idx

    return random.choice(unmatched_indices)