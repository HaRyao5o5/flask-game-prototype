from flask import Flask, render_template, request, session, redirect, url_for
import tictactoe_logic as tt
import numeron_logic as nm
import othello_logic as ot
import concentration_logic as cc
import blackjack_logic as bj
import casino_logic as cas
import slot_logic as sl

app = Flask(__name__)
app.secret_key = "dev"  # sessionを使うのに必要（本番では推測されにくい値にする）

@app.route('/')
def index():
    return render_template('index.html', chips=get_chips())

# ==================================================
# ○×ゲーム
# ==================================================

@app.route('/tictactoe/difficulty/')
def tictactoe_difficulty():
    return render_template('tictactoe_difficulty.html')

@app.route('/tictactoe/start', methods=['POST'])
def tictactoe_start():
    difficulty = request.form.get('difficulty', 'normal')
    session['tt_difficulty'] = difficulty
    session['tt_board'] = tt.create_board()
    session['tt_winner'] = None
    return redirect(url_for('tictactoe'))

@app.route('/tictactoe/')
def tictactoe():
    if 'tt_difficulty' not in session:
        return redirect(url_for('tictactoe_difficulty'))

    if 'tt_board' not in session:
        session['tt_board'] = tt.create_board()
        session['tt_winner'] = None

    return render_template(
        'tictactoe.html',
        board=session['tt_board'],
        winner=session['tt_winner'],
        difficulty=session['tt_difficulty'],
        reward=session.pop('tt_reward', None),
        chips=get_chips()
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
            cpu_row, cpu_col = tt.cpu_move(board, difficulty=session['tt_difficulty'])
            tt.place_mark(board, cpu_row, cpu_col, "O")
            winner = tt.check_winner(board)

        session['tt_winner'] = winner
        session['tt_board'] = board
        session.modified = True

        if winner == "X":
            chips = get_chips()
            new_chips, reward = cas.add_game_reward(chips, session['tt_difficulty'])
            save_chips(new_chips)
            session['tt_reward'] = reward

    return redirect(url_for('tictactoe'))

@app.route('/tictactoe/reset')
def tictactoe_reset():
    session['tt_board'] = tt.create_board()
    session['tt_winner'] = None
    return redirect(url_for('tictactoe'))

# ==================================================
# 数字当てゲーム
# ==================================================

@app.route('/numeron/difficulty/')
def numeron_difficulty():
    return render_template('numeron_difficulty.html')

@app.route('/numeron/start', methods=['POST'])
def numeron_start():
    difficulty = request.form.get('difficulty', 'normal')
    session['nm_difficulty'] = difficulty
    session['nm_player_secret'] = nm.generate_secret_number()
    session['nm_cpu_secret'] = nm.generate_secret_number()
    session['nm_history'] = []
    session['nm_winner'] = None
    session['nm_error'] = None
    return redirect(url_for('numeron'))

@app.route('/numeron/')
def numeron():
    if 'nm_difficulty' not in session:
        return redirect(url_for('numeron_difficulty'))

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
        error=session.get('nm_error'),
        difficulty=session['nm_difficulty'],
        reward=session.pop('nm_reward', None),
        chips=get_chips()
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
    cpu_guessed = nm.cpu_guess(difficulty=session['nm_difficulty'], history=session['nm_history'])
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
    
    if session['nm_winner'] == 'player':
        chips = get_chips()
        new_chips, reward = cas.add_game_reward(chips, session['nm_difficulty'])
        save_chips(new_chips)
        session['nm_reward'] = reward

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
    board = session['ot_board']

    if ot.is_game_over(board):
        session['ot_winner'] = ot.judge_winner(board)

        if session['ot_winner'] == ot.BLACK:
            chips = get_chips()
            new_chips, reward = cas.add_game_reward(chips, session['ot_difficulty'])
            save_chips(new_chips)
            session['ot_reward'] = reward

        return

    current_color = session['ot_turn']
    valid_moves = ot.get_valid_moves(board, current_color)
    messages = session.get('ot_messages', [])

    if not valid_moves:
        name = "あなた" if current_color == ot.BLACK else "CPU"
        messages.append(f"{name}は置ける場所がないためパスしました")
        session['ot_turn'] = ot.WHITE if current_color == ot.BLACK else ot.BLACK
        session['ot_messages'] = messages[-5:]
        session.modified = True
        return

    if current_color == ot.WHITE:
        row, col = ot.cpu_move(board, ot.WHITE, difficulty=session.get('ot_difficulty', 'normal'))
        ot.place_and_flip(board, row, col, ot.WHITE)
        messages.append(f"CPUは {ot.to_notation(row, col)} に置きました")
        session['ot_board'] = board
        session['ot_turn'] = ot.BLACK
        session['ot_last_cpu_move'] = (row, col)
        session['ot_messages'] = messages[-5:]
        session.modified = True
        return

@app.route('/othello/difficulty/')
def othello_difficulty():
    return render_template('othello_difficulty.html')

@app.route('/othello/start', methods=['POST'])
def othello_start():
    difficulty = request.form.get('difficulty', 'normal')
    session['ot_difficulty'] = difficulty
    session['ot_board'] = ot.create_board()
    session['ot_turn'] = ot.BLACK
    session['ot_winner'] = None
    session['ot_messages'] = []
    session['ot_last_cpu_move'] = None
    return redirect(url_for('othello'))

@app.route('/othello/')
def othello():
    if 'ot_difficulty' not in session:
        return redirect(url_for('othello_difficulty'))

    if 'ot_board' not in session:
        session['ot_board'] = ot.create_board()
        session['ot_turn'] = ot.BLACK
        session['ot_winner'] = None
        session['ot_messages'] = []
        session['ot_last_cpu_move'] = None

    board = session['ot_board']
    black, white = ot.count_stones(board)

    current_turn = session['ot_turn']
    current_valid_moves = ot.get_valid_moves(board, current_turn) if session['ot_winner'] is None else []
    is_players_turn = (
        session['ot_winner'] is None
        and current_turn == ot.BLACK
        and len(current_valid_moves) > 0
    )
    waiting = session['ot_winner'] is None and not is_players_turn
    valid_moves = current_valid_moves if is_players_turn else []

    raw_last_move = session.get('ot_last_cpu_move')
    last_cpu_move = tuple(raw_last_move) if raw_last_move else None

    return render_template(
        'othello.html',
        board=board,
        valid_moves=valid_moves,
        black_count=black,
        white_count=white,
        winner=session['ot_winner'],
        messages=session.get('ot_messages', []),
        last_cpu_move=last_cpu_move,
        waiting=waiting,
        columns=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
        difficulty=session['ot_difficulty'],
        reward=session.pop('ot_reward', None),
        chips=get_chips()
    )

@app.route('/othello/step')
def othello_step():
    if session.get('ot_winner') is None:
        othello_advance_step()
    return redirect(url_for('othello'))

@app.route('/othello/move', methods=['POST'])
def othello_move():
    if session['ot_winner'] is not None:
        return redirect(url_for('othello'))

    row = int(request.form['row'])
    col = int(request.form['col'])
    board = session['ot_board']

    if (row, col) in ot.get_valid_moves(board, ot.BLACK):
        ot.place_and_flip(board, row, col, ot.BLACK)
        session['ot_board'] = board
        session['ot_turn'] = ot.WHITE
        session.modified = True

    return redirect(url_for('othello'))

@app.route('/othello/reset')
def othello_reset():
    session['ot_board'] = ot.create_board()
    session['ot_turn'] = ot.BLACK
    session['ot_winner'] = None
    session['ot_messages'] = []
    session['ot_last_cpu_move'] = None
    return redirect(url_for('othello'))

# ==================================================
# 神経衰弱
# ==================================================

@app.route('/concentration/difficulty/')
def concentration_difficulty():
    return render_template('concentration_difficulty.html')

def _cc_new_game_state(difficulty):
    session['cc_difficulty'] = difficulty
    session['cc_cards'] = cc.create_deck()
    session['cc_matched'] = [False] * 16
    session['cc_revealed_now'] = []
    session['cc_turn'] = 'player'
    session['cc_scores'] = {'player': 0, 'cpu': 0}
    session['cc_cpu_memory'] = {}
    session['cc_winner'] = None
    session['cc_mismatch_next_turn'] = None
    session['cc_cpu_first_pick'] = None

@app.route('/concentration/start', methods=['POST'])
def concentration_start():
    difficulty = request.form.get('difficulty', 'normal')
    _cc_new_game_state(difficulty)
    return redirect(url_for('concentration'))

def _cc_check_game_over():
    if cc.is_all_matched(session['cc_matched']):
        scores = session['cc_scores']
        if scores['player'] > scores['cpu']:
            session['cc_winner'] = 'player'
        elif scores['cpu'] > scores['player']:
            session['cc_winner'] = 'cpu'
        else:
            session['cc_winner'] = 'draw'

        if session['cc_winner'] == 'player':
            chips = get_chips()
            new_chips, reward = cas.add_game_reward(chips, session['cc_difficulty'])
            save_chips(new_chips)
            session['cc_reward'] = reward

@app.route('/concentration/')
def concentration():
    if 'cc_difficulty' not in session:
        return redirect(url_for('concentration_difficulty'))

    if 'cc_cards' not in session:
        _cc_new_game_state(session['cc_difficulty'])

    cards = session['cc_cards']
    matched = session['cc_matched']
    revealed_now = session['cc_revealed_now']
    turn = session['cc_turn']
    winner = session['cc_winner']

    can_pick = (winner is None) and (turn == 'player') and (len(revealed_now) < 2)
    waiting = (winner is None) and (len(revealed_now) == 2 or turn == 'cpu')
    next_step_url = url_for('concentration_resolve') if len(revealed_now) == 2 else url_for('concentration_step')

    return render_template(
        'concentration.html',
        cards=cards,
        matched=matched,
        revealed_now=revealed_now,
        turn=turn,
        winner=winner,
        scores=session['cc_scores'],
        can_pick=can_pick,
        waiting=waiting,
        next_step_url=next_step_url,
        difficulty=session['cc_difficulty'],
        reward=session.pop('cc_reward', None),
        chips=get_chips()
    )

@app.route('/concentration/pick', methods=['POST'])
def concentration_pick():
    if session.get('cc_winner') is not None or session.get('cc_turn') != 'player':
        return redirect(url_for('concentration'))

    index = int(request.form['index'])
    matched = session['cc_matched']
    revealed_now = session['cc_revealed_now']

    if matched[index] or index in revealed_now:
        return redirect(url_for('concentration'))

    if len(revealed_now) == 0:
        revealed_now.append(index)
        session['cc_revealed_now'] = revealed_now

    elif len(revealed_now) == 1:
        idx1 = revealed_now[0]
        idx2 = index
        cards = session['cc_cards']

        if cards[idx1] == cards[idx2]:
            matched[idx1] = True
            matched[idx2] = True
            session['cc_matched'] = matched
            session['cc_scores']['player'] += 1
            session['cc_revealed_now'] = []
            session.modified = True
            _cc_check_game_over()
            # 一致したので、続けてプレイヤーの番のまま
        else:
            revealed_now.append(idx2)
            session['cc_revealed_now'] = revealed_now
            session['cc_mismatch_next_turn'] = 'cpu'

    return redirect(url_for('concentration'))

@app.route('/concentration/resolve')
def concentration_resolve():
    if session.get('cc_winner') is not None:
        return redirect(url_for('concentration'))

    session['cc_revealed_now'] = []
    next_turn = session.get('cc_mismatch_next_turn')
    if next_turn:
        session['cc_turn'] = next_turn
        session['cc_mismatch_next_turn'] = None
    session['cc_cpu_first_pick'] = None

    return redirect(url_for('concentration'))

@app.route('/concentration/step')
def concentration_step():
    if session.get('cc_winner') is not None or session.get('cc_turn') != 'cpu':
        return redirect(url_for('concentration'))

    matched = session['cc_matched']
    memory = session['cc_cpu_memory']
    cards = session['cc_cards']
    difficulty = session['cc_difficulty']

    if session.get('cc_cpu_first_pick') is None:
        idx = cc.cpu_choose_first(matched, memory, difficulty)
        memory[str(idx)] = cards[idx]
        session['cc_cpu_memory'] = memory
        session['cc_cpu_first_pick'] = idx
        session['cc_revealed_now'] = [idx]

    else:
        idx1 = session['cc_cpu_first_pick']
        idx2 = cc.cpu_choose_second(idx1, matched, memory, cards, difficulty)
        memory[str(idx2)] = cards[idx2]
        session['cc_cpu_memory'] = memory

        if cards[idx1] == cards[idx2]:
            matched[idx1] = True
            matched[idx2] = True
            session['cc_matched'] = matched
            session['cc_scores']['cpu'] += 1
            session['cc_revealed_now'] = []
            session['cc_cpu_first_pick'] = None
            session.modified = True
            _cc_check_game_over()
            # 一致したので、続けてCPUの番のまま
        else:
            session['cc_revealed_now'] = [idx1, idx2]
            session['cc_mismatch_next_turn'] = 'player'
            session['cc_cpu_first_pick'] = None

    return redirect(url_for('concentration'))

@app.route('/concentration/reset')
def concentration_reset():
    _cc_new_game_state(session.get('cc_difficulty', 'normal'))
    return redirect(url_for('concentration'))

# ==================================================
# ブラックジャック
# ==================================================

def _blackjack_settle():
    """勝敗を判定し、チップを精算する"""
    player_hand = session['bj_player']
    dealer_hand = session['bj_dealer']
    bet = session['bj_bet']
    chips = get_chips()

    result = bj.judge(player_hand, dealer_hand)

    multiplier_map = {
        'player_blackjack': 2.5,  # 3:2配当（儲けは賭け金の1.5倍）
        'player_win': 2.0,        # 賭け金がそのまま倍になって返る
        'dealer_win': 0.0,        # 賭け金を失う
        'push': 1.0,              # 賭け金がそのまま返る
    }
    new_chips = cas.apply_bet_result(chips, bet, multiplier_map[result])
    save_chips(new_chips)

    session['bj_result'] = result
    session['bj_phase'] = 'settled'
    session.modified = True

@app.route('/blackjack/')
def blackjack():
    chips = get_chips()
    phase = session.get('bj_phase', 'betting')

    context = {'chips': chips, 'phase': phase}

    if phase != 'betting':
        player_hand = session['bj_player']
        dealer_hand = session['bj_dealer']
        reveal_dealer = phase in ('dealer_turn', 'settled')

        context.update({
            'player_hand': player_hand,
            'dealer_hand': dealer_hand,
            'bet': session['bj_bet'],
            'player_total': bj.hand_value(player_hand),
            'reveal_dealer': reveal_dealer,
            'dealer_total': bj.hand_value(dealer_hand) if reveal_dealer else None,
            'result': session.get('bj_result'),
            'waiting': phase == 'dealer_turn',
        })

    return render_template('blackjack.html', **context)

@app.route('/blackjack/bet', methods=['POST'])
def blackjack_bet():
    chips = get_chips()
    amount = int(request.form.get('amount', 0))

    if not cas.can_bet(chips, amount):
        return redirect(url_for('blackjack'))

    shoe = bj.create_shoe()
    player_hand, dealer_hand, shoe = bj.deal_initial_hands(shoe)

    session['bj_shoe'] = shoe
    session['bj_player'] = player_hand
    session['bj_dealer'] = dealer_hand
    session['bj_bet'] = amount
    session.modified = True

    if bj.is_blackjack(player_hand) or bj.is_blackjack(dealer_hand):
        _blackjack_settle()
    else:
        session['bj_phase'] = 'player_turn'

    return redirect(url_for('blackjack'))

@app.route('/blackjack/hit', methods=['POST'])
def blackjack_hit():
    if session.get('bj_phase') != 'player_turn':
        return redirect(url_for('blackjack'))

    shoe = session['bj_shoe']
    player_hand = session['bj_player']
    player_hand.append(shoe.pop())
    session['bj_player'] = player_hand
    session['bj_shoe'] = shoe
    session.modified = True

    if bj.is_bust(player_hand):
        _blackjack_settle()

    return redirect(url_for('blackjack'))

@app.route('/blackjack/stand', methods=['POST'])
def blackjack_stand():
    if session.get('bj_phase') != 'player_turn':
        return redirect(url_for('blackjack'))

    session['bj_phase'] = 'dealer_turn'
    return redirect(url_for('blackjack'))

@app.route('/blackjack/dealer_step')
def blackjack_dealer_step():
    if session.get('bj_phase') != 'dealer_turn':
        return redirect(url_for('blackjack'))

    dealer_hand = session['bj_dealer']
    shoe = session['bj_shoe']

    if bj.dealer_should_hit(dealer_hand):
        dealer_hand.append(shoe.pop())
        session['bj_dealer'] = dealer_hand
        session['bj_shoe'] = shoe
        session.modified = True
    else:
        _blackjack_settle()

    return redirect(url_for('blackjack'))

@app.route('/blackjack/next')
def blackjack_next():
    session['bj_phase'] = 'betting'
    for key in ['bj_shoe', 'bj_player', 'bj_dealer', 'bj_bet', 'bj_result']:
        session.pop(key, None)
    return redirect(url_for('blackjack'))

@app.route('/blackjack/bonus')
def blackjack_bonus():
    """チップが尽きた時、追加でチップを補充する"""
    chips = get_chips()
    save_chips(cas.add_bonus_chips(chips))
    return redirect(url_for('blackjack'))

# ==================================================
# スロット
# ==================================================

@app.route('/slot/')
def slot():
    chips = get_chips()
    stopped = session.get('slot_stopped', [False, False, False])
    just_stopped = session.pop('slot_just_stopped', None)  # 一度読んだら消す(popを使う)
    return render_template(
        'slot.html',
        chips=chips,
        reels=session.get('slot_reels'),
        stopped=stopped,
        just_stopped=just_stopped,
        all_stopped=all(stopped),
        bet=session.get('slot_bet'),
        result_type=session.get('slot_result_type'),
        payout=session.get('slot_payout'),
        slot_last_bet=session.get('slot_last_bet')
    )

def _slot_start_spin(amount):
    """賭け金を受け取り、実際にスピンを開始する共通処理"""
    chips = get_chips()

    if not cas.can_bet(chips, amount):
        return False

    reels = sl.spin()
    multiplier, result_type = sl.judge(reels)

    session['slot_reels'] = reels
    session['slot_bet'] = amount
    session['slot_last_bet'] = amount
    session['slot_stopped'] = [False, False, False]  # ← 変更：カウントからリストへ
    session['slot_result_type'] = result_type
    session['slot_payout'] = None
    session['slot_pending_multiplier'] = multiplier
    session.modified = True
    return True

@app.route('/slot/spin', methods=['POST'])
def slot_spin():
    amount = int(request.form.get('amount', 0))
    _slot_start_spin(amount)
    return redirect(url_for('slot'))

@app.route('/slot/again')
def slot_again():
    amount = session.get('slot_last_bet')
    if amount:
        _slot_start_spin(amount)
    return redirect(url_for('slot'))

@app.route('/slot/stop/<int:index>')
def slot_stop(index):
    if session.get('slot_reels') is None:
        return redirect(url_for('slot'))

    stopped = session.get('slot_stopped', [False, False, False])

    if 0 <= index < 3 and not stopped[index]:
        stopped[index] = True
        session['slot_stopped'] = stopped

        if all(stopped):
            session['slot_just_stopped'] = 'all'  # ← 全部揃ったら"all"を記録
        else:
            session['slot_just_stopped'] = index

        session.modified = True

        if all(stopped):
            chips = get_chips()
            bet = session['slot_bet']
            multiplier = session['slot_pending_multiplier']
            new_chips = cas.apply_bet_result(chips, bet, multiplier)
            save_chips(new_chips)
            session['slot_payout'] = int(bet * multiplier)

    return redirect(url_for('slot'))

@app.route('/slot/next')
def slot_next():
    for key in ['slot_reels', 'slot_bet', 'slot_stopped', 'slot_result_type', 'slot_payout', 'slot_pending_multiplier']:
        session.pop(key, None)
    return redirect(url_for('slot'))

@app.route('/slot/bonus')
def slot_bonus():
    chips = get_chips()
    save_chips(cas.add_bonus_chips(chips))
    return redirect(url_for('slot'))

# ==================================================
# チップ管理の共通ヘルパー
# ==================================================

def get_chips():
    if 'chips' not in session:
        session['chips'] = cas.create_wallet()
    return session['chips']

def save_chips(amount):
    session['chips'] = amount

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)