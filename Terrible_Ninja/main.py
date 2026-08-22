import pygame
import os
import math
import time
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Terrible Ninja")
clock = pygame.time.Clock()


# ウェブ環境用: ファイルパスの処理
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except:
    BASE_DIR = "/"

IMAGE_DIR = os.path.join(BASE_DIR, "IMAGE")
BGM_DIR = os.path.join(BASE_DIR, "BGM")
font = pygame.font.Font(None, 36)

music_path = os.path.join(BGM_DIR, "terrible_ninja.mp3")

hand = True

pygame.mixer.init()

pygame.mixer.music.load(music_path)



justtime_notes = [
    {"justtime": 9.435},
    {"justtime": 15.482},
    {"justtime": 15.701},
    {"justtime": 15.915},
    {"justtime": 21.951},
    {"justtime": 22.173},
    {"justtime": 22.284},
    {"justtime": 22.395},
    {"justtime": 22.615},
    {"justtime": 22.820},
    {"justtime": 27.358},
    {"justtime": 27.465},
    {"justtime": 27.574},
    {"justtime": 27.788},
    {"justtime": 28.005},
    {"justtime": 28.333},
    {"justtime": 28.434},
    {"justtime": 28.646},
    {"justtime": 28.757},
    {"justtime": 28.867},
    {"justtime": 29.083},
    {"justtime": 29.195},
    {"justtime": 29.302},
    {"justtime": 29.373},
    {"justtime": 29.441},
    {"justtime": 29.519},
    {"justtime": 29.719},
    {"justtime": 34.042},
    {"justtime": 34.101},
    {"justtime": 34.165},
    {"justtime": 34.268},
    {"justtime": 34.379},
    {"justtime": 34.486},
    {"justtime": 34.591},
    {"justtime": 34.651},
    {"justtime": 34.705},
    {"justtime": 34.808},
    {"justtime": 34.908},
    {"justtime": 34.967},
    {"justtime": 35.024},
    {"justtime": 35.132},
    {"justtime": 35.239},
    {"justtime": 35.341},
    {"justtime": 35.412},
    {"justtime": 35.562},
    {"justtime": 35.772},
    {"justtime": 35.829},
    {"justtime": 35.891},
    {"justtime": 35.945},
    {"justtime": 36.000},
    {"justtime": 36.101},
    {"justtime": 36.212},
    {"justtime": 36.260},
    {"justtime": 36.322},
    {"justtime": 36.376},
    {"justtime": 36.422},
    {"justtime": 36.536},
    {"justtime": 36.639},
    {"justtime": 40.953},
    {"justtime": 41.070},
    {"justtime": 41.181},
    {"justtime": 41.236},
    {"justtime": 41.293},
    {"justtime": 41.346},
    {"justtime": 41.453},
    {"justtime": 41.558},
    {"justtime": 41.612},
    {"justtime": 41.667},
    {"justtime": 41.726},
    {"justtime": 41.829},
    {"justtime": 41.941},
    {"justtime": 41.993},
    {"justtime": 42.050},
    {"justtime": 42.148},
    {"justtime": 42.260},
    {"justtime": 42.422},
    {"justtime": 42.531},
    {"justtime": 42.586},
    {"justtime": 42.691},
    {"justtime": 42.798},
    {"justtime": 42.898},
    {"justtime": 42.953},
    {"justtime": 43.060},
    {"justtime": 43.183},
    {"justtime": 43.233},
    {"justtime": 43.338},
    {"justtime": 43.441},
    {"justtime": 43.502},
    {"justtime": 43.555},
    {"justtime": 43.662},
    {"justtime": 43.774},
    {"justtime": 43.828},
    {"justtime": 43.879},
    {"justtime": 43.990},
    {"justtime": 44.045},
    {"justtime": 44.148},
    {"justtime": 44.202},
    {"justtime": 44.257},
    {"justtime": 44.309},
    {"justtime": 47.872},
    {"justtime": 47.918},
    {"justtime": 47.970},
    {"justtime": 48.091},
    {"justtime": 48.194},
    {"justtime": 48.232},
    {"justtime": 48.267},
    {"justtime": 48.305},
    {"justtime": 48.412},
    {"justtime": 48.508},
    {"justtime": 48.563},
    {"justtime": 48.627},
    {"justtime": 48.732},
    {"justtime": 48.841},
    {"justtime": 48.882},
    {"justtime": 48.914},
    {"justtime": 48.953},
    {"justtime": 49.064},
    {"justtime": 49.167},
    {"justtime": 49.224},
    {"justtime": 49.274},
    {"justtime": 49.381},
    {"justtime": 49.589},
    {"justtime": 49.646},
    {"justtime": 49.703},
    {"justtime": 49.814},
    {"justtime": 49.849},
    {"justtime": 49.885},
    {"justtime": 49.919},
    {"justtime": 50.033},
    {"justtime": 50.081},
    {"justtime": 50.131},
    {"justtime": 50.248},
    {"justtime": 50.282},
    {"justtime": 50.314},
    {"justtime": 50.350},
    {"justtime": 50.462},
    {"justtime": 54.772},
    {"justtime": 54.826},
    {"justtime": 54.886},
    {"justtime": 54.945},
    {"justtime": 54.995},
    {"justtime": 55.050},
    {"justtime": 55.102},
    {"justtime": 55.159},
    {"justtime": 55.216},
    {"justtime": 55.412},
    {"justtime": 55.640},
    {"justtime": 55.697},
    {"justtime": 55.747},
    {"justtime": 55.804},
    {"justtime": 55.861},
    {"justtime": 55.912},
    {"justtime": 55.964},
    {"justtime": 56.016},
    {"justtime": 56.071},
    {"justtime": 56.285},
    {"justtime": 56.500},
    {"justtime": 56.552},
    {"justtime": 56.607},
    {"justtime": 56.664},
    {"justtime": 56.719},
    {"justtime": 56.773},
    {"justtime": 56.880},
    {"justtime": 56.933},
    {"justtime": 56.985},
    {"justtime": 57.042},
    {"justtime": 57.095},
    {"justtime": 57.150},
    {"justtime": 57.197},
    {"justtime": 57.259},
    {"justtime": 57.314},
    {"justtime": 57.373},
    {"justtime": 57.936},
    {"justtime": 68.019},
]


enemy_justtime_notes = [
    {
        "justtime": note["justtime"] - 3.45
    }
    for note in justtime_notes[:-1]
]


changetime_notes = [
    {"changetime": 2.926},
    {"changetime": 6.409},
    {"changetime": 9.863},
    {"changetime": 13.312},
    {"changetime": 16.766},
    {"changetime": 20.222},
    {"changetime": 23.674},
    {"changetime": 27.128},
    {"changetime": 30.577},
    {"changetime": 34.031},
    {"changetime": 37.483},
    {"changetime": 40.943},
    {"changetime": 44.397},
    {"changetime": 47.851},
    {"changetime": 51.296},
    {"changetime": 54.754},
    {"changetime": 58.203},
    {"changetime": 61.662},
]


split_animations = []

miss_animations = []

enemy_arrow_animations = []
enemy_note_index = 0
ENEMY_ARROW_FLIGHT_SECONDS = 0.45

changetime_note_index = 0

background1 = pygame.image.load(
    os.path.join(IMAGE_DIR, "background1.png")
).convert_alpha()
background1 = pygame.transform.smoothscale(
    background1,
    screen.get_size()
)

background2 = pygame.image.load(
    os.path.join(IMAGE_DIR, "background2.png")
).convert_alpha()
background2 = pygame.transform.smoothscale(
    background2,
    screen.get_size()
)

background_tf = True

miss_count = 0

def draw_split_arrow(x, y, progress):
    """
    矢が中央で2つに割れて、
    左右に放物線を描きながら落ちるアニメーション
    progress: 0.0 ～ 1.0
    """

    # 中央の位置
    center_x = x
    center_y = y

    # 左右への移動量
    spread = 180 * progress

    # 落下量
    fall = 250 * (progress ** 2)

    # 回転
    rotation = progress * math.pi * 1.5

    # 左側
    left_x = center_x - spread
    left_y = center_y + fall

    # 右側
    right_x = center_x + spread
    right_y = center_y + fall

    # 後ろ半分と矢じり側を別々に描く。
    # progressが0のときは、2つがつながって1本の矢に見える。
    draw_arrow_tail_piece(
        left_x,
        left_y,
        -rotation
    )

    draw_arrow_head_piece(
        right_x,
        right_y,
        rotation
    )


def draw_arrow_tail_piece(x, y, angle):
    """切断された矢の後ろ半分を描く。"""
    length = 30
    start_x = x - math.cos(angle) * length
    start_y = y - math.sin(angle) * length

    pygame.draw.line(
        screen,
        (120, 70, 20),
        (start_x, start_y),
        (x, y),
        4
    )

    # 矢羽
    feather_size = 8
    pygame.draw.line(
        screen,
        (180, 180, 180),
        (start_x, start_y),
        (
            start_x + math.cos(angle + math.pi / 3) * feather_size,
            start_y + math.sin(angle + math.pi / 3) * feather_size
        ),
        3
    )
    pygame.draw.line(
        screen,
        (180, 180, 180),
        (start_x, start_y),
        (
            start_x + math.cos(angle - math.pi / 3) * feather_size,
            start_y + math.sin(angle - math.pi / 3) * feather_size
        ),
        3
    )


def draw_arrow_head_piece(x, y, angle):
    """切断された矢の矢じり側半分を描く。"""
    length = 30
    tip_x = x + math.cos(angle) * length
    tip_y = y + math.sin(angle) * length

    pygame.draw.line(
        screen,
        (120, 70, 20),
        (x, y),
        (tip_x, tip_y),
        4
    )

    size = 10
    left_x = (
        tip_x
        - math.cos(angle) * size
        + math.cos(angle + math.pi / 2) * size
    )
    left_y = (
        tip_y
        - math.sin(angle) * size
        + math.sin(angle + math.pi / 2) * size
    )
    right_x = (
        tip_x
        - math.cos(angle) * size
        - math.cos(angle + math.pi / 2) * size
    )
    right_y = (
        tip_y
        - math.sin(angle) * size
        - math.sin(angle + math.pi / 2) * size
    )

    pygame.draw.polygon(
        screen,
        (180, 180, 180),
        [
            (tip_x, tip_y),
            (left_x, left_y),
            (right_x, right_y)
        ]
    )


def draw_arrow_piece(x, y, angle):
    length = 60

    tip_x = x + math.cos(angle) * length
    tip_y = y + math.sin(angle) * length

    pygame.draw.line(
        screen,
        (120, 70, 20),
        (x, y),
        (tip_x, tip_y),
        4
    )

    size = 10

    left_x = (
        tip_x
        - math.cos(angle) * size
        + math.cos(angle + math.pi / 2) * size
    )

    left_y = (
        tip_y
        - math.sin(angle) * size
        + math.sin(angle + math.pi / 2) * size
    )

    right_x = (
        tip_x
        - math.cos(angle) * size
        - math.cos(angle + math.pi / 2) * size
    )

    right_y = (
        tip_y
        - math.sin(angle) * size
        - math.sin(angle + math.pi / 2) * size
    )

    pygame.draw.polygon(
        screen,
        (180, 180, 180),
        [
            (tip_x, tip_y),
            (left_x, left_y),
            (right_x, right_y)
        ]
    )


def draw_enemy_arrow(animation, current_time):
    """白い忍者が放った矢を、右方向へ飛ばす。"""
    progress = (
        current_time - animation["start_time"]
    ) / ENEMY_ARROW_FLIGHT_SECONDS
    progress = max(0.0, min(1.0, progress))

    start_x = 410
    start_y = 335
    end_x = 750

    x = start_x + (end_x - start_x) * progress
    y = start_y
    angle = 0

    draw_arrow_piece(x, y, angle)


def judgement(current_time):
    global miss_count
    
    evaluation = None
    
    if not justtime_notes:
        return False
    
    nearest_note = min(
        justtime_notes,
        key=lambda note: abs(
            note["justtime"] - current_time
        )
    )
    
    difference = abs(
        nearest_note["justtime"] - current_time
    )
    
    if difference <= 0.15:
        
        justtime_notes.remove(
            nearest_note
        )
        print("perfect")
        evaluation = "perfect"
        return evaluation
        
    elif difference <= 0.2:
        justtime_notes.remove(
            nearest_note
        )
        evaluation = "miss"
        print("miss")
        miss_count += 1
        return evaluation
    return evaluation

def draw_miss_arrow(x, y, progress):
    """割れずに放物線を描きながら落ちる矢を描画する。"""
    move_x = 150 * progress
    move_y = (
        -100 * progress
        + 300 * (progress ** 2)
    )
    rotation = progress * math.pi * 2

    draw_arrow_piece(
        x + move_x,
        y + move_y,
        rotation
    )

def draw_hands():
    if hand == True:
        # 参考画像のように少し反った刀身を、黒い縁から描く
        blade_points = [
            (292, 344),
            (288, 325),
            (283, 305),
            (278, 284),
            (272, 263),
            (267, 244)
        ]
        pygame.draw.lines(
            screen,
            (0, 0, 0),
            False,
            blade_points,
            9
        )
        pygame.draw.lines(
            screen,
            (245, 245, 240),
            False,
            blade_points,
            5
        )

        # 細く尖った切っ先
        pygame.draw.polygon(
            screen,
            (0, 0, 0),
            [
                (263, 247),
                (265, 236),
                (271, 246)
            ]
        )
        pygame.draw.polygon(
            screen,
            (245, 245, 240),
            [
                (266, 246),
                (266, 239),
                (269, 246)
            ]
        )

        # 小さな楕円形の鍔
        pygame.draw.ellipse(
            screen,
            (0, 0, 0),
            (283, 339, 20, 11)
        )
        pygame.draw.ellipse(
            screen,
            (245, 245, 240),
            (287, 342, 12, 5)
        )

        # 縦向きの柄
        pygame.draw.line(
            screen,
            (0, 0, 0),
            (292, 346),
            (296, 380),
            9
        )
        pygame.draw.line(
            screen,
            (225, 225, 215),
            (292, 348),
            (296, 378),
            4
        )

        # 忍者の左側から手元へつながる短い腕
        pygame.draw.line(
            screen,
            (0, 0, 0),
            (315, 361),
            (299, 359),
            15
        )

        # 白い手を柄の上下に並べる
        pygame.draw.ellipse(
            screen,
            (0, 0, 0),
            (286, 347, 17, 17)
        )
        pygame.draw.ellipse(
            screen,
            (255, 255, 255),
            (290, 350, 9, 11)
        )
        pygame.draw.ellipse(
            screen,
            (0, 0, 0),
            (288, 361, 17, 17)
        )
        pygame.draw.ellipse(
            screen,
            (255, 255, 255),
            (292, 364, 9, 11)
        )

        # 指の区切り線
        pygame.draw.line(
            screen,
            (0, 0, 0),
            (291, 355),
            (298, 355),
            1
        )
        pygame.draw.line(
            screen,
            (0, 0, 0),
            (293, 369),
            (300, 369),
            1
        )
    else:
        # Falseでは刀と手を左右反転して描く
        blade_points = [
            (370, 344),
            (374, 325),
            (379, 305),
            (384, 284),
            (390, 263),
            (395, 244)
        ]
        pygame.draw.lines(
            screen,
            (0, 0, 0),
            False,
            blade_points,
            9
        )
        pygame.draw.lines(
            screen,
            (245, 245, 240),
            False,
            blade_points,
            5
        )

        # 細く尖った切っ先
        pygame.draw.polygon(
            screen,
            (0, 0, 0),
            [
                (399, 247),
                (397, 236),
                (391, 246)
            ]
        )
        pygame.draw.polygon(
            screen,
            (245, 245, 240),
            [
                (396, 246),
                (396, 239),
                (393, 246)
            ]
        )

        # 小さな楕円形の鍔
        pygame.draw.ellipse(
            screen,
            (0, 0, 0),
            (359, 339, 20, 11)
        )
        pygame.draw.ellipse(
            screen,
            (245, 245, 240),
            (363, 342, 12, 5)
        )

        # 縦向きの柄
        pygame.draw.line(
            screen,
            (0, 0, 0),
            (370, 346),
            (366, 380),
            9
        )
        pygame.draw.line(
            screen,
            (225, 225, 215),
            (370, 348),
            (366, 378),
            4
        )

        # 忍者の右側から手元へつながる短い腕
        pygame.draw.line(
            screen,
            (0, 0, 0),
            (349, 361),
            (363, 359),
            15
        )

        # 白い手を柄の上下に並べる
        pygame.draw.ellipse(
            screen,
            (0, 0, 0),
            (359, 347, 17, 17)
        )
        pygame.draw.ellipse(
            screen,
            (255, 255, 255),
            (363, 350, 9, 11)
        )
        pygame.draw.ellipse(
            screen,
            (0, 0, 0),
            (357, 361, 17, 17)
        )
        pygame.draw.ellipse(
            screen,
            (255, 255, 255),
            (361, 364, 9, 11)
        )

        # 指の区切り線
        pygame.draw.line(
            screen,
            (0, 0, 0),
            (364, 355),
            (371, 355),
            1
        )
        pygame.draw.line(
            screen,
            (0, 0, 0),
            (362, 369),
            (369, 369),
            1
        )

def load_result_image(filename):
    """結果画像を画面全体に収まるサイズで読み込む。"""
    image = pygame.image.load(os.path.join(IMAGE_DIR, filename)).convert()
    return pygame.transform.scale(image, screen.get_size())

def play_result_bgm(filename):
    """結果画面用のBGMに切り替える。"""
    pygame.mixer.music.load(os.path.join(BGM_DIR, filename))
    pygame.mixer.music.play()

running = True

pygame.mixer.music.play()

message_surface = None
message_expires_at = 0.0
MESSAGE_DISPLAY_SECONDS = 1.0

result_mode = False
result_image = None


while running:
    
    current_time = max(
        0.0,
        pygame.mixer.music.get_pos() / 1000.0
    )
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if (
            not result_mode
            and (
                event.type == pygame.KEYDOWN
                or event.type == pygame.MOUSEBUTTONDOWN
            )
        ):
            if hand:
                hand = False
            else:
                hand = True
            print(current_time)
            evaluation = judgement(current_time)

            if evaluation in ("perfect", "miss"):
                message_surface = font.render(
                    evaluation,
                    True,
                    (0, 0, 0)
                )
                message_expires_at = (
                    time.time() + MESSAGE_DISPLAY_SECONDS
                )
            
            if evaluation == "perfect":
                split_animations.append({
                    "start_time": time.time(),
                    "x": 400,
                    "y": 300
            })
            
            if evaluation == "miss":
                miss_animations.append({
                    "start_time": time.time(),
                    "x": 400,
                    "y": 300
            })

    if result_mode:
        screen.blit(result_image, (0, 0))
        pygame.display.flip()
        clock.tick(60)
        continue

    # enemy_justtime_notesの時刻ごとに一度だけ矢を発射する
    while enemy_note_index < len(enemy_justtime_notes):
        enemy_note_time = enemy_justtime_notes[
            enemy_note_index
        ]["justtime"]

        if current_time < enemy_note_time:
            break

        enemy_arrow_animations.append({
            "start_time": enemy_note_time
        })
        enemy_note_index += 1

    if changetime_note_index < len(changetime_notes):
        target_time = changetime_notes[changetime_note_index]["changetime"]
        
        if current_time >= target_time:
            background_tf = not background_tf
            
            miss_animations.clear()
            
            changetime_note_index += 1
    
    if background_tf:
        screen.blit(background2, (0,0))
        
        draw_hands()
    else:
        
        screen.blit(background1, (0, 0))

    for animation in enemy_arrow_animations[:]:
        elapsed = current_time - animation["start_time"]

        if elapsed >= ENEMY_ARROW_FLIGHT_SECONDS:
            enemy_arrow_animations.remove(animation)
            continue

        draw_enemy_arrow(animation, current_time)
    
    for animation in split_animations[:]:
        
        progress = (
            time.time() - animation["start_time"]
        ) / 0.8
        
        if progress >= 1:
            split_animations.remove(animation)
            continue
        
        draw_split_arrow(
            animation["x"],
            animation["y"],
            progress
        )
    
    for note in justtime_notes[:]:
        
        if current_time >= note["justtime"] + 0.21:
            
            justtime_notes.remove(note)
            
            miss_animations.append({
                "x": random.randint(490, 510),
                "y": random.randint(240, 260)
            })
            message_surface = font.render(
                "miss",
                True,
                (0, 0, 0)
            )
            message_expires_at = (
                time.time() + MESSAGE_DISPLAY_SECONDS
            )
            print("miss")
            miss_count += 1
    
    
    for animation in miss_animations[:]:
        if "start_time" in animation:
            progress = (
                time.time() - animation["start_time"]
            ) / 1.2

            if progress >= 1:
                miss_animations.remove(animation)
                continue
        else:
            # 時間切れのMissは、これまでどおりその場に残す
            progress = 0.0

        draw_miss_arrow(
            animation["x"],
            animation["y"],
            progress
        )

    if (
        message_surface is not None
        and time.time() < message_expires_at
    ):
        screen.blit(message_surface, (350, 200))
    elif message_surface is not None:
        message_surface = None
    
    text = font.render(
        "MISS : " + str(miss_count),
        True,
        (0, 0, 0)
    )
    
    screen.blit(text, (30, 30))

    if not pygame.mixer.music.get_busy():
        if miss_count <= 10:
            result_image_name = "high_level.png"
            result_bgm_name = "high_level.mp3"
        elif miss_count <= 20:
            result_image_name = "good.png"
            result_bgm_name = "good.mp3"
        else:
            result_image_name = "background.png"
            result_bgm_name = "redo.mp3"

        result_image = load_result_image(result_image_name)
        play_result_bgm(result_bgm_name)
        result_mode = True
        continue
    
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
