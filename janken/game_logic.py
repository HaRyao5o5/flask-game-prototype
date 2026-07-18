import random

HANDS = ["rock", "scissors", "paper"]

# player_handがこの値を出すと勝つ相手の手（＝CPUがこれを出すとプレイヤーが勝つ）
BEATEN_BY = {
    "rock": "scissors",
    "scissors": "paper",
    "paper": "rock",
}


def judge(player_hand, cpu_hand):
    """
    プレイヤーとCPUの手を受け取り、"win" / "lose" / "draw" を返す
    """
    if player_hand == cpu_hand:
        return "draw"

    win_patterns = {
        ("rock", "scissors"),
        ("scissors", "paper"),
        ("paper", "rock"),
    }

    if (player_hand, cpu_hand) in win_patterns:
        return "win"
    else:
        return "lose"


def cpu_choice(mode="normal", player_hand=None):
    """
    CPUの手を決める。
    mode="easy" の場合、60%の確率でプレイヤーが勝つ手を選ぶ（player_handが必要）。
    """
    if mode == "easy" and player_hand in BEATEN_BY:
        if random.random() < 0.6:
            return BEATEN_BY[player_hand]
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