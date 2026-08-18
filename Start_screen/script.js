// ==========================================
// ゲーム起動
// ==========================================

function openGame(gameName) {

    if (gameName === "Built_to_Scale2") {

        /*
         * Start_screen/index.html
         *
         *      ↓ ../
         *
         * GitHubリポジトリ
         *
         *      ↓ Built_to_Scale2/
         *
         * Built_to_Scale2
         */

        window.location.href = "../Built_to_Scale2/index.html";
    }
}


// ==========================================
// 作成中表示
// ==========================================

let comingSoonTimer = null;


function showComingSoon(gameName) {

    const overlay =
        document.getElementById("overlay");

    const message =
        document.getElementById("coming-message");


    message.textContent =
        gameName + "は作成中です";


    overlay.classList.add("show");


    // 以前のタイマーを削除
    if (comingSoonTimer !== null) {

        clearTimeout(comingSoonTimer);
    }


    // 2秒後に消す
    comingSoonTimer = setTimeout(function () {

        overlay.classList.remove("show");

    }, 2000);
}


// ==========================================
// 最高記録
// ==========================================

async function loadBestRecord() {

    try {

        const response =
            await fetch("../Built_to_Scale2/record.json");


        if (!response.ok) {

            return;
        }


        const data =
            await response.json();


        if (data.best_miss !== undefined) {

            document.getElementById(
                "built-record"
            ).textContent =
                data.best_miss + " miss";
        }

    } catch (error) {

        console.log(
            "record.jsonが見つかりません"
        );
    }
}


loadBestRecord();