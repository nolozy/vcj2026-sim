# VCJ 2026 Split2 Advance Stage シミュレーター

VCJ 2026 Split2 Advance Stage の進出確率をモンテカルロシミュレーション（10万回）で予測する Web アプリです。

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red)

---

## 動作画面

- **試合結果入力タブ**：勝者・MAPスコア・ラウンド数を入力して保存
- **シミュレーション結果タブ**：グループA・Bの最終順位確率をヒートマップで表示・PNG保存

---

## PC にインストールして動かす方法

### 1. Python をインストール（まだの人）

[https://www.python.org/downloads/](https://www.python.org/downloads/) から **Python 3.10 以上** をダウンロードしてインストール。

> ⚠️ インストール時に **「Add Python to PATH」にチェックを入れること！**

### 2. このリポジトリをダウンロード

右上の **「Code」→「Download ZIP」** でダウンロードして解凍する。

または Git がある場合：

```bash
git clone <このリポジトリのURL>
cd vcj2026-sim
```

### 3. 必要なライブラリをインストール

解凍したフォルダの中で **ターミナル（コマンドプロンプト / PowerShell）** を開き、以下を実行：

```bash
pip install -r requirements.txt
```

### 4. アプリを起動

```bash
streamlit run app.py
```

ブラウザが自動で開き `http://localhost:8501` が表示されます。

---

## 使い方

1. **「📝 試合結果入力」タブ** を開く
2. 試合ごとに勝者・MAPスコア・ラウンド数を入力して **「💾 結果を保存する」**
3. **「📊 シミュレーション結果」タブ** を開いて **「🚀 シミュレーション実行」** をクリック
4. ヒートマップが表示されたら **「📥 ヒートマップ画像をダウンロード」** で PNG 保存

> Day1 の結果はあらかじめ入力済みで変更不可です。

### 試合結果の共有

- サイドバーの **「💾 結果データをダウンロード (.json)」** で結果ファイルをエクスポート
- 友達に送って **「📤 結果データを読み込む」** でインポートすれば同じ状態で使えます

---

## Google Colab で動かす（PC にインストール不要）

Google アカウントがあれば PC に何もインストールせず使えます。

1. `colab_runner.ipynb` を Google Colab で開く
2. `app.py` を Colab にアップロード
3. セルを上から順番に実行
4. 表示された ngrok URL をブラウザで開く

> ngrok の無料アカウントが必要です → [https://ngrok.com](https://ngrok.com)

---

## 大会情報

| | Group A | Group B |
|---|---|---|
| チーム | REJECT / SCARZ / AGELITE / ALESTAR / REIGNITE FOXX / PARON | RIDDLE ORDER / IGZIST / WEC C / KING GUY / Murash Gaming / Kirihana Academy |
| 進出枠 | 上位 **2チーム** | 上位 **2チーム** |
| 形式 | 総当たり（BO3）| 総当たり（BO3）|

### タイブレーカー（VCJ 公式ルール 11.7 準拠）

| ケース | 適用順 |
|---|---|
| 2チーム同率 | H2H勝利 → H2H MAP差 → H2H RND差 → 全体MAP差 → 全体RND差 |
| 3チーム同率 | H2H勝利 → (循環時) 全体MAP差 → 全体RND差 |
| 4チーム以上 | H2H勝利 → H2H MAP差 → H2H RND差 → 全体MAP差 → 全体RND差 |
