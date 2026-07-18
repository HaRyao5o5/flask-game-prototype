import random

HANDS = ["rock", "scissors", "paper"]

def judge(player_hand, cpu_hand):
    """
    プレイヤーとCPUの手を受け取り、"win" / "lose" / "draw" を返す
    """
    if player_hand == cpu_hand:
        return "draw"
    
    # プレイヤーが勝つ組み合わせ
    win_patterns = {
        ("rock", "scissors"),
        ("scissors", "paper"),
        ("paper", "rock")
    }

    if (player_hand, cpu_hand) in win_patterns:
        return "win"
    else:
        return "lose"
    
def cpu_choice():
    return random.choice(HANDS)