import os
from flask import Flask, render_template, request, session, redirect, url_for
from game_logic import judge, cpu_choice

app = Flask(__name__)
app.secret_key = os.urandom(24)  # プロトタイプ用。再起動するとスコアはリセットされる

EMPTY_SCORE = {'win': 0, 'lose': 0, 'draw': 0}

@app.route('/')
def index():
    session.setdefault('score', dict(EMPTY_SCORE))
    return render_template('index.html', score=session['score'])

@app.route('/play', methods=['POST'])
def play():
    player_hand = request.form['hand']
    cpu_hand = cpu_choice()
    result = judge(player_hand, cpu_hand)

    score = session.get('score', dict(EMPTY_SCORE))
    score[result] += 1
    session['score'] = score

    return render_template(
        'index.html',
        result=result,
        player_hand=player_hand,
        cpu_hand=cpu_hand,
        score=score
    )

@app.route('/reset')
def reset():
    session['score'] = dict(EMPTY_SCORE)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)