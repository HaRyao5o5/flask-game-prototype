import random

HANDS = ["rock", "scissors", "paper"]

# キーの手が勝てる相手の手（例: "rock"は"scissors"に勝つ）
BEATEN_BY = {
    "rock": "scissors",
    "scissors": "paper",
    "paper": "rock",
}

# キーの手に勝つ手（BEATEN_BYの逆引き）
COUNTER_HAND = {v: k for k, v in BEATEN_BY.items()}

HABIT_THRESHOLD = 3  # この回数以上データが溜まってから「くせ」を利用する


def judge(player_hand, cpu_hand):
    """
    プレイヤーとCPUの手を受け取り、"win" / "lose" / "draw" を返す
    """
    if player_hand == cpu_hand:
        return "draw"

    if BEATEN_BY.get(player_hand) == cpu_hand:
        return "win"
    return "lose"


def predict_player_hand(hand_counts):
    """
    プレイヤーが最もよく出している手を予測する。
    データが少なければNoneを返す。
    """
    total = sum(hand_counts.values())
    if total < HABIT_THRESHOLD:
        return None
    return max(hand_counts, key=hand_counts.get)


def cpu_choice(mode="normal", player_hand=None, hand_counts=None):
    """
    CPUの手を決める。
    - mode="easy": 60%の確率でプレイヤーが勝つ手を選ぶ
    - mode="hard": プレイヤーのくせを分析し、65%の確率でそれに対抗する手を選ぶ
    - mode="normal": 完全ランダム
    """
    if mode == "easy" and player_hand in BEATEN_BY:
        if random.random() < 0.6:
            return BEATEN_BY[player_hand]

    if mode == "hard" and hand_counts:
        predicted = predict_player_hand(hand_counts)
        if predicted and random.random() < 0.65:
            return COUNTER_HAND[predicted]

    return random.choice(HANDS)


def match_winner(set_wins, target):
    """
    3本先取の勝者を判定する。まだ決着していなければNoneを返す。
    """
    if set_wins["player"] >= target:
        return "player"
    if set_wins["cpu"] >= target:
        return "cpu"
    return None