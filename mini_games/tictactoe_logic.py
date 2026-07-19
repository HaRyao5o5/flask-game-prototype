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
    if difficulty == "easy":
        return _cpu_move_easy(board)
    elif difficulty == "normal":
        return _cpu_move_normal(board)
    else:
        return _cpu_move_normal(board)

def _cpu_move_easy(board):
    """空いているマスからランダムに選ぶ"""
    empty_cells = [(r, c) for r in range(3) for c in range(3) if board[r][c] == ""]
    return random.choice(empty_cells)

def _cpu_move_normal(board):
    """
    優先順位:
    1. 自分(O)が置いて勝てる手があればそれを選ぶ
    2. 相手(X)が置いたら勝ってしまう手があればブロックする
    3. 中央が空いていれば取る
    4. 角が空いていれば取る
    5. それ以外はランダム
    """
    empty_cells = [(r, c) for r in range(3) for c in range(3) if board[r][c] == ""]

    # 1. 勝てる手を探す（実際に置いてみて確認し、すぐ戻す）
    for r, c in empty_cells:
        board[r][c] = "O"
        won = check_winner(board) == "O"
        board[r][c] = ""
        if won:
            return (r, c)

    # 2. 相手の勝ち筋をブロックする手を探す
    for r, c in empty_cells:
        board[r][c] = "X"
        would_lose = check_winner(board) == "X"
        board[r][c] = ""
        if would_lose:
            return (r, c)

    # 3. 中央を優先
    if board[1][1] == "":
        return (1, 1)

    # 4. 角を優先
    corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
    empty_corners = [pos for pos in corners if board[pos[0]][pos[1]] == ""]
    if empty_corners:
        return random.choice(empty_corners)

    # 5. それ以外はランダム
    return random.choice(empty_cells)