# Rhythm Game Web - セットアップガイド

ウェブ版リズムゲームへようこそ！

## セットアップ手順

### 1. 必要なパッケージをインストール

```bash
pip install flask
```

### 2. 音声ファイルを配置

Built to Scale 2のBGM（music.mp3）を以下のディレクトリにコピーしてください：

```
RTG/
└── static/
    └── audio/
        └── built_to_scale2_music.mp3
```

### 3. サーバーを起動

```bash
cd c:\Users\pedro\Documents\src\RTG
python web_server.py
```

### 4. ブラウザでアクセス

ブラウザを開いて、以下のURLにアクセスしてください：

```
http://localhost:5000
```

## ディレクトリ構造

```
RTG/
├── web_server.py                 # Flaskサーバーメイン
├── templates/
│   ├── login.html               # ログインページ
│   ├── launcher.html            # ゲームランチャー
│   ├── built_to_scale2.html     # ゲーム画面
│   └── 404.html                 # エラーページ
├── static/
│   ├── css/
│   │   ├── style.css            # 共通スタイル
│   │   └── game.css             # ゲームスタイル
│   ├── js/
│   │   ├── game_data.js         # ゲームデータ
│   │   └── built_to_scale2.js   # メインゲームロジック
│   └── audio/
│       └── built_to_scale2_music.mp3
├── user_records/                # ユーザーのrecordファイル格納先
│   ├── user1.json
│   ├── user2.json
│   └── ...
└── Built_to_Scale2/            # デスクトップ版ゲーム
```

## 機能説明

### ユーザー管理
- ユーザー名でログイン（パスワード不要）
- ユーザーごとにrecordを保存
- `user_records/` フォルダに保存されます

### ゲーム
- **Built to Scale 2**：ウェブ版で完全実装
  - キーボード入力で判定
  - Perfect/Miss判定
  - スコア自動保存

### record管理
- 各ユーザーの最高記録（最小ミス数）を保存
- ゲーム終了時に自動比較・更新
- JSONフォーマットで保存

## APIエンドポイント

### 認証
- `POST /api/login` - ログイン
- `POST /api/logout` - ログアウト

### Record管理
- `GET /api/records/<game_name>` - 特定ゲームのrecord取得
- `POST /api/records/<game_name>/save` - record保存
- `GET /api/all_records` - 全ゲームのrecord取得

## デスクトップ版との互換性

デスクトップ版（PyGame）も並行して使用可能です：

```bash
# デスクトップ版スタート画面
python Start_screen/main.py

# デスクトップ版 Built to Scale 2
python Built_to_Scale2/main.py
```

## トラブルシューティング

### 音声が再生されない
- `static/audio/built_to_scale2_music.mp3` が存在することを確認
- ブラウザのコンソールでエラーを確認

### ポート5000が使用中の場合
```python
# web_server.py の最後を修正
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)  # 8000に変更
```

### record が保存されない
- `user_records/` フォルダが書き込み可能か確認
- ブラウザのコンソールでAPIエラーを確認

## 今後の機能追加

- Terrible Ninja のウェブ版実装
- ランキング画面の実装
- ユーザー認証の強化
- データベース対応
