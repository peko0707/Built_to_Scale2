const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// ゲーム状態
let gameState = {
    playing: false,
    missCount: 0,
    bestMiss: null,
    nextNoteIndex: 0,
    blocks: [],
    evaluationText: null,
    evaluationTime: null,
    musicStartTime: null,
    audioContext: null,
    audioElement: null,
    resultShown: false
};

// ブロッククラス
class Block {
    constructor(note) {
        this.note = note;
        this.startTime = note.start;
        this.endTime = note.end;
        this.leftX = GAME_CONFIG.LEFT_START;
        this.rightX = GAME_CONFIG.RIGHT_START;
        this.angle = 0;
        this.deleteHeight = 0;
        this.depth = 0;
        this.deleted = false;
        this.deleteType = null;  // 'perfect', 'miss', 'timeout'
        
        // 移動速度を計算
        const travelTime = this.endTime - this.startTime;
        const distance = GAME_CONFIG.CENTER_X - GAME_CONFIG.LEFT_START;
        this.speed = distance / travelTime;
    }

    update(currentTime) {
        if (this.deleted) return;

        const elapsed = currentTime - this.startTime;

        if (!this.deleteType) {
            // 移動中
            this.leftX = GAME_CONFIG.LEFT_START + this.speed * elapsed;
            this.rightX = GAME_CONFIG.RIGHT_START - this.speed * elapsed;
            this.angle = this.speed * elapsed * 0.5;

            // タイムアウト判定
            if (currentTime >= this.endTime + 1) {
                this.deleteType = 'timeout';
                gameState.missCount++;
            }
        } else if (this.deleteType === 'perfect' || this.deleteType === 'miss') {
            // 消滅アニメーション
            this.depth += 5;
            if (this.depth >= 80) {
                this.deleted = true;
            }
        } else if (this.deleteType === 'timeout') {
            // 下へ消滅
            this.deleteHeight += 5;
            this.angle = 0;
            if (this.deleteHeight >= GAME_CONFIG.BLOCK_SIZE) {
                this.deleted = true;
            }
        }
    }

    draw() {
        if (this.deleted) return;

        if (this.deleteType === 'perfect' || this.deleteType === 'miss') {
            // 奥行きアニメーション
            const scale = 1 - this.depth / 100;
            drawBlockPair(
                this.leftX, this.rightX,
                this.angle,
                GAME_CONFIG.BLOCK_SIZE * scale,
                this.deleteType === 'perfect' ? '#FF6464' : '#FFFFFF'
            );
        } else if (this.deleteType === 'timeout') {
            // 高さを削る
            const h = GAME_CONFIG.BLOCK_SIZE - this.deleteHeight;
            if (h > 0) {
                drawBlockPair(this.leftX, this.rightX, this.angle, h, '#FF6464', this.deleteHeight);
            }
        } else {
            // 通常描画
            drawBlockPair(this.leftX, this.rightX, this.angle, GAME_CONFIG.BLOCK_SIZE, '#FF6464');
        }
    }

    judge(currentTime) {
        if (this.deleted || this.deleteType) return null;

        const timeDiff = Math.abs(this.endTime - currentTime);

        if (timeDiff <= GAME_CONFIG.PERFECT_WINDOW) {
            this.deleteType = 'perfect';
            this.leftX = GAME_CONFIG.CENTER_X - 20;
            this.rightX = GAME_CONFIG.CENTER_X + 20;
            this.angle = 0;
            return 'Perfect!';
        }

        return null;
    }
}

// ブロック描画
function drawBlockPair(leftX, rightX, angle, size, color, heightOffset = 0) {
    // 左側ブロック
    ctx.save();
    ctx.translate(leftX + size / 2, GAME_CONFIG.CENTER_Y);
    ctx.rotate((-angle * Math.PI) / 180);
    ctx.fillStyle = color;
    ctx.fillRect(-size / 2, heightOffset - size / 2, size, size);
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 3;
    ctx.strokeRect(-size / 2, heightOffset - size / 2, size, size);
    ctx.restore();

    // 右側ブロック
    ctx.save();
    ctx.translate(rightX - size / 2, GAME_CONFIG.CENTER_Y);
    ctx.rotate((angle * Math.PI) / 180);
    ctx.fillStyle = color;
    ctx.fillRect(-size / 2, heightOffset - size / 2, size, size);
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 3;
    ctx.strokeRect(-size / 2, heightOffset - size / 2, size, size);
    ctx.restore();
}

// ゲーム初期化
async function initGame() {
    // 最高記録を読み込み
    try {
        const response = await fetch("/api/records/built_to_scale2");
        const data = await response.json();
        if (data.success && data.record.best_miss !== null) {
            gameState.bestMiss = data.record.best_miss;
            document.getElementById("bestRecord").textContent = gameState.bestMiss;
        }
    } catch (error) {
        console.error("Error loading best record:", error);
    }

    // 音声セットアップ
    try {
        gameState.audioElement = new Audio(MUSIC_URL);
        gameState.audioElement.addEventListener("ended", onMusicEnd);
    } catch (error) {
        console.error("Error loading audio:", error);
    }

    gameState.playing = true;
    if (gameState.audioElement) {
        gameState.audioElement.play().catch(e => console.error("Play error:", e));
        gameState.musicStartTime = performance.now() / 1000;
    }

    gameLoop();
}

// ゲームループ
function gameLoop() {
    ctx.fillStyle = '#f0f0f0';
    ctx.fillRect(0, 0, GAME_CONFIG.WIDTH, GAME_CONFIG.HEIGHT);

    if (!gameState.playing) return;

    const currentTime = (performance.now() / 1000) - gameState.musicStartTime;

    // 新しいノートを生成
    if (gameState.nextNoteIndex < NOTES.length) {
        const note = NOTES[gameState.nextNoteIndex];
        if (currentTime >= note.start) {
            gameState.blocks.push(new Block(note));
            gameState.nextNoteIndex++;
        }
    }

    // ブロック更新と描画
    for (let block of gameState.blocks) {
        block.update(currentTime);
        block.draw();
    }

    // ブロック削除
    gameState.blocks = gameState.blocks.filter(b => !b.deleted);

    // UI更新
    document.getElementById("missCount").textContent = gameState.missCount;

    // 評価テキスト表示
    if (gameState.evaluationText) {
        const elapsed = performance.now() / 1000 - gameState.evaluationTime;
        if (elapsed < 1.0) {
            const evalDiv = document.getElementById("evaluationText");
            evalDiv.textContent = gameState.evaluationText;
            evalDiv.classList.add("show");
        } else {
            document.getElementById("evaluationText").classList.remove("show");
            gameState.evaluationText = null;
        }
    }

    // ゲーム終了判定
    if (gameState.nextNoteIndex >= NOTES.length && gameState.blocks.length === 0) {
        showResult();
        return;
    }

    if (gameState.playing) {
        requestAnimationFrame(gameLoop);
    }
}

// 結果表示
async function showResult() {
    if (gameState.resultShown) return;
    gameState.resultShown = true;
    gameState.playing = false;

    if (gameState.audioElement) {
        gameState.audioElement.pause();
    }

    // スコア保存
    try {
        const response = await fetch("/api/records/built_to_scale2/save", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ miss_count: gameState.missCount })
        });

        const data = await response.json();
        if (data.success) {
            gameState.bestMiss = data.best_miss;
        }
    } catch (error) {
        console.error("Error saving record:", error);
    }

    // 結果画面表示
    const resultScreen = document.getElementById("resultScreen");
    const resultTitle = document.getElementById("resultTitle");
    const finalMissCount = document.getElementById("finalMissCount");

    finalMissCount.textContent = gameState.missCount;

    if (gameState.missCount >= 15) {
        resultTitle.textContent = "Redo...";
        resultTitle.style.color = "#ff6b6b";
    } else if (gameState.missCount >= 4) {
        resultTitle.textContent = "Good!";
        resultTitle.style.color = "#FFD700";
    } else {
        resultTitle.textContent = "High Level!";
        resultTitle.style.color = "#4CAF50";
    }

    resultScreen.style.display = "flex";
}

// 音楽終了
function onMusicEnd() {
    if (gameState.playing) {
        setTimeout(showResult, 3000);
    }
}

// キーボード入力
document.addEventListener("keydown", (e) => {
    if (!gameState.playing) return;

    const currentTime = (performance.now() / 1000) - gameState.musicStartTime;

    // 最も近いブロックを検索
    let nearest = null;
    let minDiff = Infinity;

    for (let block of gameState.blocks) {
        if (block.deleted || block.deleteType) continue;

        const diff = Math.abs(currentTime - block.endTime);
        if (diff < minDiff && diff <= GAME_CONFIG.JUDGEMENT_WINDOW) {
            minDiff = diff;
            nearest = block;
        }
    }

    if (nearest) {
        const result = nearest.judge(currentTime);
        if (result) {
            gameState.evaluationText = result;
            gameState.evaluationTime = performance.now() / 1000;
        }
    }
});

// ゲーム開始
window.addEventListener("load", initGame);
