from flask import Flask, render_template, request, session, redirect, url_for
import tictactoe_logic as tt
import numeron_logic as nm
import othello_logic as ot

app = Flask(__name__)
app.secret_key = "dev"  # sessionを使うのに必要（本番では推測されにくい値にする）

@app.route('/')
def index():
    return render_template('index.html')

# ==================================================
# ○×ゲーム
# ==================================================

@app.route('/tictactoe/')
def tictactoe():
    if 'tt_board' not in session:
        session['tt_board'] = tt.create_board()
        session['tt_winner'] = None

    return render_template(
        'tictactoe.html',
        board=session['tt_board'],
        winner=session['tt_winner']
    )

@app.route('/tictactoe/move', methods=['POST'])
def tictactoe_move():
    board = session['tt_board']

    if session['tt_winner'] is not None:
        return redirect(url_for('tictactoe'))

    row = int(request.form['row'])
    col = int(request.form['col'])

    if tt.is_valid_move(board, row, col):
        tt.place_mark(board, row, col, "X")

        winner = tt.check_winner(board)

        if winner is None:
            cpu_row, cpu_col = tt.cpu_move(board, difficulty="normal")
            tt.place_mark(board, cpu_row, cpu_col, "O")
            winner = tt.check_winner(board)

        session['tt_winner'] = winner
        session['tt_board'] = board
        session.modified = True

    return redirect(url_for('tictactoe'))

@app.route('/tictactoe/reset')
def tictactoe_reset():
    session['tt_board'] = tt.create_board()
    session['tt_winner'] = None
    return redirect(url_for('tictactoe'))

# ==================================================
# 数字当てゲーム
# ==================================================

@app.route('/numeron/')
def numeron():
    if 'nm_player_secret' not in session:
        session['nm_player_secret'] = nm.generate_secret_number()
        session['nm_cpu_secret'] = nm.generate_secret_number()
        session['nm_history'] = []
        session['nm_winner'] = None
        session['nm_error'] = None

    return render_template(
        'numeron.html',
        history=session['nm_history'],
        winner=session['nm_winner'],
        error=session.get('nm_error')
    )

@app.route('/numeron/guess', methods=['POST'])
def numeron_guess():
    if session['nm_winner'] is not None:
        return redirect(url_for('numeron'))

    player_guess = request.form.get('guess', '')

    if not nm.is_valid_guess(player_guess):
        session['nm_error'] = "3桁の、すべて異なる数字を入力してね（例: 123）"
        return redirect(url_for('numeron'))

    session['nm_error'] = None

    player_eat, player_bite = nm.judge(session['nm_cpu_secret'], player_guess)
    cpu_guessed = nm.cpu_guess(difficulty="normal", history=session['nm_history'])
    cpu_eat, cpu_bite = nm.judge(session['nm_player_secret'], cpu_guessed)

    history = session['nm_history']
    history.append({
        'player_guess': player_guess,
        'player_eat': player_eat,
        'player_bite': player_bite,
        'cpu_guess': cpu_guessed,
        'cpu_eat': cpu_eat,
        'cpu_bite': cpu_bite,
    })
    session['nm_history'] = history[-10:]
    session.modified = True

    if player_eat == 3 and cpu_eat == 3:
        session['nm_winner'] = 'draw'
    elif player_eat == 3:
        session['nm_winner'] = 'player'
    elif cpu_eat == 3:
        session['nm_winner'] = 'cpu'

    return redirect(url_for('numeron'))

@app.route('/numeron/reset')
def numeron_reset():
    session['nm_player_secret'] = nm.generate_secret_number()
    session['nm_cpu_secret'] = nm.generate_secret_number()
    session['nm_history'] = []
    session['nm_winner'] = None
    session['nm_error'] = None
    return redirect(url_for('numeron'))

# ==================================================
# オセロ
# ==================================================

def othello_advance_step():
    board = session['othello_board']

    if ot.is_game_over(board):
        session['othello_winner'] = ot.judge_winner(board)
        return

    current_color = session['othello_turn']
    valid_moves = ot.get_valid_moves(board, current_color)
    messages = session.get('othello_messages', [])

    if not valid_moves:
        name = "あなた" if current_color == ot.BLACK else "CPU"
        messages.append(f"{name}は置ける場所がないためパスしました")
        session['othello_turn'] = ot.WHITE if current_color == ot.BLACK else ot.BLACK
        session['othello_messages'] = messages[-5:]
        session.modified = True
        return

    if current_color == ot.WHITE:
        row, col = ot.cpu_move(board, ot.WHITE, difficulty="normal")
        ot.place_and_flip(board, row, col, ot.WHITE)
        messages.append(f"CPUは {ot.to_notation(row, col)} に置きました")
        session['othello_board'] = board
        session['othello_turn'] = ot.BLACK
        session['othello_last_cpu_move'] = (row, col)
        session['othello_messages'] = messages[-5:]
        session.modified = True
        return

@app.route('/othello/')
def othello():
    if 'othello_board' not in session:
        session['othello_board'] = ot.create_board()
        session['othello_turn'] = ot.BLACK
        session['othello_winner'] = None
        session['othello_messages'] = []
        session['othello_last_cpu_move'] = None

    board = session['othello_board']
    black, white = ot.count_stones(board)

    current_turn = session['othello_turn']
    current_valid_moves = ot.get_valid_moves(board, current_turn) if session['othello_winner'] is None else []
    is_players_turn = (
        session['othello_winner'] is None
        and current_turn == ot.BLACK
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

    if (row, col) in ot.get_valid_moves(board, ot.BLACK):
        ot.place_and_flip(board, row, col, ot.BLACK)
        session['othello_board'] = board
        session['othello_turn'] = ot.WHITE
        session.modified = True

    return redirect(url_for('othello'))

@app.route('/othello/reset')
def othello_reset():
    session['othello_board'] = ot.create_board()
    session['othello_turn'] = ot.BLACK
    session['othello_winner'] = None
    session['othello_messages'] = []
    session['othello_last_cpu_move'] = None
    return redirect(url_for('othello'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)