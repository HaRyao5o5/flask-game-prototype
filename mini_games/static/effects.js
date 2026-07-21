// 効果音生成（Web Audio APIで音を合成するので、音声ファイル不要）

let audioCtx = null;

function getAudioCtx() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    return audioCtx;
}

function playTone(frequency, duration, type = "sine", volume = 0.15, delay = 0) {
    const ctx = getAudioCtx();
    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();

    oscillator.type = type;
    oscillator.frequency.value = frequency;
    gainNode.gain.value = volume;

    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);

    const startTime = ctx.currentTime + delay;
    oscillator.start(startTime);
    gainNode.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
    oscillator.stop(startTime + duration);
}

function playClickSound() {
    playTone(600, 0.08, "sine", 0.1);
}

function playWinSound() {
    // 上昇アルペジオ
    playTone(523, 0.15, "sine", 0.15, 0);
    playTone(659, 0.15, "sine", 0.15, 0.12);
    playTone(784, 0.25, "sine", 0.15, 0.24);
}

function playLoseSound() {
    playTone(392, 0.2, "sawtooth", 0.1, 0);
    playTone(294, 0.35, "sawtooth", 0.1, 0.15);
}

function playDrawSound() {
    playTone(440, 0.3, "triangle", 0.1);
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".cell-btn, .guess-btn, .difficulty-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            playClickSound();
        });
    });

    // オセロ：CPUが直前に置いた石があれば、軽い音を鳴らす
    if (document.querySelector(".stone.last-move")) {
        playTone(500, 0.1, "sine", 0.08);
    }

    const result = document.body.dataset.result;
    if (result === "win") {
        playWinSound();
    } else if (result === "lose") {
        playLoseSound();
    } else if (result === "draw") {
        playDrawSound();
    }
});