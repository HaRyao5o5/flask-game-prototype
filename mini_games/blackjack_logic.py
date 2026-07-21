import random

RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = ["♠", "♥", "♦", "♣"]

def create_shoe():
    """1組52枚のトランプを作り、シャッフルして返す"""
    deck = [{"rank": rank, "suit": suit} for suit in SUITS for rank in RANKS]
    random.shuffle(deck)
    return deck

def card_label(card):
    """カード1枚を表示用の文字列にする（例: "A♠"）"""
    return f"{card['rank']}{card['suit']}"

def hand_value(hand):
    """
    手札の合計値を計算する。Aは1か11のうち、バーストしない方を自動選択する。
    戻り値: 合計値(int)
    """
    total = 0
    ace_count = 0

    for card in hand:
        rank = card["rank"]
        if rank == "A":
            ace_count += 1
            total += 11
        elif rank in ["J", "Q", "K"]:
            total += 10
        else:
            total += int(rank)

    # Aを11として数えた結果21を超えていたら、1つずつ1として数え直す
    while total > 21 and ace_count > 0:
        total -= 10
        ace_count -= 1

    return total

def is_bust(hand):
    """手札が21を超えている(バーストしている)かどうか"""
    return hand_value(hand) > 21

def is_blackjack(hand):
    """最初の2枚でちょうど21(ブラックジャック)かどうか"""
    return len(hand) == 2 and hand_value(hand) == 21

def deal_initial_hands(shoe):
    """
    山札(shoe)から、プレイヤーとディーラーにそれぞれ2枚ずつ配る。
    戻り値: (player_hand, dealer_hand, 残りのshoe)
    """
    player_hand = [shoe.pop(), shoe.pop()]
    dealer_hand = [shoe.pop(), shoe.pop()]
    return player_hand, dealer_hand, shoe

def dealer_should_hit(dealer_hand):
    """
    ディーラーがヒットすべきかどうかを判定する。
    ルール: 17未満なら必ずヒット、17以上ならスタンド
    """
    return hand_value(dealer_hand) < 17

def judge(player_hand, dealer_hand):
    """
    決着を判定する。戻り値は次のいずれか:
    "player_blackjack" : プレイヤーがブラックジャックで勝利(配当1.5倍)
    "player_win"       : プレイヤーの通常勝利
    "dealer_win"       : ディーラーの勝利
    "push"             : 引き分け
    """
    player_total = hand_value(player_hand)
    dealer_total = hand_value(dealer_hand)

    if is_bust(player_hand):
        return "dealer_win"
    if is_bust(dealer_hand):
        return "player_win"

    if is_blackjack(player_hand) and not is_blackjack(dealer_hand):
        return "player_blackjack"
    if is_blackjack(dealer_hand) and not is_blackjack(player_hand):
        return "dealer_win"

    if player_total > dealer_total:
        return "player_win"
    elif dealer_total > player_total:
        return "dealer_win"
    else:
        return "push"