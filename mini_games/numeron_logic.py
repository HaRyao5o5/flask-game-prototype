import random

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

def cpu_guess(difficulty="easy", history=None):
    """
    CPUの予想を決める。今はeasyのみ実装（重複なしのランダムな3桁）
    historyは今後「これまでの結果を踏まえて絞り込む」CPUを作る時のための引数
    """
    if difficulty == "easy":
        return generate_secret_number()  # ランダム生成のロジックを予想生成に流用
    else:
        return generate_secret_number()