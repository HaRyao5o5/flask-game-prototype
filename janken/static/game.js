const HAND_EMOJI = {
    rock: '✊',
    scissors: '✌️',
    paper: '✋'
};

const RESULT_COLORS = {
    win: '#4ade80',
    lose: '#f87171',
    draw: '#fbbf24'
};

// 手を左右から滑り込ませて表示する
function drawHand(canvasId, hand, direction, onDone) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');
    const emoji = HAND_EMOJI[hand] || '❓';
    const startOffset = direction === 'left' ? -80 : 80;
    const duration = 20; // フレーム数
    let frame = 0;

    function animate() {
        frame++;
        const t = Math.min(frame / duration, 1);
        const eased = 1 - Math.pow(1 - t, 3); // イーズアウト
        const offsetX = startOffset * (1 - eased);
        const scale = 0.5 + 0.5 * eased;

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        ctx.translate(canvas.width / 2 + offsetX, canvas.height / 2);
        ctx.scale(scale, scale);
        ctx.font = '80px serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(emoji, 0, 0);
        ctx.restore();

        if (t < 1) {
            requestAnimationFrame(animate);
        } else if (onDone) {
            onDone();
        }
    }
    animate();
}

// 中央にパーティクルを弾けさせる
function burstParticles(canvasId, colorHex) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const count = 26;
    const particles = [];

    for (let i = 0; i < count; i++) {
        const angle = (Math.PI * 2 * i) / count;
        const speed = 2 + Math.random() * 3;
        particles.push({
            x: cx,
            y: cy,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            life: 40 + Math.random() * 10
        });
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        let alive = false;

        particles.forEach(p => {
            if (p.life <= 0) return;
            alive = true;
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.05; // 重力
            p.life--;

            ctx.globalAlpha = Math.max(p.life / 50, 0);
            ctx.fillStyle = colorHex;
            ctx.beginPath();
            ctx.arc(p.x, p.y, 3, 0, Math.PI * 2);
            ctx.fill();
        });

        ctx.globalAlpha = 1;
        if (alive) requestAnimationFrame(animate);
    }
    animate();
}

// プレイヤー・CPU両方の手のアニメーションが終わったらパーティクルを発生させる
function playBattleAnimation(playerHand, cpuHand, result) {
    let doneCount = 0;

    function checkBothDone() {
        doneCount++;
        if (doneCount === 2) {
            burstParticles('effectCanvas', RESULT_COLORS[result] || '#ffffff');
        }
    }

    drawHand('playerCanvas', playerHand, 'left', checkBothDone);
    drawHand('cpuCanvas', cpuHand, 'right', checkBothDone);
}