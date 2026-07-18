const HAND_EMOJI = {
    rock: '✊',
    scissors: '✌️',
    paper: '✋'
};

function drawHand(canvasId, hand) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');
    const emoji = HAND_EMOJI[hand] || '❓';

    let scale = 0;
    const targetScale = 1;
    const speed = 0.08;

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        ctx.save();
        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.scale(scale, scale);
        ctx.font = '80px serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(emoji, 0, 0);
        ctx.restore();

        if (scale < targetScale) {
            scale += speed;
            requestAnimationFrame(animate);
        }
    }

    animate();
}