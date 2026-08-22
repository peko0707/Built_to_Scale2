const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

/* =========================================
   背景
========================================= */

const background = new Image();
background.src = "/static/images/background.png";

const RESULT_MESSAGES = Object.freeze({
    redo: "全然組み立って\nないですよ～\n(⌒∇⌒)",
    good: "まぁまぁ組み立った\nなかなかやるやんけ\n( ･´ｰ･｀)",
    highLevel: "すごすぎる！？\n普通に尊敬します。\n(ﾟдﾟ)！"
});


/* =========================================
   ゲーム設定
   Python版に合わせる
========================================= */



/* =========================================
   ゲーム状態
========================================= */

const gameState = {
    started: false,
    playing: false,

    missCount: 0,
    bestMiss: null,

    nextNoteIndex: 0,

    blocks: [],

    evaluationText: null,
    evaluationTime: 0,

    resultShown: false,

    resultTimerStarted: false
};


/* =========================================
   音楽
========================================= */

let audio = null;


/*
   Audioを1個しか作らない
*/
function createAudio() {

    if (audio !== null) {
        return;
    }

    audio = new Audio(MUSIC_URL);

    audio.preload = "auto";

    audio.addEventListener("ended", () => {
        if (gameState.playing) {
            showResult();
        }
    });
}


/* =========================================
   ブロック画像
========================================= */

function createBlockImage(circleColor) {

    const c = document.createElement("canvas");

    c.width = 85;
    c.height = 85;

    const cctx = c.getContext("2d");

    // 赤い四角
    cctx.fillStyle = "#ff6464";
    cctx.fillRect(0, 0, 85, 85);

    // 黒い枠
    cctx.strokeStyle = "#000000";
    cctx.lineWidth = 5;
    cctx.strokeRect(0, 0, 85, 85);

    // 黒い円
    cctx.beginPath();
    cctx.fillStyle = "#000000";
    cctx.arc(42, 42, 17, 0, Math.PI * 2);
    cctx.fill();

    // 中の円
    cctx.beginPath();
    cctx.fillStyle = circleColor;
    cctx.arc(42, 42, 15, 0, Math.PI * 2);
    cctx.fill();

    return c;
}


const normalBlock = createBlockImage("#ffffff");
const perfectBlock = createBlockImage("#ff6464");
const missBlock = createBlockImage("#ffffff");


/* =========================================
   Block
========================================= */

class Block {

    constructor(note) {

        this.start = note.start;
        this.end = note.end;

        this.l_x = GAME_CONFIG.LEFT_START;
        this.r_x = GAME_CONFIG.RIGHT_START;

        this.angle = 0;

        this.deleting = false;

        this.depth = 0;
        this.deleteHeight = 0;

        this.deleted = false;

        /*
           Python版と同じ

           距離:
           -90 → 360
           = 450px
        */

        const travelTime = this.end - this.start;

        const distance =
            GAME_CONFIG.CENTER_X -
            GAME_CONFIG.LEFT_START;

        this.speed = distance / travelTime;
    }


    update(musicTime) {

        if (this.deleted) {
            return;
        }

        /*
           消滅中は通常移動しない
        */

        if (
            this.deleting === "back" ||
            this.deleting === "miss"
        ) {
            return;
        }

        if (this.deleting === "down") {
            return;
        }


        /*
           Python版と同じ移動
        */

        const elapsed =
            musicTime - this.start;


        this.l_x =
            GAME_CONFIG.LEFT_START +
            this.speed * elapsed;


        this.r_x =
            GAME_CONFIG.RIGHT_START -
            this.speed * elapsed;


        /*
           Python版と同じ回転

           左  = -angle
           右  = +angle
        */

        this.angle =
            this.speed * elapsed;


        /*
           Python版と同じ
           l_x >= 500 でミス
        */

        if (this.l_x >= 500) {

            this.deleting = "down";

            gameState.missCount++;

            return;
        }


        /*
           念のため終了後にも消す
        */

        if (musicTime >= this.end + 1) {

            this.deleting = "down";

            gameState.missCount++;
        }
    }
}


/* =========================================
   ブロック描画
========================================= */

function drawBlock(
    image,
    x,
    angle,
    size = 85,
    height = 85,
    heightOffset = 0
) {

    ctx.save();


    /*
       ブロックの中心座標

       Python版:
       center=(x + 42.5, 242.5)
    */

    ctx.translate(
        x + 42.5,
        GAME_CONFIG.CENTER_Y
    );


    ctx.rotate(
        angle * Math.PI / 180
    );


    ctx.drawImage(
        image,

        -size / 2,

        -height / 2 + heightOffset,

        size,
        height
    );


    ctx.restore();
}


/* =========================================
   ペア描画
========================================= */

function drawPair(block) {


    /*
       通常
    */

    if (block.deleting === false) {

        drawBlock(
            normalBlock,
            block.l_x,
            block.angle
        );

        drawBlock(
            normalBlock,
            block.r_x,
            -block.angle
        );

        return;
    }


    /*
       Perfect / Miss
    */

    if (
        block.deleting === "back" ||
        block.deleting === "miss"
    ) {

        const scale =
            Math.max(
                0,
                1 - block.depth / 100
            );

        const size =
            85 * scale;


        if (size <= 0) {
            return;
        }


        const image =
            block.deleting === "back"
                ? perfectBlock
                : missBlock;


        drawBlock(
            image,
            block.l_x,
            -block.angle,
            size,
            size
        );

        drawBlock(
            image,
            block.r_x,
            block.angle,
            size,
            size
        );

        return;
    }


    /*
       下に消える
    */

    if (block.deleting === "down") {

        const height =
            Math.max(
                0,
                85 - block.deleteHeight
            );


        if (height <= 0) {
            return;
        }


        drawBlock(
            normalBlock,
            block.l_x,
            0,
            85,
            height
        );


        drawBlock(
            normalBlock,
            block.r_x,
            0,
            85,
            height
        );
    }
}


/* =========================================
   ノーツ生成
========================================= */

function spawnNotes(musicTime) {

    /*
       1フレームで複数ノーツ来ても
       全部生成する
    */

    while (
        gameState.nextNoteIndex <
        NOTES.length
    ) {

        const note =
            NOTES[gameState.nextNoteIndex];


        if (
            musicTime <
            note.start
        ) {
            break;
        }


        gameState.blocks.push(
            new Block(note)
        );


        gameState.nextNoteIndex++;
    }
}


/* =========================================
   ブロック更新
========================================= */

function updateBlocks(musicTime) {

    for (
        const block of gameState.blocks
    ) {

        block.update(musicTime);


        /*
           Perfect / Miss
           奥に消える
        */

        if (
            block.deleting === "back" ||
            block.deleting === "miss"
        ) {

            block.depth += 5;


            if (block.depth >= 80) {
                block.deleted = true;
            }
        }


        /*
           Miss
           下に消える
        */

        else if (
            block.deleting === "down"
        ) {

            block.deleteHeight += 5;


            if (
                block.deleteHeight >= 85
            ) {
                block.deleted = true;
            }
        }
    }


    gameState.blocks =
        gameState.blocks.filter(
            block => !block.deleted
        );
}


/* =========================================
   判定
========================================= */

function judge() {

    if (
        !gameState.playing ||
        !audio
    ) {
        return;
    }


    /*
       ★重要

       音楽そのものの時間を使う
    */

    const musicTime =
        audio.currentTime;


    let target = null;

    let minDifference =
        Infinity;


    /*
       一番近いノーツを探す
    */

    for (
        const block of gameState.blocks
    ) {

        if (
            block.deleting !== false
        ) {
            continue;
        }


        const difference =
            Math.abs(
                musicTime -
                block.end
            );


        if (
            difference <=
            GAME_CONFIG.JUDGEMENT_WINDOW
        ) {

            if (
                difference <
                minDifference
            ) {

                minDifference =
                    difference;

                target = block;
            }
        }
    }


    if (!target) {
        return;
    }


    const difference =
        Math.abs(
            musicTime -
            target.end
        );


    /*
       Perfect
    */

    if (
        difference <=
        GAME_CONFIG.PERFECT_WINDOW
    ) {

        /*
           Python版と同じ

           判定時に中央へ移動
        */

        target.l_x = 360;
        target.r_x = 360;

        target.angle = 0;

        target.deleting = "back";


        showEvaluation(
            "Perfect!"
        );

        return;
    }


    /*
       Miss
    */

    target.deleting = "miss";

    gameState.missCount++;


    showEvaluation(
        "Miss!"
    );
}


/* =========================================
   評価表示
========================================= */

function showEvaluation(text) {

    gameState.evaluationText = text;

    gameState.evaluationTime =
        performance.now();


    const element =
        document.getElementById(
            "evaluationText"
        );


    element.textContent = text;

    element.classList.add("show");


    setTimeout(() => {

        element.classList.remove("show");

    }, 1000);
}


/* =========================================
   BEST記録読み込み
========================================= */

async function loadBestRecord() {

    try {

        const response =
            await fetch(
                "/api/records/built_to_scale2"
            );


        const data =
            await response.json();


        if (
            data.success &&
            data.record.best_miss !== null
        ) {

            gameState.bestMiss =
                data.record.best_miss;


            document.getElementById(
                "bestRecord"
            ).textContent =
                gameState.bestMiss;
        }

    } catch (error) {

        console.error(
            "BEST読み込みエラー:",
            error
        );
    }
}


/* =========================================
   スコア保存
========================================= */

async function saveRecord() {

    try {

        const response =
            await fetch(
                "/api/records/built_to_scale2/save",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        miss_count:
                            gameState.missCount
                    })
                }
            );


        const data =
            await response.json();


        if (data.success) {

            gameState.bestMiss =
                data.best_miss;
        }

    } catch (error) {

        console.error(
            "スコア保存エラー:",
            error
        );
    }
}


/* =========================================
   結果画面
========================================= */

async function showResult() {

    if (gameState.resultShown) {
        return;
    }

    gameState.resultShown = true;
    gameState.playing = false;

    // ゲーム音楽を停止
    if (audio) {
        audio.pause();
    }

    await saveRecord();

    const resultScreen =
        document.getElementById("resultScreen");

    const finalMissCount =
        document.getElementById("finalMissCount");

    const resultImage =
        document.getElementById("resultImage");


    // MISS数を表示
    if (finalMissCount) {
        finalMissCount.textContent =
            gameState.missCount;
    }


    // 結果画像・結果音声
    let resultImagePath;
    let resultAudioPath;
    let resultMessage;
    let resultRank;


    if (gameState.missCount >= 16) {

        // 16 MISS以上 → REDO
        resultImagePath =
            "/static/images/redo.png";

        resultAudioPath =
            "/static/audio/redo.mp3";

        resultMessage =
            RESULT_MESSAGES.redo;

        resultRank = "redo";

    }

    else if (gameState.missCount >= 4) {

        // 4～15 MISS → GOOD
        resultImagePath =
            "/static/images/good.png";

        resultAudioPath =
            "/static/audio/good.mp3";

        resultMessage =
            RESULT_MESSAGES.good;

        resultRank = "good";

    }

    else {

        // 0～3 MISS → HIGH LEVEL
        resultImagePath =
            "/static/images/high_level.png";

        resultAudioPath =
            "/static/audio/high_level.mp3";

        resultMessage =
            RESULT_MESSAGES.highLevel;

        resultRank = "high-level";
    }


    // 結果画像を表示
    if (resultImage) {
        resultImage.src = resultImagePath;
    }

    document.getElementById("resultName").textContent =
        "組み立ての評価";
    document.getElementById("resultMessage").textContent =
        resultMessage;
    resultScreen.dataset.rank = resultRank;


    // 結果音声を再生
    const resultAudio =
        new Audio(resultAudioPath);

    resultAudio.preload = "auto";

    try {
        await resultAudio.play();
    }

    catch (error) {
        console.error(
            "結果音声の再生エラー:",
            error
        );
    }


    // 結果画面を表示
    if (resultScreen) {
        resultScreen.style.display = "flex";
    }
}

/* =========================================
   ゲームループ
========================================= */

function gameLoop() {

    if (
        !gameState.playing
    ) {
        return;
    }


    /*
       背景
    */

    ctx.clearRect(
        0,
        0,
        GAME_CONFIG.WIDTH,
        GAME_CONFIG.HEIGHT
    );


    if (
        background.complete &&
        background.naturalWidth > 0
    ) {

        ctx.drawImage(
            background,
            0,
            0,
            GAME_CONFIG.WIDTH,
            GAME_CONFIG.HEIGHT
        );

    } else {

        ctx.fillStyle =
            "#ffffff";

        ctx.fillRect(
            0,
            0,
            GAME_CONFIG.WIDTH,
            GAME_CONFIG.HEIGHT
        );
    }


    /*
       音楽の現在位置
    */

    const musicTime =
        audio.currentTime;


    /*
       ノーツ生成
    */

    spawnNotes(musicTime);


    /*
       ノーツ更新
    */

    updateBlocks(musicTime);


    /*
       ノーツ描画
    */

    for (
        const block of gameState.blocks
    ) {

        drawPair(block);
    }


    /*
       MISS
    */

    document.getElementById(
        "missCount"
    ).textContent =
        gameState.missCount;


    /*
       BEST
    */

    if (
        gameState.bestMiss !== null
    ) {

        document.getElementById(
            "bestRecord"
        ).textContent =
            gameState.bestMiss;
    }


    /*
       全ノーツ終了
    */

    if (
        gameState.nextNoteIndex >=
            NOTES.length &&
        gameState.blocks.length === 0
    ) {

        if (
            !gameState.resultTimerStarted
        ) {

            gameState.resultTimerStarted =
                true;


            setTimeout(
                showResult,
                3000
            );
        }

        return;
    }


    requestAnimationFrame(
        gameLoop
    );
}


/* =========================================
   ゲーム開始
========================================= */

async function startGame() {

    /*
       二重起動防止
    */

    if (
        gameState.started
    ) {
        return;
    }


    gameState.started = true;


    createAudio();


    try {

        /*
           音楽を最初から
        */

        audio.currentTime = 0;


        /*
           クリック/キー入力から
           再生するのでブラウザに許可される
        */

        await audio.play();


        gameState.playing = true;


        gameLoop();

    } catch (error) {

        console.error(
            "音楽再生エラー:",
            error
        );


        gameState.started = false;


        alert(
            "音楽を再生できませんでした。もう一度クリックしてください。"
        );
    }
}


/* =========================================
   キーボード
========================================= */

document.addEventListener(
    "keydown",
    event => {

        /*
           キーリピート無視
        */

        if (
            event.repeat
        ) {
            return;
        }


        event.preventDefault();


        /*
           最初のキーなら開始
        */

        if (
            !gameState.started
        ) {

            startGame();

            return;
        }


        /*
           それ以降は判定
        */

        judge();
    }
);


/* =========================================
   マウス・タッチ
========================================= */

canvas.addEventListener(
    "pointerdown",
    event => {

        event.preventDefault();


        /*
           最初のクリック
        */

        if (
            !gameState.started
        ) {

            startGame();

            return;
        }


        /*
           それ以降は判定
        */

        judge();
    }
);


/* =========================================
   初期化
========================================= */

window.addEventListener(
    "load",
    () => {

        loadBestRecord();

        createAudio();


        /*
           最初の画面にも背景を表示
        */

        if (
            background.complete &&
            background.naturalWidth > 0
        ) {

            ctx.drawImage(
                background,
                0,
                0,
                800,
                600
            );

        } else {

            background.onload = () => {

                ctx.drawImage(
                    background,
                    0,
                    0,
                    800,
                    600
                );
            };
        }
    }
);
