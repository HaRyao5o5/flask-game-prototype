from flask import Flask, render_template, request, session, redirect, url_for
from tictactoe_logic import create_board, is_valid_move, place_mark, check_winner, cpu_move
from numeron_logic import generate_secret_number, judge, is_valid_guess, cpu_guess
from othello_logic import (
    create_board, get_valid_moves, place_and_flip,
    count_stones, is_game_over, judge_winner, cpu_move,
    to_notation, BLACK, WHITE
)

app = Flask(__name__)
app.secret_key = "dev"  # sessionを使うのに必要（本番では推測されにくい値にする）

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tictactoe/')
def tictactoe():
    # 新規アクセス時は盤面を初期化してsessionに保存
    if 'board' not in session:
        session['board'] = create_board()
        session['winner'] = None

    return render_template(
        'tictactoe.html',
        board=session['board'],
        winner=session['winner']
    )

@app.route('/tictactoe/move', methods=['POST'])
def tictactoe_move():
    board = session['board']

    # すでに決着していたら、それ以上操作を受け付けない
    if session['winner'] is not None:
        return redirect(url_for('tictactoe'))

    row = int(request.form['row'])
    col = int(request.form['col'])

    # プレイヤーの手を反映
    if is_valid_move(board, row, col):
        place_mark(board, row, col, "X")

        winner = check_winner(board)

        # プレイヤーの手だけで決着しなければ、続けてCPUが打つ
        if winner is None:
            cpu_row, cpu_col = cpu_move(board, difficulty="easy")
            place_mark(board, cpu_row, cpu_col, "O")
            winner = check_winner(board)

        session['winner'] = winner
        session['board'] = board
        session.modified = True  # リストの中身を書き換えた場合に必要

    return redirect(url_for('tictactoe'))

@app.route('/tictactoe/reset')
def tictactoe_reset():
    session['board'] = create_board()
    session['winner'] = None
    return redirect(url_for('tictactoe'))

@app.route('/numeron/')
def numeron():
    if 'player_secret' not in session:
        session['player_secret'] = generate_secret_number()
        session['cpu_secret'] = generate_secret_number()
        session['history'] = []
        session['winner'] = None
        session['error'] = None

    return render_template(
        'numeron.html',
        history=session['history'],
        winner=session['winner'],
        error=session.get('error')
    )

@app.route('/numeron/guess', methods=['POST'])
def numeron_guess():
    if session['winner'] is not None:
        return redirect(url_for('numeron'))

    player_guess = request.form.get('guess', '')

    if not is_valid_guess(player_guess):
        session['error'] = "3桁の、すべて異なる数字を入力してね（例: 123）"
        return redirect(url_for('numeron'))

    session['error'] = None  # ← 有効な入力が来たらエラーは消す

    # (以下は変更なし)
    player_eat, player_bite = judge(session['cpu_secret'], player_guess)
    cpu_guessed = cpu_guess(difficulty="easy")
    cpu_eat, cpu_bite = judge(session['player_secret'], cpu_guessed)

    history = session['history']
    history.append({
        'player_guess': player_guess,
        'player_eat': player_eat,
        'player_bite': player_bite,
        'cpu_guess': cpu_guessed,
        'cpu_eat': cpu_eat,
        'cpu_bite': cpu_bite,
    })
    session['history'] = history[-10:]
    session.modified = True

    if player_eat == 3 and cpu_eat == 3:
        session['winner'] = 'draw'
    elif player_eat == 3:
        session['winner'] = 'player'
    elif cpu_eat == 3:
        session['winner'] = 'cpu'

    return redirect(url_for('numeron'))

@app.route('/numeron/reset')
def numeron_reset():
    session['player_secret'] = generate_secret_number()
    session['cpu_secret'] = generate_secret_number()
    session['history'] = []
    session['winner'] = None
    session['error'] = None
    return redirect(url_for('numeron'))

def othello_advance_step():
    """
    1ステップだけ進める（パス、またはCPUの1手）。
    プレイヤーの番になったら何もせず終わる。
    """
    board = session['othello_board']

    if is_game_over(board):
        session['othello_winner'] = judge_winner(board)
        return

    current_color = session['othello_turn']
    valid_moves = get_valid_moves(board, current_color)
    messages = session.get('othello_messages', [])

    if not valid_moves:
        name = "あなた" if current_color == BLACK else "CPU"
        messages.append(f"{name}は置ける場所がないためパスしました")
        session['othello_turn'] = WHITE if current_color == BLACK else BLACK
        session['othello_messages'] = messages[-5:]
        session.modified = True
        return

    if current_color == WHITE:
        row, col = cpu_move(board, WHITE, difficulty="easy")
        place_and_flip(board, row, col, WHITE)
        messages.append(f"CPUは {to_notation(row, col)} に置きました")
        session['othello_board'] = board
        session['othello_turn'] = BLACK
        session['othello_last_cpu_move'] = (row, col)
        session['othello_messages'] = messages[-5:]
        session.modified = True
        return
    # current_color == BLACK の場合はプレイヤーの番なので何もしない

@app.route('/othello/')
def othello():
    if 'othello_board' not in session:
        session['othello_board'] = create_board()
        session['othello_turn'] = BLACK
        session['othello_winner'] = None
        session['othello_messages'] = []
        session['othello_last_cpu_move'] = None

    board = session['othello_board']
    black, white = count_stones(board)

    # 「黒の番」だけでなく「黒に置ける場所があるか」まで確認する
    current_turn = session['othello_turn']
    current_valid_moves = get_valid_moves(board, current_turn) if session['othello_winner'] is None else []
    is_players_turn = (
        session['othello_winner'] is None
        and current_turn == BLACK
        and len(current_valid_moves) > 0
    )
    waiting = session['othello_winner'] is None and not is_players_turn

    valid_moves = current_valid_moves if is_players_turn else []

    raw_last_move = session.get('othello_last_cpu_move')
    last_cpu_move = tuple(raw_last_move) if raw_last_move else None

    return render_template(
        'othello.html',
        board=board,
        valid_moves=valid_moves,
        black_count=black,
        white_count=white,
        winner=session['othello_winner'],
        messages=session.get('othello_messages', []),
        last_cpu_move=last_cpu_move,
        waiting=waiting,
        columns=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    )

@app.route('/othello/step')
def othello_step():
    if session.get('othello_winner') is None:
        othello_advance_step()
    return redirect(url_for('othello'))

@app.route('/othello/move', methods=['POST'])
def othello_move():
    if session['othello_winner'] is not None:
        return redirect(url_for('othello'))

    row = int(request.form['row'])
    col = int(request.form['col'])
    board = session['othello_board']

    if (row, col) in get_valid_moves(board, BLACK):
        place_and_flip(board, row, col, BLACK)
        session['othello_board'] = board
        session['othello_turn'] = WHITE
        session.modified = True

    return redirect(url_for('othello'))

@app.route('/othello/reset')
def othello_reset():
    session['othello_board'] = create_board()
    session['othello_turn'] = BLACK
    session['othello_winner'] = None
    session['othello_messages'] = []
    session['othello_last_cpu_move'] = None
    return redirect(url_for('othello'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)