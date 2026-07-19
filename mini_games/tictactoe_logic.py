import random

def create_board():
    """3x3の空の盤面を作る"""
    return [["" for _ in range(3)] for _ in range(3)]

def is_valid_move(board, row, col):
    """指定したマスに置けるかどうか"""
    return board[row][col] == ""

def place_mark(board, row, col, mark):
    """指定したマスにマークを置く"""
    board[row][col] = mark

def check_winner(board):
    """
    勝者を判定する。"X" / "O" / "draw" / None（まだ決着していない）を返す
    """
    lines = []

    for row in board:
        lines.append(row)

    for col in range(3):
        lines.append([board[row][col] for row in range(3)])

    lines.append([board[i][i] for i in range(3)])
    lines.append([board[i][2 - i] for i in range(3)])

    for line in lines:
        if line[0] != "" and line[0] == line[1] == line[2]:
            return line[0]

    if all(board[r][c] != "" for r in range(3) for c in range(3)):
        return "draw"

    return None

def cpu_move(board, difficulty="easy"):
    """
    CPUの手を決める。difficultyによって呼び分ける（今はeasyのみ実装済み）
    """
    if difficulty == "easy":
        return _cpu_move_easy(board)
    else:
        # 未実装の難易度が来たら、とりあえずeasyにフォールバック
        return _cpu_move_easy(board)

def _cpu_move_easy(board):
    """空いているマスからランダムに選ぶ"""
    empty_cells = [(r, c) for r in range(3) for c in range(3) if board[r][c] == ""]
    return random.choice(empty_cells)