from flask import Flask, render_template, request, jsonify, session
import os
import json
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# ==========================================
# パス設定
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_RECORDS_DIR = os.path.join(BASE_DIR, "user_records")

# user_records ディレクトリが存在しなければ作成
os.makedirs(USER_RECORDS_DIR, exist_ok=True)

# ==========================================
# ユーザーrecord管理
# ==========================================

def get_user_record_file(username):
    """ユーザーのrecordファイルパスを取得"""
    return os.path.join(USER_RECORDS_DIR, f"{username}.json")

def load_user_records(username):
    """ユーザーのrecordを読み込む"""
    record_file = get_user_record_file(username)
    
    if os.path.isfile(record_file):
        try:
            with open(record_file, "r") as f:
                return json.load(f)
        except:
            pass
    
    # デフォルト構造
    return {
        "username": username,
        "created_at": datetime.now().isoformat(),
        "games": {
            "built_to_scale2": {
                "best_miss": None
            },
            "terrible_ninja": {
                "best_miss": None
            }
        }
    }

def save_user_records(username, records):
    """ユーザーのrecordを保存"""
    record_file = get_user_record_file(username)
    
    with open(record_file, "w") as f:
        json.dump(records, f, indent=2)

# ==========================================
# ルート
# ==========================================

@app.route("/")
def index():
    """ログインページ"""
    return render_template("login.html")

@app.route("/launcher")
def launcher():
    """ゲームランチャー"""
    username = session.get("username")
    
    if not username:
        return render_template("login.html")
    
    # ユーザーのrecordを取得
    records = load_user_records(username)
    
    return render_template("launcher.html", 
                          username=username,
                          records=records)

@app.route("/game/built_to_scale2")
def built_to_scale2():
    """Built to Scale 2 ゲーム画面"""
    username = session.get("username")
    
    if not username:
        return render_template("login.html")
    
    return render_template("built_to_scale2.html", username=username)

# ==========================================
# API エンドポイント
# ==========================================

@app.route("/api/login", methods=["POST"])
def api_login():
    """ログイン処理"""
    data = request.json
    username = data.get("username", "").strip()
    
    if not username:
        return jsonify({"success": False, "message": "ユーザー名を入力してください"}), 400
    
    # ユーザー名に特殊文字が含まれていないかチェック
    if not all(c.isalnum() or c in "_-" for c in username):
        return jsonify({"success": False, "message": "ユーザー名は英数字、_、-のみ使用可能です"}), 400
    
    # セッションに保存
    session["username"] = username
    
    return jsonify({"success": True, "username": username})

@app.route("/api/logout", methods=["POST"])
def api_logout():
    """ログアウト処理"""
    session.clear()
    return jsonify({"success": True})

@app.route("/api/records/<game_name>", methods=["GET"])
def api_get_records(game_name):
    """ゲームのrecordを取得"""
    username = session.get("username")
    
    if not username:
        return jsonify({"success": False, "message": "ログインしてください"}), 401
    
    records = load_user_records(username)
    game_record = records.get("games", {}).get(game_name)
    
    if game_record is None:
        return jsonify({"success": False, "message": "ゲームが見つかりません"}), 404
    
    return jsonify({"success": True, "record": game_record})

@app.route("/api/records/<game_name>/save", methods=["POST"])
def api_save_record(game_name):
    """ゲームのrecordを保存"""
    username = session.get("username")
    
    if not username:
        return jsonify({"success": False, "message": "ログインしてください"}), 401
    
    data = request.json
    miss_count = data.get("miss_count")
    
    if miss_count is None:
        return jsonify({"success": False, "message": "miss_countが必要です"}), 400
    
    records = load_user_records(username)
    
    # ゲームレコードがなければ作成
    if "games" not in records:
        records["games"] = {}
    if game_name not in records["games"]:
        records["games"][game_name] = {}
    
    # ベストスコアを更新
    game_record = records["games"][game_name]
    best_miss = game_record.get("best_miss")
    
    updated = False
    if best_miss is None or miss_count < best_miss:
        game_record["best_miss"] = miss_count
        game_record["last_played"] = datetime.now().isoformat()
        updated = True
        save_user_records(username, records)
    
    return jsonify({
        "success": True,
        "updated": updated,
        "best_miss": game_record.get("best_miss")
    })

@app.route("/api/all_records", methods=["GET"])
def api_get_all_records():
    """全ゲームのrecordを取得"""
    username = session.get("username")
    
    if not username:
        return jsonify({"success": False, "message": "ログインしてください"}), 401
    
    records = load_user_records(username)
    
    return jsonify({"success": True, "records": records})

# ==========================================
# エラーハンドリング
# ==========================================

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

# ==========================================
# メイン
# ==========================================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
