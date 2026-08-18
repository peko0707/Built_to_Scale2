import pygame
import os
import subprocess
import sys
import json

pygame.init()

# ==========================================
# 基本設定
# ==========================================

WIDTH = 1200
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rhythm Game Launcher")
clock = pygame.time.Clock()

# フォント
font_path = "C:/Windows/Fonts/meiryo.ttc"
if not os.path.isfile(font_path):
    font_path = None

title_font = pygame.font.Font(font_path, 48)
game_font = pygame.font.Font(font_path, 32)
small_font = pygame.font.Font(font_path, 20)

# 色
BG_COLOR = (20, 20, 30)
TITLE_COLOR = (255, 255, 255)
GAME_COLOR = (200, 200, 200)
GAME_HOVER_COLOR = (255, 255, 100)
RECORD_COLOR = (100, 200, 100)
BUTTON_COLOR = (60, 80, 200)
BUTTON_HOVER_COLOR = (100, 120, 255)
TEXT_COLOR = (255, 100, 100)

# ==========================================
# 最高記録読み込み関数
# ==========================================

def load_best_record(game_dir):
    """ゲームディレクトリからrecord.jsonを読み込む"""
    record_file = os.path.join(game_dir, "record.json")
    
    if os.path.isfile(record_file):
        try:
            with open(record_file, "r") as f:
                data = json.load(f)
                best_miss = data.get("best_miss")
                if best_miss is not None:
                    return f"{best_miss} miss"
        except:
            pass
    
    return ""  # ファイルが存在しないか読み込み失敗なら空文字列

# ==========================================
# ゲームリスト（後から追加しやすいように構造化）
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RTG_DIR = os.path.dirname(BASE_DIR)

# ゲーム定義
game_definitions = [
    {
        "name": "Built to Scale 2",
        "script": os.path.join(RTG_DIR, "Built_to_Scale2", "main.py"),
        "game_dir": os.path.join(RTG_DIR, "Built_to_Scale2"),
        "status": "available"
    },
    {
        "name": "Terrible Ninja",
        "script": os.path.join(RTG_DIR, "Terrible_Ninja", "main.py"),
        "game_dir": os.path.join(RTG_DIR, "Terrible_Ninja"),
        "status": "coming_soon"
    },
    # ここに新しいゲームを追加していく
    # {
    #     "name": "New Game",
    #     "script": os.path.join(RTG_DIR, "New_Game", "main.py"),
    #     "game_dir": os.path.join(RTG_DIR, "New_Game"),
    #     "status": "available"
    # },
]

# ゲームリストに最高記録を追加
games = []
for game_def in game_definitions:
    game = game_def.copy()
    game["best_record"] = load_best_record(game_def["game_dir"])
    games.append(game)

# ==========================================
# ゲームボタン領域の計算
# ==========================================

GAME_START_Y = 200
GAME_SPACING = 100
BUTTON_WIDTH = 400
BUTTON_HEIGHT = 70

game_buttons = []
for i, game in enumerate(games):
    y = GAME_START_Y + i * GAME_SPACING
    game_buttons.append({
        "game": game,
        "rect": pygame.Rect(150, y, BUTTON_WIDTH, BUTTON_HEIGHT),
        "hovered": False
    })

# ==========================================
# ランキング領域
# ==========================================

ranking_rect = pygame.Rect(650, 150, 500, 500)

# ==========================================
# "作成中" メッセージ表示用
# ==========================================

show_coming_soon = False
coming_soon_game_name = ""
coming_soon_timer = 0
COMING_SOON_DURATION = 2000  # ミリ秒

# ==========================================
# メインループ
# ==========================================

running = True

while running:
    dt = clock.tick(60)

    # ==================================
    # イベント処理
    # ==================================

    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ゲームボタンクリック
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for button_info in game_buttons:
                    if button_info["rect"].collidepoint(mouse_pos):
                        game = button_info["game"]

                        if game["status"] == "available":
                            # ゲーム起動
                            try:
                                subprocess.Popen(
                                    [sys.executable, game["script"]]
                                )
                                # 起動後、メインウィンドウを最小化
                                # （オプション）
                            except Exception as e:
                                print(f"Error launching {game['name']}: {e}")

                        elif game["status"] == "coming_soon":
                            # "作成中" メッセージ表示
                            show_coming_soon = True
                            coming_soon_game_name = game["name"]
                            coming_soon_timer = COMING_SOON_DURATION

    # ==================================
    # ホバー判定
    # ==================================

    for button_info in game_buttons:
        button_info["hovered"] = button_info["rect"].collidepoint(
            mouse_pos
        )

    # ==================================
    # "作成中" メッセージのタイマー
    # ==================================

    if show_coming_soon:
        coming_soon_timer -= dt
        if coming_soon_timer <= 0:
            show_coming_soon = False

    # ==================================
    # 描画
    # ==================================

    screen.fill(BG_COLOR)

    # ========== タイトル ==========

    title_text = title_font.render(
        "Rhythm Game Launcher",
        True,
        TITLE_COLOR
    )

    title_rect = title_text.get_rect(center=(WIDTH // 2, 50))
    screen.blit(title_text, title_rect)

    # ========== ゲームボタン ==========

    for button_info in game_buttons:
        game = button_info["game"]
        rect = button_info["rect"]
        hovered = button_info["hovered"]

        # ボタン背景
        button_bg_color = (
            BUTTON_HOVER_COLOR
            if hovered
            else BUTTON_COLOR
        )

        pygame.draw.rect(
            screen,
            button_bg_color,
            rect,
            border_radius=10
        )

        # ボタン枠
        pygame.draw.rect(
            screen,
            GAME_HOVER_COLOR if hovered else GAME_COLOR,
            rect,
            3,
            border_radius=10
        )

        # ゲーム名
        game_name_text = game_font.render(
            game["name"],
            True,
            GAME_HOVER_COLOR if hovered else GAME_COLOR
        )

        name_x = rect.x + 20
        name_y = rect.y + 15

        screen.blit(game_name_text, (name_x, name_y))

        # 最高記録（存在する場合のみ表示）
        if game["best_record"]:
            record_text = small_font.render(
                game["best_record"],
                True,
                RECORD_COLOR
            )

            record_x = rect.right - record_text.get_width() - 20
            record_y = rect.y + 25

            screen.blit(record_text, (record_x, record_y))

    # ========== ランキング表示 ==========

    # ランキングタイトル
    ranking_title = game_font.render(
        "Ranking",
        True,
        TITLE_COLOR
    )

    screen.blit(
        ranking_title,
        (ranking_rect.x, ranking_rect.y - 50)
    )

    # ランキング領域の枠
    pygame.draw.rect(
        screen,
        GAME_COLOR,
        ranking_rect,
        2
    )

    # ランキング内容（後で実装）
    placeholder_text = small_font.render(
        "(Ranking content)",
        True,
        (150, 150, 150)
    )

    screen.blit(
        placeholder_text,
        (
            ranking_rect.x + 20,
            ranking_rect.y + 20
        )
    )

    # ========== "作成中" メッセージ ==========

    if show_coming_soon:
        # 半透明の背景
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # メッセージテキスト
        coming_soon_text = title_font.render(
            f"{coming_soon_game_name}は作成中です",
            True,
            TEXT_COLOR
        )

        text_rect = coming_soon_text.get_rect(
            center=(WIDTH // 2, HEIGHT // 2)
        )

        screen.blit(coming_soon_text, text_rect)

    # ==================================
    # 表示更新
    # ==================================

    pygame.display.flip()

pygame.quit()
