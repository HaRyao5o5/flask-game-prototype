import os
from flask import Flask, render_template, request, session, redirect, url_for
from game_logic import judge, cpu_choice, match_winner, predict_player_hand

app = Flask(__name__)
app.secret_key = os.urandom(24)  # プロトタイプ用。再起動するとセッションはリセットされる

EMPTY_SCORE = {"win": 0, "lose": 0, "draw": 0}
EMPTY_SET_WINS = {"player": 0, "cpu": 0}
EMPTY_HAND_COUNTS = {"rock": 0, "scissors": 0, "paper": 0}
TARGET_WINS = 3
HISTORY_LIMIT = 10

HAND_LABELS = {
    "rock": "✊ グー",
    "scissors": "✌️ チョキ",
    "paper": "✋ パー",
}


def init_session():
    session.setdefault("score", dict(EMPTY_SCORE))
    session.setdefault("set_wins", dict(EMPTY_SET_WINS))
    session.setdefault("history", [])
    session.setdefault("mode", "normal")
    session.setdefault("hand_counts", dict(EMPTY_HAND_COUNTS))


def render_index(**extra):
    predicted = None
    if session["mode"] == "hard":
        predicted = predict_player_hand(session["hand_counts"])

    return render_template(
        "index.html",
        score=session["score"],
        set_wins=session["set_wins"],
        history=session["history"],
        mode=session["mode"],
        match_winner=match_winner(session["set_wins"], TARGET_WINS),
        target=TARGET_WINS,
        hand_labels=HAND_LABELS,
        predicted=predicted,
        **extra
    )


@app.route("/")
def index():
    init_session()
    return render_index()


@app.route("/mode/<level>")
def set_mode(level):
    init_session()
    if level in ("easy", "normal", "hard"):
        session["mode"] = level
        session.modified = True
    return redirect(url_for("index"))


@app.route("/play", methods=["POST"])
def play():
    init_session()

    if match_winner(session["set_wins"], TARGET_WINS):
        return redirect(url_for("index"))

    player_hand = request.form["hand"]
    cpu_hand = cpu_choice(
        mode=session["mode"],
        player_hand=player_hand,
        hand_counts=session["hand_counts"],
    )
    result = judge(player_hand, cpu_hand)

    session["score"][result] += 1
    session["hand_counts"][player_hand] += 1

    if result == "win":
        session["set_wins"]["player"] += 1
    elif result == "lose":
        session["set_wins"]["cpu"] += 1

    history = session["history"]
    history.insert(0, {
        "player_hand": player_hand,
        "cpu_hand": cpu_hand,
        "result": result,
    })
    session["history"] = history[:HISTORY_LIMIT]
    session.modified = True

    return render_index(
        result=result,
        player_hand=player_hand,
        cpu_hand=cpu_hand,
    )


@app.route("/new_match")
def new_match():
    init_session()
    session["set_wins"] = dict(EMPTY_SET_WINS)
    session.modified = True
    return redirect(url_for("index"))


@app.route("/reset")
def reset():
    session["score"] = dict(EMPTY_SCORE)
    session["set_wins"] = dict(EMPTY_SET_WINS)
    session["history"] = []
    session["hand_counts"] = dict(EMPTY_HAND_COUNTS)
    session.modified = True
    return redirect(url_for("index"))


@app.route("/rules")
def rules():
    return render_template("rules.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)