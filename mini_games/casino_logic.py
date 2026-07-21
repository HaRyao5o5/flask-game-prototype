STARTING_CHIPS = 100

GAME_WIN_REWARD = {
    "easy": 5,
    "normal": 15,
}

def create_wallet():
    """初期チップ額を返す"""
    return STARTING_CHIPS

def can_bet(chips, amount):
    """賭けようとしている額が、今の残高以下かどうか"""
    return 0 < amount <= chips

def apply_bet_result(chips, amount, multiplier):
    """
    賭け金(amount)に対する結果を反映する。
    multiplier:
      2.0  → 通常の勝ち(賭け金が2倍になって返ってくる、つまり+amount)
      1.5  → ブラックジャックの特別配当(+amount*1.5)
      1.0  → 引き分け(賭け金がそのまま返ってくる、増減なし)
      0.0  → 負け(賭け金を失う)
    戻り値: 更新後のchips
    """
    return chips - amount + int(amount * multiplier)

def add_bonus_chips(chips, amount=50):
    """チップが尽きた時などに、追加でチップを補充する"""
    return chips + amount

def add_game_reward(chips, difficulty="normal"):
    """
    通常ゲームで勝った時の報酬をチップに加算する。
    戻り値: (更新後のchips, 実際に加算した枚数)
    """
    amount = GAME_WIN_REWARD.get(difficulty, 10)
    return chips + amount, amount