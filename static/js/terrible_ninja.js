"use strict";

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const WIDTH = 800;
const HEIGHT = 600;
const PERFECT_WINDOW = 0.1;
const JUDGEMENT_WINDOW = 0.2;
const AUTO_MISS_DELAY = 0.21;
const MESSAGE_SECONDS = 1;
const ENEMY_ARROW_SECONDS = 0.45;

const ASSETS = {
    background1: "/static/images/terrible_ninja_background1.png",
    background2: "/static/images/terrible_ninja_background2.png",
    music: "/static/audio/terrible_ninja.mp3",
    timing: "/static/data/terrible_ninja.json",
    results: {
        high: {
            image: "/static/images/high_level.png",
            audio: "/static/audio/high_level.mp3"
        },
        good: {
            image: "/static/images/good.png",
            audio: "/static/audio/good.mp3"
        },
        redo: {
            image: "/static/images/background.png",
            audio: "/static/audio/redo.mp3"
        }
    }
};

const state = {
    ready: false,
    started: false,
    playing: false,
    resultShown: false,
    missCount: 0,
    handLeft: true,
    backgroundTwo: true,
    changeIndex: 0,
    enemyIndex: 0,
    notes: [],
    enemyTimes: [],
    changeTimes: [],
    enemyArrows: [],
    splitAnimations: [],
    missAnimations: [],
    staticMissArrows: [],
    messageUntil: 0,
    bestMiss: null
};

const images = {};
let music = null;
let resultAudio = null;

function loadImage(url) {
    return new Promise((resolve, reject) => {
        const image = new Image();
        image.onload = () => resolve(image);
        image.onerror = () => reject(new Error(`画像を読み込めません: ${url}`));
        image.src = url;
    });
}

async function initialize() {
    try {
        const [background1, background2, timingResponse] = await Promise.all([
            loadImage(ASSETS.background1),
            loadImage(ASSETS.background2),
            fetch(ASSETS.timing)
        ]);

        if (!timingResponse.ok) {
            throw new Error(`タイミングデータの取得に失敗しました: ${timingResponse.status}`);
        }

        const timing = await timingResponse.json();
        images.background1 = background1;
        images.background2 = background2;
        state.notes = timing.justtimes.map(time => ({ time, active: true }));
        state.enemyTimes = timing.enemyJusttimes;
        state.changeTimes = timing.changeTimes;

        music = new Audio(ASSETS.music);
        music.preload = "auto";
        music.addEventListener("ended", showResult);

        state.ready = true;
        drawFrame(0);
        await loadBestRecord();
    } catch (error) {
        console.error(error);
        document.getElementById("startMessage").textContent = "ゲームの読み込みに失敗しました";
    }
}

async function startGame() {
    if (!state.ready || state.started) {
        return;
    }

    state.started = true;
    document.getElementById("startMessage").hidden = true;

    try {
        music.currentTime = 0;
        await music.play();
        state.playing = true;
        requestAnimationFrame(gameLoop);
    } catch (error) {
        console.error("音楽を再生できません", error);
        state.started = false;
        document.getElementById("startMessage").hidden = false;
        document.getElementById("startMessage").textContent = "もう一度クリックしてスタート";
    }
}

function handleAction() {
    if (!state.started) {
        startGame();
        return;
    }
    if (!state.playing) {
        return;
    }

    state.handLeft = !state.handLeft;
    judge(music.currentTime);
}

function judge(currentTime) {
    let nearest = null;
    let nearestDifference = Infinity;

    for (const note of state.notes) {
        if (!note.active) {
            continue;
        }
        const difference = Math.abs(note.time - currentTime);
        if (difference < nearestDifference) {
            nearest = note;
            nearestDifference = difference;
        }
    }

    if (!nearest || nearestDifference > JUDGEMENT_WINDOW) {
        return;
    }

    nearest.active = false;
    if (nearestDifference <= PERFECT_WINDOW) {
        showEvaluation("perfect");
        state.splitAnimations.push({ startedAt: performance.now(), x: 400, y: 300 });
        return;
    }

    state.missCount += 1;
    showEvaluation("miss");
    state.missAnimations.push({ startedAt: performance.now(), x: 400, y: 300 });
}

function showEvaluation(text) {
    const element = document.getElementById("evaluationText");
    element.textContent = text;
    element.classList.add("show");
    state.messageUntil = performance.now() + MESSAGE_SECONDS * 1000;
}

function update(currentTime, now) {
    while (
        state.changeIndex < state.changeTimes.length &&
        currentTime >= state.changeTimes[state.changeIndex]
    ) {
        state.backgroundTwo = !state.backgroundTwo;
        state.staticMissArrows.length = 0;
        state.changeIndex += 1;
    }

    while (
        state.enemyIndex < state.enemyTimes.length &&
        currentTime >= state.enemyTimes[state.enemyIndex]
    ) {
        state.enemyArrows.push({ musicStartedAt: state.enemyTimes[state.enemyIndex] });
        state.enemyIndex += 1;
    }

    for (const note of state.notes) {
        if (note.active && currentTime >= note.time + AUTO_MISS_DELAY) {
            note.active = false;
            state.missCount += 1;
            state.staticMissArrows.push({
                x: 490 + Math.random() * 20,
                y: 240 + Math.random() * 20
            });
            showEvaluation("miss");
        }
    }

    state.enemyArrows = state.enemyArrows.filter(
        arrow => currentTime - arrow.musicStartedAt < ENEMY_ARROW_SECONDS
    );
    state.splitAnimations = state.splitAnimations.filter(
        animation => now - animation.startedAt < 800
    );
    state.missAnimations = state.missAnimations.filter(
        animation => now - animation.startedAt < 1200
    );

    if (state.messageUntil && now >= state.messageUntil) {
        document.getElementById("evaluationText").classList.remove("show");
        state.messageUntil = 0;
    }

    document.getElementById("missCount").textContent = state.missCount;
}

function gameLoop(now) {
    if (!state.playing) {
        return;
    }
    const currentTime = music.currentTime;
    update(currentTime, now);
    drawFrame(currentTime, now);
    requestAnimationFrame(gameLoop);
}

function drawFrame(currentTime, now = performance.now()) {
    const background = state.backgroundTwo ? images.background2 : images.background1;
    if (background) {
        ctx.drawImage(background, 0, 0, WIDTH, HEIGHT);
    } else {
        ctx.fillStyle = "#80789f";
        ctx.fillRect(0, 0, WIDTH, HEIGHT);
    }

    if (state.backgroundTwo) {
        drawSwordAndHands(state.handLeft);
    }

    for (const arrow of state.enemyArrows) {
        drawEnemyArrow(arrow, currentTime);
    }
    for (const animation of state.splitAnimations) {
        drawSplitArrow(animation, (now - animation.startedAt) / 800);
    }
    for (const animation of state.missAnimations) {
        drawMissArrow(animation, (now - animation.startedAt) / 1200);
    }
    for (const arrow of state.staticMissArrows) {
        drawArrow(arrow.x, arrow.y, 0);
    }
}

function strokePath(points, color, width) {
    ctx.beginPath();
    ctx.moveTo(points[0][0], points[0][1]);
    for (let index = 1; index < points.length; index += 1) {
        ctx.lineTo(points[index][0], points[index][1]);
    }
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.stroke();
}

function fillPolygon(points, color) {
    ctx.beginPath();
    ctx.moveTo(points[0][0], points[0][1]);
    for (let index = 1; index < points.length; index += 1) {
        ctx.lineTo(points[index][0], points[index][1]);
    }
    ctx.closePath();
    ctx.fillStyle = color;
    ctx.fill();
}

function fillEllipse(x, y, width, height, color) {
    ctx.beginPath();
    ctx.ellipse(x + width / 2, y + height / 2, width / 2, height / 2, 0, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
}

function drawSwordAndHands(leftSide) {
    ctx.save();
    if (!leftSide) {
        ctx.translate(662, 0);
        ctx.scale(-1, 1);
    }

    const blade = [
        [292, 344], [288, 325], [283, 305],
        [278, 284], [272, 263], [267, 244]
    ];
    strokePath(blade, "#000", 9);
    strokePath(blade, "#f5f5f0", 5);
    fillPolygon([[263, 247], [265, 236], [271, 246]], "#000");
    fillPolygon([[266, 246], [266, 239], [269, 246]], "#f5f5f0");

    fillEllipse(283, 339, 20, 11, "#000");
    fillEllipse(287, 342, 12, 5, "#f5f5f0");
    strokePath([[292, 346], [296, 380]], "#000", 9);
    strokePath([[292, 348], [296, 378]], "#e1e1d7", 4);
    strokePath([[315, 361], [299, 359]], "#000", 15);

    fillEllipse(286, 347, 17, 17, "#000");
    fillEllipse(290, 350, 9, 11, "#fff");
    fillEllipse(288, 361, 17, 17, "#000");
    fillEllipse(292, 364, 9, 11, "#fff");
    strokePath([[291, 355], [298, 355]], "#000", 1);
    strokePath([[293, 369], [300, 369]], "#000", 1);
    ctx.restore();
}

function drawArrow(x, y, angle, length = 60) {
    const tipX = x + Math.cos(angle) * length;
    const tipY = y + Math.sin(angle) * length;
    strokePath([[x, y], [tipX, tipY]], "#784614", 4);

    const size = 10;
    fillPolygon([
        [tipX, tipY],
        [
            tipX - Math.cos(angle) * size + Math.cos(angle + Math.PI / 2) * size,
            tipY - Math.sin(angle) * size + Math.sin(angle + Math.PI / 2) * size
        ],
        [
            tipX - Math.cos(angle) * size - Math.cos(angle + Math.PI / 2) * size,
            tipY - Math.sin(angle) * size - Math.sin(angle + Math.PI / 2) * size
        ]
    ], "#b4b4b4");
}

function drawEnemyArrow(animation, currentTime) {
    const progress = Math.max(0, Math.min(1,
        (currentTime - animation.musicStartedAt) / ENEMY_ARROW_SECONDS
    ));
    drawArrow(410 + (750 - 410) * progress, 335, 0);
}

function drawSplitArrow(animation, progress) {
    const spread = 180 * progress;
    const fall = 250 * progress * progress;
    const rotation = progress * Math.PI * 1.5;
    drawArrowTail(animation.x - spread, animation.y + fall, -rotation);
    drawArrowHead(animation.x + spread, animation.y + fall, rotation);
}

function drawArrowTail(x, y, angle) {
    const length = 30;
    const startX = x - Math.cos(angle) * length;
    const startY = y - Math.sin(angle) * length;
    strokePath([[startX, startY], [x, y]], "#784614", 4);
    const size = 8;
    strokePath([[startX, startY], [
        startX + Math.cos(angle + Math.PI / 3) * size,
        startY + Math.sin(angle + Math.PI / 3) * size
    ]], "#b4b4b4", 3);
    strokePath([[startX, startY], [
        startX + Math.cos(angle - Math.PI / 3) * size,
        startY + Math.sin(angle - Math.PI / 3) * size
    ]], "#b4b4b4", 3);
}

function drawArrowHead(x, y, angle) {
    drawArrow(x, y, angle, 30);
}

function drawMissArrow(animation, progress) {
    const x = animation.x + 150 * progress;
    const y = animation.y - 100 * progress + 300 * progress * progress;
    drawArrow(x, y, progress * Math.PI * 2);
}

async function loadBestRecord() {
    try {
        const response = await fetch("/api/records/terrible_ninja");
        const data = await response.json();
        if (data.success && data.record.best_miss !== null) {
            state.bestMiss = data.record.best_miss;
            document.getElementById("bestRecord").textContent = state.bestMiss;
        }
    } catch (error) {
        console.error("BEST記録を読み込めません", error);
    }
}

async function saveRecord() {
    try {
        await fetch("/api/records/terrible_ninja/save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ miss_count: state.missCount })
        });
    } catch (error) {
        console.error("記録を保存できません", error);
    }
}

async function showResult() {
    if (state.resultShown) {
        return;
    }
    state.resultShown = true;
    state.playing = false;
    await saveRecord();

    let result;
    if (state.missCount <= 10) {
        result = ASSETS.results.high;
    } else if (state.missCount <= 20) {
        result = ASSETS.results.good;
    } else {
        result = ASSETS.results.redo;
    }

    document.getElementById("finalMissCount").textContent = state.missCount;
    document.getElementById("resultImage").src = result.image;
    document.getElementById("resultScreen").hidden = false;

    resultAudio = new Audio(result.audio);
    resultAudio.preload = "auto";
    try {
        await resultAudio.play();
    } catch (error) {
        console.error("結果BGMを再生できません", error);
    }
}

document.addEventListener("keydown", event => {
    if (event.repeat || state.resultShown) {
        return;
    }
    event.preventDefault();
    handleAction();
});

canvas.addEventListener("pointerdown", event => {
    event.preventDefault();
    handleAction();
});

window.addEventListener("load", initialize);
