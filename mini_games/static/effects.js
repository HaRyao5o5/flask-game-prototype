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

function initSlotReels() {
    const SYMBOL_ORDER = ["🍒", "🍋", "🔔", "💎", "7️⃣"];
    const CELL_HEIGHT = 90;
    const SET_HEIGHT = SYMBOL_ORDER.length * CELL_HEIGHT;
    const CRUISE_SPEED = 600;
    const TARGET_DURATION = 2.2;

    document.querySelectorAll(".slot-cell.spinning[data-target]").forEach((cell) => {
        const strip = cell.querySelector(".reel-strip");
        if (!strip) return;

        let offset = 0;
        let lastTimestamp = null;
        let rafId = null;
        let stopped = false;

        function cruiseTick(timestamp) {
            if (stopped) return;
            if (lastTimestamp === null) lastTimestamp = timestamp;
            const dt = (timestamp - lastTimestamp) / 1000;
            lastTimestamp = timestamp;

            offset = (offset + CRUISE_SPEED * dt) % SET_HEIGHT;
            strip.style.transform = `translateY(-${offset}px)`;
            rafId = requestAnimationFrame(cruiseTick);
        }
        rafId = requestAnimationFrame(cruiseTick);

        const column = cell.closest(".slot-column");
        const stopBtn = column ? column.querySelector(".stop-btn") : null;
        if (!stopBtn) return;

        stopBtn.addEventListener("click", (e) => {
            e.preventDefault();
            if (stopped) return;
            stopped = true;
            cancelAnimationFrame(rafId);

            const targetSymbol = cell.dataset.target;
            const targetIndex = SYMBOL_ORDER.indexOf(targetSymbol);

            // 「その絵柄がちょうど表示窓に収まる」オフセット値そのもの（ズレ補正なし、ここが正解位置）
            const targetOffsetBase = targetIndex * CELL_HEIGHT;
            const deltaToTarget = ((targetOffsetBase - offset) % SET_HEIGHT + SET_HEIGHT) % SET_HEIGHT;

            const desiredDistance = CRUISE_SPEED * TARGET_DURATION / 2;
            const extraLoops = Math.max(0, Math.round((desiredDistance - deltaToTarget) / SET_HEIGHT));
            const totalDistance = deltaToTarget + SET_HEIGHT * extraLoops;

            const duration = 2 * totalDistance / CRUISE_SPEED;
            const deceleration = CRUISE_SPEED / duration;

            const startOffset = offset;
            const decelStart = performance.now();
            const finalOffset = startOffset + totalDistance;

            function decelTick(timestamp) {
                const elapsed = (timestamp - decelStart) / 1000;

                if (elapsed >= duration) {
                    // 最後は必ずキリのいい位置(セルの境界)にぴったり合わせて固定する
                    const snappedOffset = Math.round(finalOffset / CELL_HEIGHT) * CELL_HEIGHT;
                    strip.style.transform = `translateY(-${snappedOffset}px)`;
                    playTone(400, 0.1, "sine", 0.1);
                    cell.dataset.settled = "true"; // ← ②で使う目印

                    setTimeout(() => {
                        window.location.href = stopBtn.getAttribute("href");
                    }, 300);
                    return;
                }

                const distanceSoFar = CRUISE_SPEED * elapsed - 0.5 * deceleration * elapsed * elapsed;
                strip.style.transform = `translateY(-${startOffset + distanceSoFar}px)`;
                requestAnimationFrame(decelTick);
            }
            requestAnimationFrame(decelTick);
        });
    });
}

document.addEventListener("DOMContentLoaded", initSlotReels);

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".cell-btn, .guess-btn, .difficulty-btn, button.card, .stop-btn, .hold-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            playClickSound();
        });
    });

    if (document.querySelector(".cup.shaking")) {
        let count = 0;
        const rattle = setInterval(() => {
            playTone(300 + Math.random() * 200, 0.05, "square", 0.04);
            count++;
            if (count > 6) clearInterval(rattle);
        }, 300);
    }

    if (document.querySelector(".wheel.spinning")) {
    let count = 0;
    const spin = setInterval(() => {
        playTone(200 + Math.random() * 100, 0.04, "triangle", 0.05);
        count++;
        if (count > 10) clearInterval(spin);
    }, 200);
}

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