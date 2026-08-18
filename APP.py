import pygame
import os
import numpy as np
import librosa
import time
import threading
from collections import OrderedDict

# =========================================================
# 安全なスロー再生版
# =========================================================
# 重要:
# 0.1倍速の「曲全体」を巨大なWAVに変換しません。
# 元音源を小さなチャンクに分け、必要な部分だけを
# librosaでスロー化してpygameへ順番に渡します。
# そのため0.1倍でもメモリ使用量が大きくなりにくいです。
# =========================================================

# ---------------------------------------------------------
# 音楽ファイル
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

music_path = os.path.join(
    BASE_DIR,
    "Terrible_Ninja",
    "BGM",
    "terrible_ninja.mp3"
)

if not os.path.isfile(music_path):
    # 元コードと同じ場所を想定しつつ、見つからない場合は
    # APP.pyのフォルダを検索します。
    candidate = os.path.join(
        BASE_DIR,
        "terrible_ninja.mp3"
    )
    if os.path.isfile(candidate):
        music_path = candidate


# ---------------------------------------------------------
# 音声読み込み
# ---------------------------------------------------------
print("Loading audio...")

y, sr = librosa.load(
    music_path,
    sr=None,
    mono=True
)

print("Audio loaded.")

# 元音源の長さ
source_duration = len(y) / float(sr)


# ---------------------------------------------------------
# pygame
# ---------------------------------------------------------
# librosaのサンプルレートに合わせる。
# これによりmake_sound()での変換を安定させる。
pygame.init()
pygame.mixer.init(
    frequency=int(sr),
    size=-16,
    channels=1,
    buffer=1024
)

WIDTH = 1200
HEIGHT = 700

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "譜面作成ツール - Safe Slow Playback"
)


# ---------------------------------------------------------
# フォント
# ---------------------------------------------------------
font_path = "C:/Windows/Fonts/meiryo.ttc"

if not os.path.isfile(font_path):
    font_path = None

title_font = pygame.font.Font(font_path, 32)
font = pygame.font.Font(font_path, 24)
small_font = pygame.font.Font(font_path, 18)


# =========================================================
# スロー再生設定
# =========================================================

SPEEDS = [0.1, 0.25, 0.5, 1.0]

current_speed = 1.0

# 1チャンクで使用する「元曲」の秒数。
# 0.1倍でも2秒 → 20秒の音声になるだけなので、
# 曲全体を10倍にするよりはるかに安全。
CHUNK_SOURCE_SECONDS = 2.0

# 先読みするチャンク数
PRELOAD_CHUNKS = 2

# pygameのChannel
music_channel = pygame.mixer.Channel(0)


# =========================================================
# チャンクキャッシュ
# =========================================================

# 同じ場所を再生するときの再計算を減らす。
# 最大数を制限してメモリを使いすぎないようにする。
chunk_cache = OrderedDict()
CACHE_LIMIT = 4


# ---------------------------------------------------------
# キャッシュキー
# ---------------------------------------------------------
def cache_key(speed, source_start):
    return (
        round(float(speed), 4),
        round(float(source_start), 3)
    )


# ---------------------------------------------------------
# キャッシュ保存
# ---------------------------------------------------------
def cache_put(key, sound):
    chunk_cache[key] = sound
    chunk_cache.move_to_end(key)

    while len(chunk_cache) > CACHE_LIMIT:
        chunk_cache.popitem(last=False)


# =========================================================
# チャンク生成
# =========================================================

def make_chunk(speed, source_start):
    """元音源の一部だけを速度変更してpygame Soundにする。"""

    source_start = max(
        0.0,
        min(
            source_start,
            source_duration
        )
    )

    key = cache_key(
        speed,
        source_start
    )

    if key in chunk_cache:
        sound = chunk_cache[key]
        chunk_cache.move_to_end(key)
        return sound

    start_sample = int(source_start * sr)
    end_sample = int(
        min(
            source_duration,
            source_start + CHUNK_SOURCE_SECONDS
        ) * sr
    )

    if end_sample <= start_sample:
        return None

    original_chunk = y[
        start_sample:end_sample
    ]

    # 通常速度は加工せずそのまま使用
    if abs(speed - 1.0) < 0.0001:
        processed = original_chunk
    else:
        # rate < 1.0 なら実際に音声が遅くなる
        processed = librosa.effects.time_stretch(
            original_chunk.astype(np.float32),
            rate=float(speed)
        )

    # pygame mixerは16bit signed PCMを使用
    processed = np.clip(
        processed,
        -1.0,
        1.0
    )

    pcm = (
        processed * 32767.0
    ).astype(np.int16)

    if len(pcm) == 0:
        return None

    pcm = np.column_stack((pcm, pcm))
    sound = pygame.sndarray.make_sound(pcm)

    cache_put(
        key,
        sound
    )

    return sound


# =========================================================
# チャンク再生管理
# =========================================================

play_generation = 0
play_lock = threading.Lock()

playing = False
current_time = 0.0

play_start_real_time = 0.0
play_start_music_time = 0.0

# 現在のチャンク情報
active_source_start = 0.0
active_chunk_source_length = 0.0
active_chunk_music_length = 0.0

# 次のチャンク生成用
next_chunk_sound = None
next_chunk_source_start = None

# バックグラウンド生成スレッド
prepare_thread = None
prepare_request = None
prepare_result = None
prepare_lock = threading.Lock()


# =========================================================
# バックグラウンドで次チャンクを作る
# =========================================================

def prepare_next_chunk(speed, source_start, generation):
    global prepare_result

    try:
        sound = make_chunk(
            speed,
            source_start
        )

        with prepare_lock:
            prepare_result = (
                generation,
                speed,
                source_start,
                sound
            )
    except Exception as exc:
        print(
            "Chunk generation error:",
            repr(exc)
        )
        with prepare_lock:
            prepare_result = (
                generation,
                speed,
                source_start,
                None
            )


# =========================================================
# 次チャンクの先読み開始
# =========================================================

def request_chunk(speed, source_start, generation):
    global prepare_thread
    global prepare_request
    global prepare_result

    with prepare_lock:
        prepare_request = (
            generation,
            speed,
            source_start
        )
        prepare_result = None

    def worker():
        with prepare_lock:
            request = prepare_request

        if request is None:
            return

        req_generation, req_speed, req_start = request

        prepare_next_chunk(
            req_speed,
            req_start,
            req_generation
        )

    prepare_thread = threading.Thread(
        target=worker,
        daemon=True
    )
    prepare_thread.start()


# =========================================================
# 現在チャンクの再生
# =========================================================

def play_chunk(source_start, generation):
    global active_source_start
    global active_chunk_source_length
    global active_chunk_music_length
    global next_chunk_sound
    global next_chunk_source_start

    if generation != play_generation:
        return False

    sound = make_chunk(
        current_speed,
        source_start
    )

    if sound is None:
        return False

    music_channel.stop()
    music_channel.play(sound)

    active_source_start = source_start

    remaining_source = max(
        0.0,
        source_duration - source_start
    )

    active_chunk_source_length = min(
        CHUNK_SOURCE_SECONDS,
        remaining_source
    )

    active_chunk_music_length = (
        active_chunk_source_length
        / current_speed
    )

    # 次のチャンクをバックグラウンドで準備
    next_source = (
        source_start
        + active_chunk_source_length
    )

    if next_source < source_duration - 0.001:
        request_chunk(
            current_speed,
            next_source,
            generation
        )
    else:
        next_chunk_sound = None
        next_chunk_source_start = None

    return True


# =========================================================
# 次チャンクへ切り替え
# =========================================================

def advance_chunk():
    global next_chunk_sound
    global next_chunk_source_start
    global current_time
    global play_start_real_time
    global play_start_music_time
    global active_source_start
    global active_chunk_source_length
    global active_chunk_music_length

    next_source = (
        active_source_start
        + active_chunk_source_length
    )

    if next_source >= source_duration - 0.001:
        music_channel.stop()
        return False

    # 先読み結果を確認
    prepared = None
    with prepare_lock:
        prepared = prepare_result

    if prepared is not None:
        generation, speed, source_start, sound = prepared

        if (
            generation == play_generation
            and abs(speed - current_speed) < 0.0001
            and abs(source_start - next_source) < 0.01
        ):
            next_chunk_sound = sound
            next_chunk_source_start = source_start

    if next_chunk_sound is not None:
        sound = next_chunk_sound
        next_chunk_sound = None
        next_chunk_source_start = None

        music_channel.play(sound)

        active_source_start = next_source

        remaining_source = max(
            0.0,
            source_duration - next_source
        )

        active_chunk_source_length = min(
            CHUNK_SOURCE_SECONDS,
            remaining_source
        )

        active_chunk_music_length = (
            active_chunk_source_length
            / current_speed
        )

        request_chunk(
            current_speed,
            next_source + active_chunk_source_length,
            play_generation
        )

        # 現在時刻はチャンク境界から正確に計算
        current_time = next_source
        play_start_music_time = current_time
        play_start_real_time = (
            pygame.time.get_ticks()
            / 1000.0
        )

        return True

    # まだ先読みが終わっていない場合は、ここで同期生成。
    # ただし2秒分だけなので、曲全体を作る方式より軽い。
    sound = make_chunk(
        current_speed,
        next_source
    )

    if sound is None:
        music_channel.stop()
        return False

    music_channel.play(sound)

    active_source_start = next_source

    remaining_source = max(
        0.0,
        source_duration - next_source
    )

    active_chunk_source_length = min(
        CHUNK_SOURCE_SECONDS,
        remaining_source
    )

    active_chunk_music_length = (
        active_chunk_source_length
        / current_speed
    )

    request_chunk(
        current_speed,
        next_source + active_chunk_source_length,
        play_generation
    )

    current_time = next_source
    play_start_music_time = current_time
    play_start_real_time = (
        pygame.time.get_ticks()
        / 1000.0
    )

    return True


# =========================================================
# 再生開始
# =========================================================

def start_music(start_time):
    global playing
    global play_start_real_time
    global play_start_music_time
    global current_time
    global play_generation
    global next_chunk_sound
    global next_chunk_source_start

    start_time = max(
        0.0,
        min(
            start_time,
            source_duration
        )
    )

    play_generation += 1

    generation = play_generation

    next_chunk_sound = None
    next_chunk_source_start = None

    music_channel.stop()

    if start_time >= source_duration - 0.001:
        current_time = source_duration
        playing = False
        return

    ok = play_chunk(
        start_time,
        generation
    )

    if not ok:
        playing = False
        return

    playing = True

    current_time = start_time

    play_start_real_time = (
        pygame.time.get_ticks()
        / 1000.0
    )

    play_start_music_time = start_time


# =========================================================
# 一時停止
# =========================================================

def pause_music():
    global playing
    global current_time
    global play_generation

    if playing:
        update_playback_time()

    play_generation += 1

    music_channel.stop()

    playing = False


# =========================================================
# 再生位置更新
# =========================================================

def update_playback_time():
    global current_time
    global playing

    if not playing:
        return

    now = (
        pygame.time.get_ticks()
        / 1000.0
    )

    elapsed = (
        now
        - play_start_real_time
    )

    current_time = (
        play_start_music_time
        + elapsed * current_speed
    )

    current_time = min(
        current_time,
        source_duration
    )


# =========================================================
# 再生チャンク監視
# =========================================================

def update_audio():
    global playing
    global current_time

    if not playing:
        return

    update_playback_time()

    # 現在チャンクが終わったら次へ
    if not music_channel.get_busy():
        if not advance_chunk():
            current_time = source_duration
            playing = False
            return

    # 曲全体の終了
    if current_time >= source_duration:
        current_time = source_duration
        music_channel.stop()
        playing = False


# =========================================================
# 波形データ
# =========================================================
# 元コードと同じく通常速度の波形だけを表示。
# ここでは追加のスロー音声を作らない。

mono_samples = y.astype(float)

max_value = np.max(
    np.abs(mono_samples)
)

if max_value != 0:
    mono_samples /= max_value

sample_count = len(mono_samples)
frequency = sr

duration = source_duration


# =========================================================
# 波形表示設定
# =========================================================

waveform_top = 250
waveform_height = 300

zoom = 1.0
view_start = 0.0


# =========================================================
# ノート
# =========================================================

notes = []


# =========================================================
# 時間 → X
# =========================================================

def time_from_x(x):
    view_duration = (
        duration / zoom
    )

    return (
        view_start
        + x / WIDTH
        * view_duration
    )


# =========================================================
# X → 時間
# =========================================================

def x_from_time(t):
    view_duration = (
        duration / zoom
    )

    return int(
        (
            t - view_start
        )
        / view_duration
        * WIDTH
    )


# =========================================================
# 一番近いノート
# =========================================================

def find_nearest_note(t):
    if not notes:
        return None

    nearest = min(
        notes,
        key=lambda n:
        abs(n["justtime"] - t)
    )

    distance = abs(
        nearest["justtime"] - t
    )

    if distance <= 0.15:
        return nearest

    return None


# =========================================================
# 保存
# =========================================================

def save_notes():
    path = os.path.join(
        BASE_DIR,
        "notes.txt"
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:
        f.write("notes = [\n")

        for note in sorted(
            notes,
            key=lambda n:
            n["justtime"]
        ):
            f.write(
                f'    {{"justtime": '
                f'{note["justtime"]:.3f}}},\n'
            )

        f.write("]\n")

    print("Notes saved.")


# =========================================================
# 波形描画
# =========================================================

def draw_waveform():
    surface = pygame.Surface(
        (
            WIDTH,
            waveform_height
        )
    )

    surface.fill(
        (25, 25, 25)
    )

    view_duration = (
        duration / zoom
    )

    view_end = (
        view_start
        + view_duration
    )

    start_sample = int(
        view_start * frequency
    )

    end_sample = int(
        view_end * frequency
    )

    start_sample = max(
        0,
        start_sample
    )

    end_sample = min(
        sample_count,
        end_sample
    )

    if end_sample <= start_sample:
        return surface

    visible = mono_samples[
        start_sample:end_sample
    ]

    visible_count = len(visible)

    for x in range(WIDTH):
        start = int(
            x / WIDTH * visible_count
        )

        end = int(
            (x + 1) / WIDTH * visible_count
        )

        if end <= start:
            end = start + 1

        if start >= visible_count:
            break

        end = min(
            end,
            visible_count
        )

        chunk = visible[start:end]

        if len(chunk) == 0:
            continue

        maximum = np.max(chunk)
        minimum = np.min(chunk)

        y1 = int(
            waveform_height / 2
            - maximum * 130
        )

        y2 = int(
            waveform_height / 2
            - minimum * 130
        )

        pygame.draw.line(
            surface,
            (170, 170, 170),
            (x, y1),
            (x, y2)
        )

    return surface


# =========================================================
# ドラッグ
# =========================================================

dragging = False
drag_start_x = 0
drag_start_view = 0


# =========================================================
# メインループ
# =========================================================

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # -------------------------------------------------
        # キーボード
        # -------------------------------------------------
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                start_music(current_time)

            elif event.key == pygame.K_SPACE:
                if playing:
                    pause_music()
                else:
                    start_music(current_time)

            elif event.key == pygame.K_LEFT:
                was_playing = playing
                if was_playing:
                    pause_music()

                current_time = max(
                    0.0,
                    current_time - 1.0
                )

                if was_playing:
                    start_music(current_time)

            elif event.key == pygame.K_RIGHT:
                was_playing = playing
                if was_playing:
                    pause_music()

                current_time = min(
                    duration,
                    current_time + 1.0
                )

                if was_playing:
                    start_music(current_time)

            elif event.key == pygame.K_BACKSPACE:
                if notes:
                    notes.pop()

            # ---------------------------------------------
            # 速度変更
            # ---------------------------------------------
            elif event.key in (
                pygame.K_1,
                pygame.K_2,
                pygame.K_3,
                pygame.K_4
            ):
                new_speed = {
                    pygame.K_1: 0.1,
                    pygame.K_2: 0.25,
                    pygame.K_3: 0.5,
                    pygame.K_4: 1.0
                }[event.key]

                if abs(new_speed - current_speed) > 0.0001:
                    was_playing = playing

                    if was_playing:
                        update_playback_time()
                        pause_music()

                    current_speed = new_speed

                    print(
                        "Speed:",
                        current_speed,
                        "x"
                    )

                    if was_playing:
                        start_music(current_time)

            elif event.key == pygame.K_f:
                save_notes()

            elif event.key == pygame.K_HOME:
                view_start = 0

            elif event.key == pygame.K_END:
                view_start = max(
                    0,
                    duration
                    - duration / zoom
                )

        # -------------------------------------------------
        # ホイール
        # -------------------------------------------------
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()

            if (
                waveform_top
                <= my
                <= waveform_top + waveform_height
            ):
                mouse_time_before = time_from_x(mx)

                if event.y > 0:
                    zoom *= 1.25
                else:
                    zoom /= 1.25

                zoom = max(
                    1.0,
                    min(30.0, zoom)
                )

                new_view_duration = (
                    duration / zoom
                )

                view_start = (
                    mouse_time_before
                    - mx / WIDTH
                    * new_view_duration
                )

                view_start = max(
                    0,
                    view_start
                )

                max_start = max(
                    0,
                    duration
                    - new_view_duration
                )

                view_start = min(
                    view_start,
                    max_start
                )

        # -------------------------------------------------
        # マウスクリック
        # -------------------------------------------------
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            if event.button == 2:
                if (
                    waveform_top
                    <= my
                    <= waveform_top + waveform_height
                ):
                    dragging = True
                    drag_start_x = mx
                    drag_start_view = view_start

            elif (
                waveform_top
                <= my
                <= waveform_top + waveform_height
            ):
                clicked_time = time_from_x(mx)

                if event.button == 1:
                    notes.append(
                        {
                            "justtime": clicked_time
                        }
                    )
                    notes.sort(
                        key=lambda n:
                        n["justtime"]
                    )

                elif event.button == 3:
                    nearest = find_nearest_note(
                        clicked_time
                    )

                    if nearest is not None:
                        notes.remove(nearest)

        # -------------------------------------------------
        # 中クリック解除
        # -------------------------------------------------
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                dragging = False

        # -------------------------------------------------
        # ドラッグ
        # -------------------------------------------------
        if event.type == pygame.MOUSEMOTION:
            if dragging:
                mx, my = event.pos

                dx = mx - drag_start_x

                view_duration = (
                    duration / zoom
                )

                time_move = (
                    dx / WIDTH
                    * view_duration
                )

                view_start = (
                    drag_start_view
                    - time_move
                )

                view_start = max(
                    0,
                    view_start
                )

                max_start = max(
                    0,
                    duration
                    - view_duration
                )

                view_start = min(
                    view_start,
                    max_start
                )

    # -----------------------------------------------------
    # 音声更新
    # -----------------------------------------------------
    update_audio()

    # -----------------------------------------------------
    # 描画
    # -----------------------------------------------------
    screen.fill(
        (15, 15, 15)
    )

    title = title_font.render(
        "譜面作成ツール",
        True,
        (255, 255, 255)
    )
    screen.blit(title, (30, 20))

    controls1 = font.render(
        "ENTER：再生    SPACE：一時停止    ← →：1秒移動",
        True,
        (220, 220, 220)
    )
    controls2 = font.render(
        "ホイール：ズーム    中クリック＋ドラッグ：表示移動",
        True,
        (220, 220, 220)
    )
    controls3 = font.render(
        "左クリック：ノート追加    右クリック：ノート削除",
        True,
        (220, 220, 220)
    )
    controls4 = font.render(
        "BACKSPACE：最後のノート削除    F：保存",
        True,
        (220, 220, 220)
    )
    controls5 = font.render(
        "速度：1=0.1倍  2=0.25倍  3=0.5倍  4=通常速",
        True,
        (220, 220, 220)
    )

    screen.blit(controls1, (30, 65))
    screen.blit(controls2, (30, 100))
    screen.blit(controls3, (30, 135))
    screen.blit(controls4, (30, 170))
    screen.blit(controls5, (30, 205))

    waveform = draw_waveform()
    screen.blit(
        waveform,
        (0, waveform_top)
    )

    # -----------------------------------------------------
    # 時間目盛り
    # -----------------------------------------------------
    view_duration = duration / zoom
    view_end = view_start + view_duration

    if zoom < 2:
        grid_interval = 5.0
    elif zoom < 4:
        grid_interval = 2.0
    elif zoom < 8:
        grid_interval = 1.0
    elif zoom < 15:
        grid_interval = 0.5
    elif zoom < 25:
        grid_interval = 0.2
    else:
        grid_interval = 0.1

    first_grid = (
        int(view_start / grid_interval)
        * grid_interval
    )

    second = first_grid
    last_label_right = -9999

    while second <= view_end:
        x = x_from_time(second)

        if 0 <= x <= WIDTH:
            pygame.draw.line(
                screen,
                (60, 60, 60),
                (x, waveform_top),
                (
                    x,
                    waveform_top
                    + waveform_height
                ),
                1
            )

            label = small_font.render(
                f"{second:.3f}s",
                True,
                (200, 200, 200)
            )

            label_width = label.get_width()

            if x >= last_label_right + 8:
                screen.blit(
                    label,
                    (
                        x + 3,
                        waveform_top + 5
                    )
                )
                last_label_right = (
                    x + label_width
                )

        second += grid_interval

    # -----------------------------------------------------
    # ノート
    # -----------------------------------------------------
    for note in notes:
        justtime = note["justtime"]

        if (
            view_start
            <= justtime
            <= view_end
        ):
            x = x_from_time(justtime)

            pygame.draw.line(
                screen,
                (100, 200, 100),
                (x, waveform_top),
                (
                    x,
                    waveform_top
                    + waveform_height
                ),
                3
            )

            pygame.draw.circle(
                screen,
                (100, 200, 100),
                (
                    x,
                    waveform_top
                    + waveform_height // 2
                ),
                7
            )

    # -----------------------------------------------------
    # 現在位置
    # -----------------------------------------------------
    if (
        view_start
        <= current_time
        <= view_end
    ):
        play_x = x_from_time(current_time)

        pygame.draw.line(
            screen,
            (255, 230, 40),
            (play_x, waveform_top),
            (
                play_x,
                waveform_top
                + waveform_height
            ),
            5
        )

        pygame.draw.polygon(
            screen,
            (255, 230, 40),
            [
                (
                    play_x - 10,
                    waveform_top - 5
                ),
                (
                    play_x + 10,
                    waveform_top - 5
                ),
                (
                    play_x,
                    waveform_top + 12
                )
            ]
        )

    # -----------------------------------------------------
    # マウス位置
    # -----------------------------------------------------
    mx, my = pygame.mouse.get_pos()
    mouse_time = time_from_x(mx)

    if (
        waveform_top
        <= my
        <= waveform_top + waveform_height
    ):
        pygame.draw.line(
            screen,
            (80, 180, 255),
            (mx, waveform_top),
            (
                mx,
                waveform_top
                + waveform_height
            ),
            2
        )

    # -----------------------------------------------------
    # 下部情報
    # -----------------------------------------------------
    current_text = font.render(
        f"現在の再生位置：{current_time:.3f} 秒",
        True,
        (255, 230, 40)
    )
    screen.blit(
        current_text,
        (30, 550)
    )

    mouse_text = font.render(
        f"マウス位置：{mouse_time:.3f} 秒",
        True,
        (80, 180, 255)
    )
    screen.blit(
        mouse_text,
        (350, 550)
    )

    note_text = font.render(
        f"ノート数：{len(notes)}",
        True,
        (255, 100, 100)
    )
    screen.blit(
        note_text,
        (700, 550)
    )

    duration_text = font.render(
        f"曲の長さ：{duration:.3f} 秒",
        True,
        (220, 220, 220)
    )
    screen.blit(
        duration_text,
        (900, 550)
    )

    zoom_text = small_font.render(
        f"ズーム：{zoom:.2f}x",
        True,
        (180, 180, 180)
    )
    screen.blit(
        zoom_text,
        (30, 660)
    )

    status_text = small_font.render(
        "左クリック：ノート追加 / 右クリック：ノート削除",
        True,
        (180, 180, 180)
    )
    screen.blit(
        status_text,
        (300, 660)
    )

    speed_text = small_font.render(
        f"速度：{current_speed}x",
        True,
        (150, 200, 150)
    )
    screen.blit(
        speed_text,
        (700, 660)
    )

    pygame.display.flip()

    # CPUを無駄に100%にしない
    clock.tick(60)


# =========================================================
# 終了
# =========================================================

music_channel.stop()
pygame.mixer.quit()
pygame.quit()