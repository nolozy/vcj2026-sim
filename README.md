# VCJ 2026 Split2 Advance Stage シミュレーター

VCJ 2026 Split2 Advance Stage の進出確率をモンテカルロシミュレーション（10万回）で予測する Streamlit Web アプリです。

## 機能

- **試合結果入力**：Day ごとに勝者・MAPスコア・ラウンド数を入力
- **シミュレーション**：未消化の試合を 10万回シミュレーションして最終順位の確率を計算
- **ヒートマップ出力**：グループ A・B の最終順位パーセンテージを画像で表示・ダウンロード
- **公式タイブレーカー準拠**（11.7 条）
  - 2チーム：H2H勝利 → H2H MAP差 → H2H RND差 → 全体MAP差 → 全体RND差
  - 3チーム：H2H勝利 → (循環時) 全体MAP差 → 全体RND差
  - 4チーム以上：H2H勝利 → H2H MAP差 → H2H RND差 → 全体MAP差 → 全体RND差

## グループ構成

| Group A | Group B |
|---|---|
| REJECT | RIDDLE ORDER |
| SCARZ | IGZIST |
| AGELITE | WEC C |
| ALESTAR | KING GUY |
| REIGNITE FOXX | Murash Gaming |
| PARON | Kirihana Academy |

各グループ上位 **2チーム** がメインステージへ進出。

## ローカルで起動する

```bash
pip install -r requirements.txt
streamlit run app.py
```

ブラウザで `http://localhost:8501` を開いてください。

## Google Colab で起動する

`colab_runner.ipynb` をColabで開き、セルを順番に実行してください。  
ngrok の無料アカウント（[https://ngrok.com](https://ngrok.com)）があれば外部URLが発行されます。

## データの保存・共有

- 試合結果は `vcj2026_results.json` に保存されます
- サイドバーから JSON をダウンロード／アップロードして友達と共有できます
