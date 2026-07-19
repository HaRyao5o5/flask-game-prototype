import random

BOARD_SIZE = 8
EMPTY = ""
BLACK = "black"
WHITE = "white"

# 8方向（上下左右＋斜め4方向）を(行の増減, 列の増減)のタプルで表現
DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
]

COLUMN_LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

def create_board():
    """8x8の盤面を作り、中央4マスに初期配置をセットする"""
    board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    board[3][3] = WHITE
    board[3][4] = BLACK
    board[4][3] = BLACK
    board[4][4] = WHITE
    return board

def opponent(color):
    """相手の色を返す"""
    return WHITE if color == BLACK else BLACK

def _on_board(row, col):
    """盤面の範囲内かどうか"""
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

def _flippable_in_direction(board, row, col, color, d_row, d_col):
    """
    指定した1方向に、挟んでひっくり返せる石があるかを調べる。
    ひっくり返せる石の座標リストを返す（無ければ空リスト）
    """
    flippable = []
    r, c = row + d_row, col + d_col

    # まず相手の石が連続している間、座標を記録しながら進む
    while _on_board(r, c) and board[r][c] == opponent(color):
        flippable.append((r, c))
        r += d_row
        c += d_col

    # 相手の石の先に自分の石があれば、挟めている＝有効
    if _on_board(r, c) and board[r][c] == color and flippable:
        return flippable

    # 盤外に出た、空マスだった、自分の石が無かった場合は挟めていない
    return []

def get_flippable_cells(board, row, col, color):
    """
    指定したマスに置いた場合に、ひっくり返せる石を全方向分まとめて返す。
    空マスでない場合は空リストを返す（＝置けない）
    """
    if board[row][col] != EMPTY:
        return []

    all_flippable = []
    for d_row, d_col in DIRECTIONS:
        all_flippable += _flippable_in_direction(board, row, col, color, d_row, d_col)

    return all_flippable

def get_valid_moves(board, color):
    """
    colorが置けるマスの一覧を [(row, col), ...] の形で返す
    """
    valid_moves = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if get_flippable_cells(board, row, col, color):
                valid_moves.append((row, col))
    return valid_moves

def place_and_flip(board, row, col, color):
    """
    指定したマスにcolorの石を置き、挟んだ石をすべてひっくり返す。
    呼び出す前に get_flippable_cells 等で有効な手か確認しておくこと
    """
    flippable = get_flippable_cells(board, row, col, color)
    board[row][col] = color
    for r, c in flippable:
        board[r][c] = color

def count_stones(board):
    """
    (黒の数, 白の数) を返す
    """
    black = sum(row.count(BLACK) for row in board)
    white = sum(row.count(WHITE) for row in board)
    return black, white

def is_game_over(board):
    """
    両者とも置ける場所が無ければ終局とみなす
    """
    return not get_valid_moves(board, BLACK) and not get_valid_moves(board, WHITE)

def judge_winner(board):
    """
    石数を比較して勝者を返す。"black" / "white" / "draw"
    """
    black, white = count_stones(board)
    if black > white:
        return BLACK
    elif white > black:
        return WHITE
    else:
        return "draw"

def cpu_move(board, color, difficulty="easy"):
    """
    CPUの手を決める。有効な手の中からdifficultyに応じて選ぶ。
    置ける場所が無い場合はNoneを返す（＝パス）
    """
    valid_moves = get_valid_moves(board, color)

    if not valid_moves:
        return None

    if difficulty == "easy":
        return random.choice(valid_moves)
    else:
        # 未実装の難易度は easy にフォールバック
        return random.choice(valid_moves)

def to_notation(row, col):
    """
    (row, col) を "C4" のようなオセロ表記に変換する
    """
    column_letter = chr(ord('A') + col)
    row_number = row + 1
    return f"{column_letter}{row_number}"

def to_notation(row, col):
    """(row, col) を "C4" のようなオセロ表記に変換する"""
    return f"{COLUMN_LETTERS[col]}{row + 1}"