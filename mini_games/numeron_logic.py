import random
from itertools import permutations

def generate_secret_number():
    """
    0〜9の中から重複しない3桁の数字を生成する（例："192"）
    先頭が0でもOKとする（ヌメロンのルールに合わせるなら禁止することもあるが、今回はシンプルに許可）
    """
    digits = random.sample(range(10), 3)
    return "".join(str(d) for d in digits)

def is_valid_guess(guess):
    """
    予想が正しい形式かどうかをチェックする
    - 3桁の数字であること
    - すべて異なる数字であること
    """
    if len(guess) != 3:
        return False
    if not guess.isdigit():
        return False
    if len(set(guess)) != 3:
        return False
    return True

def judge(secret, guess):
    """
    秘密の数字(secret)と予想(guess)を比較し、EATとBITEの数を返す
    戻り値: (eat, bite)
    """
    eat = 0
    bite = 0

    for i in range(3):
        if guess[i] == secret[i]:
            eat += 1
        elif guess[i] in secret:
            bite += 1

    return eat, bite

def _all_candidates():
    """重複しない3桁の数字を全パターン列挙する（720通り）"""
    return ["".join(str(d) for d in p) for p in permutations(range(10), 3)]

def cpu_guess(difficulty="easy", history=None):
    if difficulty == "easy" or not history:
        return generate_secret_number()

    # これまでのCPU自身の予想と結果に矛盾しない候補だけに絞り込む
    candidates = _all_candidates()
    for turn in history:
        past_guess = turn['cpu_guess']
        past_eat = turn['cpu_eat']
        past_bite = turn['cpu_bite']
        candidates = [c for c in candidates if judge(c, past_guess) == (past_eat, past_bite)]

    if candidates:
        return random.choice(candidates)

    # 万が一候補が0件になった場合の保険（通常は起きないはず）
    return generate_secret_number()