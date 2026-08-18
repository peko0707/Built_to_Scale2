import cv2
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

video_path = os.path.join(IMAGE_DIR, "terrible_ninja.mp4")
music_path = os.path.join(BGM_DIR, "terrible_ninja.mp3")

video = cv2.VideoCapture(video_path)
fps = video.get(cv2.CAP_PROP_FPS) or 30


zoom = 1
width = int(screen.get_width() * zoom)
height = int(screen.get_height() * zoom)

pygame.mixer.init()

pygame.mixer.music.load(music_path)



justtime_notes = [
    {"justtime": 6.214},
    {"justtime": 12.248},
    {"justtime": 12.466},
    {"justtime": 12.689},
    {"justtime": 18.731},
    {"justtime": 18.946},
    {"justtime": 19.049},
    {"justtime": 19.169},
    {"justtime": 19.385},
    {"justtime": 19.598},
    {"justtime": 24.124},
    {"justtime": 24.229},
    {"justtime": 24.343},
    {"justtime": 24.559},
    {"justtime": 24.780},
    {"justtime": 25.093},
    {"justtime": 25.199},
    {"justtime": 25.423},
    {"justtime": 25.529},
    {"justtime": 25.644},
    {"justtime": 25.859},
    {"justtime": 25.968},
    {"justtime": 26.067},
    {"justtime": 26.143},
    {"justtime": 26.219},
    {"justtime": 26.290},
    {"justtime": 26.502},
    {"justtime": 30.806},
    {"justtime": 30.860},
    {"justtime": 30.917},
    {"justtime": 31.031},
    {"justtime": 31.140},
    {"justtime": 31.247},
    {"justtime": 31.352},
    {"justtime": 31.410},
    {"justtime": 31.462},
    {"justtime": 31.575},
    {"justtime": 31.676},
    {"justtime": 31.724},
    {"justtime": 31.785},
    {"justtime": 31.893},
    {"justtime": 32.000},
    {"justtime": 32.107},
    {"justtime": 32.157},
    {"justtime": 32.326},
    {"justtime": 32.530},
    {"justtime": 32.586},
    {"justtime": 32.643},
    {"justtime": 32.705},
    {"justtime": 32.759},
    {"justtime": 32.862},
    {"justtime": 32.971},
    {"justtime": 33.019},
    {"justtime": 33.074},
    {"justtime": 33.134},
    {"justtime": 33.192},
    {"justtime": 33.297},
    {"justtime": 33.406},
    {"justtime": 37.712},
    {"justtime": 37.823},
    {"justtime": 37.939},
    {"justtime": 37.992},
    {"justtime": 38.050},
    {"justtime": 38.095},
    {"justtime": 38.217},
    {"justtime": 38.320},
    {"justtime": 38.372},
    {"justtime": 38.425},
    {"justtime": 38.483},
    {"justtime": 38.586},
    {"justtime": 38.693},
    {"justtime": 38.753},
    {"justtime": 38.805},
    {"justtime": 38.914},
    {"justtime": 39.025},
    {"justtime": 39.062},
    {"justtime": 39.178},
    {"justtime": 39.291},
    {"justtime": 39.339},
    {"justtime": 39.444},
    {"justtime": 39.551},
    {"justtime": 39.669},
    {"justtime": 39.720},
    {"justtime": 39.828},
    {"justtime": 39.939},
    {"justtime": 39.993},
    {"justtime": 40.085},
    {"justtime": 40.201},
    {"justtime": 40.261},
    {"justtime": 40.312},
    {"justtime": 40.417},
    {"justtime": 40.529},
    {"justtime": 40.582},
    {"justtime": 40.634},
    {"justtime": 40.743},
    {"justtime": 40.801},
    {"justtime": 40.908},
    {"justtime": 40.962},
    {"justtime": 41.013},
    {"justtime": 41.069},
    {"justtime": 44.622},
    {"justtime": 44.673},
    {"justtime": 44.721},
    {"justtime": 44.836},
    {"justtime": 44.947},
    {"justtime": 44.989},
    {"justtime": 45.018},
    {"justtime": 45.059},
    {"justtime": 45.170},
    {"justtime": 45.275},
    {"justtime": 45.327},
    {"justtime": 45.385},
    {"justtime": 45.492},
    {"justtime": 45.599},
    {"justtime": 45.636},
    {"justtime": 45.673},
    {"justtime": 45.710},
    {"justtime": 45.826},
    {"justtime": 45.923},
    {"justtime": 45.979},
    {"justtime": 46.030},
    {"justtime": 46.141},
    {"justtime": 46.346},
    {"justtime": 46.418},
    {"justtime": 46.465},
    {"justtime": 46.572},
    {"justtime": 46.610},
    {"justtime": 46.641},
    {"justtime": 46.674},
    {"justtime": 46.789},
    {"justtime": 46.843},
    {"justtime": 46.900},
    {"justtime": 47.003},
    {"justtime": 47.041},
    {"justtime": 47.069},
    {"justtime": 47.109},
    {"justtime": 47.216},
    {"justtime": 51.529},
    {"justtime": 51.584},
    {"justtime": 51.642},
    {"justtime": 51.696},
    {"justtime": 51.754},
    {"justtime": 51.805},
    {"justtime": 51.857},
    {"justtime": 51.912},
    {"justtime": 51.968},
    {"justtime": 52.187},
    {"justtime": 52.391},
    {"justtime": 52.446},
    {"justtime": 52.504},
    {"justtime": 52.564},
    {"justtime": 52.618},
    {"justtime": 52.669},
    {"justtime": 52.723},
    {"justtime": 52.774},
    {"justtime": 52.828},
    {"justtime": 53.047},
    {"justtime": 53.259},
    {"justtime": 53.311},
    {"justtime": 53.364},
    {"justtime": 53.426},
    {"justtime": 53.482},
    {"justtime": 53.529},
    {"justtime": 53.641},
    {"justtime": 53.692},
    {"justtime": 53.739},
    {"justtime": 53.797},
    {"justtime": 53.855},
    {"justtime": 53.907},
    {"justtime": 53.954},
    {"justtime": 54.016},
    {"justtime": 54.069},
    {"justtime": 54.125},
    {"justtime": 54.701},
    {"justtime": 64.746},
]

changetime_notes = [
    {"changetime": 3.165},
    {"changetime": 6.618},
    {"changetime": 10.070},
    {"changetime": 13.527},
    {"changetime": 16.979},
    {"changetime": 20.431},
    {"changetime": 23.886},
    {"changetime": 27.336},
    {"changetime": 30.789},
    {"changetime": 34.232},
    {"changetime": 37.702},
    {"changetime": 41.148},
    {"changetime": 44.607},
    {"changetime": 48.048},
    {"changetime": 51.511},
    {"changetime": 54.966},
    {"changetime": 58.416},
]

split_animations = []

miss_animations = []

start_time = time.time()

changetime_note_index = 0

background = pygame.image.load(
    os.path.join(IMAGE_DIR, "background.png")
    ).convert_alpha()

background_tf = False

left_image = pygame.image.load(
    os.path.join(IMAGE_DIR, "left.png")
    ).convert_alpha()

right_image = pygame.image.load(
    os.path.join(IMAGE_DIR, "right.png")
    ).convert_alpha()



ninja_image = left_image


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

    # 左右の矢を描画
    draw_arrow_piece(
        left_x,
        left_y,
        math.pi + rotation
    )

    draw_arrow_piece(
        right_x,
        right_y,
        rotation
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
    
    if difference <= 0.1:
        
        justtime_notes.remove(
            nearest_note
        )
        print("perfect")
        evaluation = "perfect"
        return evaluation
        
    #elif difference <= 0.1:
    #    justtime_notes.remove(
    #        nearest_note
    #    )
    #    evaluation = "miss"
    #    return evaluation
    return evaluation

def draw_miss_arrow(x, y):
    draw_arrow_piece(
        x,
        y,
        0
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

while running:
    current_time = time.time() - start_time
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            
            evaluation = judgement(current_time)
            
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
            
            
            if ninja_image == left_image:
                ninja_image = right_image
            elif ninja_image == right_image:
                ninja_image = left_image
    
    
    
    if changetime_note_index < len(changetime_notes):
        target_time = changetime_notes[changetime_note_index]["changetime"]
        
        if current_time >= target_time:
            background_tf = not background_tf
            
            miss_animations.clear()
            
            changetime_note_index += 1
    
    
    
    ok, frame = video.read()

    if not ok:
        break

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    surface = pygame.image.frombuffer(
        frame.data,
        frame.shape[1::-1],
        "RGB"
    )

    surface = pygame.transform.scale(
        surface,
        (width, height)
    )
    
    
    if background_tf:
        screen.blit(background, (0,0))
        if ninja_image == left_image:
            x = 267
            y = 4
        elif ninja_image == right_image:
            x = 283
            y = 0
        screen.blit(ninja_image, (x,y))
        
    else:
        screen.blit(
            surface,
        (
            (screen.get_width() - width) // 2,
            (screen.get_width() - height) // 2 - 100
        )
    )
    
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
        
        if current_time >= note["justtime"] + 0.4:
            
            justtime_notes.remove(note)
            
            miss_animations.append({
                "x": random.randint(490, 510),
                "y": random.randint(240, 260)
            })
            
            print("miss")
    
    
    for animation in miss_animations:
        draw_miss_arrow(
            animation["x"],
            animation["y"]
        )
        
        
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
