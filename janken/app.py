from flask import Flask, render_template, request
from game_logic import judge, cpu_choice

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play', methods=['POST'])
def play():
    player_hand = request.form['hand']
    cpu_hand = cpu_choice()
    result = judge(player_hand, cpu_hand)
    return render_template(
        'index.html',
        result=result,
        player_hand=player_hand,
        cpu_hand=cpu_hand
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)