"""
VCJ 2026 Split2 Advance Stage シミュレーション
- グループA・B それぞれ上位2チームがメインステージへ進出
- タイブレーク: 公式ルール 11.7 に準拠
  2チーム: H2H勝利 → H2H MAP差 → H2H RND差 → 全体MAP差 → 全体RND差
  3チーム: H2H勝利 → (循環時) 全体MAP差 → 全体RND差 → BO1
  4チーム以上: H2H勝利 → H2H MAP差 → H2H RND差 → 全体MAP差 → 全体RND差
- サーキットポイントなし
"""

import io
import streamlit as st
import pandas as pd
import json
import os
import random
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

try:
    import japanize_matplotlib
except ImportError:
    pass

# ============================================================
# 定数・スケジュール定義
# ============================================================

GROUPS = {
    'A': ['REJECT', 'SCARZ', 'AGELITE', 'ALESTAR', 'REIGNITE FOXX', 'PARON'],
    'B': ['RIDDLE ORDER', 'IGZIST', 'WEC C', 'KING GUY', 'Murash Gaming', 'Kirihana Academy'],
}

SCHEDULE = [
    # ----- Group A -----
    {'id': 'A-D1-1', 'group': 'A', 'day': 1, 'team1': 'REJECT',        'team2': 'PARON'},
    {'id': 'A-D1-2', 'group': 'A', 'day': 1, 'team1': 'AGELITE',       'team2': 'ALESTAR'},
    {'id': 'A-D1-3', 'group': 'A', 'day': 1, 'team1': 'SCARZ',         'team2': 'REIGNITE FOXX'},
    {'id': 'A-D2-1', 'group': 'A', 'day': 2, 'team1': 'REJECT',        'team2': 'ALESTAR'},
    {'id': 'A-D2-2', 'group': 'A', 'day': 2, 'team1': 'AGELITE',       'team2': 'SCARZ'},
    {'id': 'A-D2-3', 'group': 'A', 'day': 2, 'team1': 'REIGNITE FOXX', 'team2': 'PARON'},
    {'id': 'A-D2-4', 'group': 'A', 'day': 2, 'team1': 'REJECT',        'team2': 'AGELITE'},
    {'id': 'A-D2-5', 'group': 'A', 'day': 2, 'team1': 'ALESTAR',       'team2': 'REIGNITE FOXX'},
    {'id': 'A-D2-6', 'group': 'A', 'day': 2, 'team1': 'SCARZ',         'team2': 'PARON'},
    {'id': 'A-D3-1', 'group': 'A', 'day': 3, 'team1': 'REJECT',        'team2': 'SCARZ'},
    {'id': 'A-D3-2', 'group': 'A', 'day': 3, 'team1': 'ALESTAR',       'team2': 'PARON'},
    {'id': 'A-D3-3', 'group': 'A', 'day': 3, 'team1': 'AGELITE',       'team2': 'REIGNITE FOXX'},
    {'id': 'A-D3-4', 'group': 'A', 'day': 3, 'team1': 'REJECT',        'team2': 'REIGNITE FOXX'},
    {'id': 'A-D3-5', 'group': 'A', 'day': 3, 'team1': 'ALESTAR',       'team2': 'SCARZ'},
    {'id': 'A-D3-6', 'group': 'A', 'day': 3, 'team1': 'AGELITE',       'team2': 'PARON'},
    # ----- Group B -----
    {'id': 'B-D1-1', 'group': 'B', 'day': 1, 'team1': 'RIDDLE ORDER',     'team2': 'Kirihana Academy'},
    {'id': 'B-D1-2', 'group': 'B', 'day': 1, 'team1': 'IGZIST',           'team2': 'Murash Gaming'},
    {'id': 'B-D1-3', 'group': 'B', 'day': 1, 'team1': 'WEC C',            'team2': 'KING GUY'},
    {'id': 'B-D2-1', 'group': 'B', 'day': 2, 'team1': 'RIDDLE ORDER',     'team2': 'IGZIST'},
    {'id': 'B-D2-2', 'group': 'B', 'day': 2, 'team1': 'Murash Gaming',    'team2': 'KING GUY'},
    {'id': 'B-D2-3', 'group': 'B', 'day': 2, 'team1': 'WEC C',            'team2': 'Kirihana Academy'},
    {'id': 'B-D2-4', 'group': 'B', 'day': 2, 'team1': 'RIDDLE ORDER',     'team2': 'Murash Gaming'},
    {'id': 'B-D2-5', 'group': 'B', 'day': 2, 'team1': 'IGZIST',           'team2': 'WEC C'},
    {'id': 'B-D2-6', 'group': 'B', 'day': 2, 'team1': 'KING GUY',         'team2': 'Kirihana Academy'},
    {'id': 'B-D3-1', 'group': 'B', 'day': 3, 'team1': 'RIDDLE ORDER',     'team2': 'KING GUY'},
    {'id': 'B-D3-2', 'group': 'B', 'day': 3, 'team1': 'IGZIST',           'team2': 'Kirihana Academy'},
    {'id': 'B-D3-3', 'group': 'B', 'day': 3, 'team1': 'Murash Gaming',    'team2': 'WEC C'},
    {'id': 'B-D3-4', 'group': 'B', 'day': 3, 'team1': 'RIDDLE ORDER',     'team2': 'WEC C'},
    {'id': 'B-D3-5', 'group': 'B', 'day': 3, 'team1': 'IGZIST',           'team2': 'KING GUY'},
    {'id': 'B-D3-6', 'group': 'B', 'day': 3, 'team1': 'Murash Gaming',    'team2': 'Kirihana Academy'},
]

DAY1_RESULTS = {
    'A-D1-1': {'winner': 'REJECT',       'map_w': 2, 'map_l': 0, 'rnd_w': 26, 'rnd_l': 7},
    'A-D1-2': {'winner': 'AGELITE',      'map_w': 2, 'map_l': 0, 'rnd_w': 26, 'rnd_l': 19},
    'A-D1-3': {'winner': 'SCARZ',        'map_w': 2, 'map_l': 0, 'rnd_w': 26, 'rnd_l': 7},
    'B-D1-1': {'winner': 'RIDDLE ORDER', 'map_w': 2, 'map_l': 0, 'rnd_w': 26, 'rnd_l': 13},
    'B-D1-2': {'winner': 'IGZIST',       'map_w': 2, 'map_l': 0, 'rnd_w': 28, 'rnd_l': 23},
    'B-D1-3': {'winner': 'WEC C',        'map_w': 2, 'map_l': 1, 'rnd_w': 37, 'rnd_l': 37},
}

RESULTS_FILE = 'vcj2026_results.json'
N_ADVANCE = 2


# ============================================================
# 結果の保存・読み込み
# ============================================================

def load_results() -> dict:
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data.update(DAY1_RESULTS)
        return data
    return dict(DAY1_RESULTS)


def save_results(results: dict):
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


# ============================================================
# シミュレーションロジック
# ============================================================

def sim_one_map(is_winner: bool) -> int:
    """1マップのラウンド数（OT 15%）"""
    if random.random() < 0.15:
        return 14 if is_winner else 12
    return 13 if is_winner else random.randint(0, 11)


def sim_match() -> dict:
    """BO3 の試合結果をランダム生成（勝者視点）"""
    if random.random() < 0.5:  # 2-0
        rw = sim_one_map(True)  + sim_one_map(True)
        rl = sim_one_map(False) + sim_one_map(False)
        return {'map_w': 2, 'map_l': 0, 'rnd_w': rw, 'rnd_l': rl}
    else:  # 2-1
        rw = sim_one_map(True)  + sim_one_map(True)  + sim_one_map(False)
        rl = sim_one_map(False) + sim_one_map(False) + sim_one_map(True)
        return {'map_w': 2, 'map_l': 1, 'rnd_w': rw, 'rnd_l': rl}


def blank_stats(teams: list) -> dict:
    return {t: {'wins': 0, 'losses': 0, 'map_w': 0, 'map_l': 0,
                'rnd_w': 0, 'rnd_l': 0} for t in teams}


def blank_h2h(teams: list) -> dict:
    return {t1: {t2: 0 for t2 in teams if t1 != t2} for t1 in teams}


def blank_h2h_maps(teams: list) -> dict:
    """直接対決の MAP 勝敗: {t1: {t2: [map_w, map_l]}}"""
    return {t1: {t2: [0, 0] for t2 in teams if t1 != t2} for t1 in teams}


def blank_h2h_rounds(teams: list) -> dict:
    """直接対決の RND 勝敗: {t1: {t2: [rnd_w, rnd_l]}}"""
    return {t1: {t2: [0, 0] for t2 in teams if t1 != t2} for t1 in teams}


def apply_result(stats: dict, h2h: dict, h2h_maps: dict, h2h_rounds: dict,
                 winner: str, loser: str,
                 mw: int, ml: int, rw: int, rl: int):
    sw = stats[winner]
    sw['wins']  += 1; sw['map_w'] += mw; sw['map_l'] += ml
    sw['rnd_w'] += rw; sw['rnd_l'] += rl

    sl = stats[loser]
    sl['losses'] += 1; sl['map_w'] += ml; sl['map_l'] += mw
    sl['rnd_w']  += rl; sl['rnd_l'] += rw

    h2h[winner][loser] += 1

    h2h_maps[winner][loser][0] += mw
    h2h_maps[winner][loser][1] += ml
    h2h_maps[loser][winner][0] += ml
    h2h_maps[loser][winner][1] += mw

    h2h_rounds[winner][loser][0] += rw
    h2h_rounds[winner][loser][1] += rl
    h2h_rounds[loser][winner][0] += rl
    h2h_rounds[loser][winner][1] += rw


# ============================================================
# タイブレーカー（公式ルール 11.7 準拠）
# ============================================================

def _binary_split(tied: list, key_fn) -> tuple:
    """
    上位（最大値）グループ と 残りグループ に二分割する。
    分割できなければ (None, None) を返す。
    """
    vals   = {t: key_fn(t) for t in tied}
    max_v  = max(vals.values())
    upper  = [t for t in tied if vals[t] == max_v]
    lower  = [t for t in tied if vals[t] != max_v]
    if not lower:
        return None, None
    return upper, lower


def _split_and_resolve(tied, key_fn, stats, h2h, h2h_maps, h2h_rounds):
    """
    基準で二分割し、各サブグループを再帰的に解決する。
    戻り値: (result_list | None, did_split: bool)
    """
    upper, lower = _binary_split(tied, key_fn)
    if upper is None:
        return None, False
    return (
        _resolve_group(upper, stats, h2h, h2h_maps, h2h_rounds) +
        _resolve_group(lower, stats, h2h, h2h_maps, h2h_rounds)
    ), True


def _resolve_group(tied: list, stats, h2h, h2h_maps, h2h_rounds) -> list:
    """グループ人数に応じて適切な 11.7.x を呼び出す"""
    if len(tied) <= 1:
        return tied
    if len(tied) == 2:
        return _resolve_two(tied[0], tied[1], stats, h2h, h2h_maps, h2h_rounds)
    if len(tied) == 3:
        return _resolve_three(tied, stats, h2h, h2h_maps, h2h_rounds)
    return _resolve_four_plus(tied, stats, h2h, h2h_maps, h2h_rounds)


def _resolve_two(a: str, b: str, stats, h2h, h2h_maps, h2h_rounds) -> list:
    """11.7.1: 2チームタイブレーカー"""
    # (1) H2H 試合勝利
    d = h2h[a].get(b, 0) - h2h[b].get(a, 0)
    if d: return [a, b] if d > 0 else [b, a]
    # (2) H2H MAP差
    d = (h2h_maps[a][b][0] - h2h_maps[a][b][1]) - (h2h_maps[b][a][0] - h2h_maps[b][a][1])
    if d: return [a, b] if d > 0 else [b, a]
    # (3) H2H RND差
    d = (h2h_rounds[a][b][0] - h2h_rounds[a][b][1]) - (h2h_rounds[b][a][0] - h2h_rounds[b][a][1])
    if d: return [a, b] if d > 0 else [b, a]
    # (4) 全体 MAP差
    d = (stats[a]['map_w'] - stats[a]['map_l']) - (stats[b]['map_w'] - stats[b]['map_l'])
    if d: return [a, b] if d > 0 else [b, a]
    # (5) 全体 RND差
    d = (stats[a]['rnd_w'] - stats[a]['rnd_l']) - (stats[b]['rnd_w'] - stats[b]['rnd_l'])
    return [a, b] if d >= 0 else [b, a]


def _resolve_three(tied: list, stats, h2h, h2h_maps, h2h_rounds) -> list:
    """
    11.7.2: 3チームタイブレーカー
    (1) 3チーム間の直接対決 → 2勝チームが自動1位、残り2は2チームTBへ
        全員1-1（循環）→ (2)へ
    (2) 全体 MAP差
    (3) 全体 RND差
    (4) BO1（シミュレーション上はランダム）
    """
    # (1) H2H 勝利でバイナリ分割を試みる
    res, split = _split_and_resolve(
        tied,
        lambda t: sum(h2h[t].get(o, 0) for o in tied if o != t),
        stats, h2h, h2h_maps, h2h_rounds
    )
    if split:
        return res
    # 全員 1-1（循環）→ H2H MAP/RND はスキップして全体へ
    # (2) 全体 MAP差
    res, split = _split_and_resolve(
        tied, lambda t: stats[t]['map_w'] - stats[t]['map_l'],
        stats, h2h, h2h_maps, h2h_rounds
    )
    if split:
        return res
    # (3) 全体 RND差
    res, split = _split_and_resolve(
        tied, lambda t: stats[t]['rnd_w'] - stats[t]['rnd_l'],
        stats, h2h, h2h_maps, h2h_rounds
    )
    if split:
        return res
    # (4) BO1 → シミュレーション上はランダム
    return random.sample(tied, len(tied))


def _resolve_four_plus(tied: list, stats, h2h, h2h_maps, h2h_rounds) -> list:
    """
    11.7.3: 4チーム以上タイブレーカー
    (1) H2H 試合勝利
    (2) H2H MAP差
    (3) H2H RND差
    (4) 全体 MAP差
    (5) 全体 RND差
    (6-9) 相手ピックMAP系（未実装→ランダム）
    各ステップでバイナリ分割を適用し、分割できたら各サブグループを再帰解決。
    """
    criteria = [
        lambda t: sum(h2h[t].get(o, 0) for o in tied if o != t),
        lambda t: sum(h2h_maps[t][o][0] - h2h_maps[t][o][1] for o in tied if o != t),
        lambda t: sum(h2h_rounds[t][o][0] - h2h_rounds[t][o][1] for o in tied if o != t),
        lambda t: stats[t]['map_w'] - stats[t]['map_l'],
        lambda t: stats[t]['rnd_w'] - stats[t]['rnd_l'],
    ]
    for key_fn in criteria:
        res, split = _split_and_resolve(tied, key_fn, stats, h2h, h2h_maps, h2h_rounds)
        if split:
            return res
    # 6-9 は実装省略 → ランダム
    return random.sample(tied, len(tied))


def compute_standings(teams: list, stats: dict, h2h: dict,
                      h2h_maps: dict, h2h_rounds: dict) -> list:
    """チームリストを最終順位順に返す（1位が先頭）"""
    sorted_by_wins = sorted(teams, key=lambda t: stats[t]['wins'], reverse=True)
    result = []
    i = 0
    while i < len(sorted_by_wins):
        j = i + 1
        while j < len(sorted_by_wins) and \
              stats[sorted_by_wins[j]]['wins'] == stats[sorted_by_wins[i]]['wins']:
            j += 1
        tied = sorted_by_wins[i:j]
        result.extend(
            _resolve_group(tied, stats, h2h, h2h_maps, h2h_rounds)
            if len(tied) > 1 else tied
        )
        i = j
    return result


def run_simulation(match_results: dict, n_sims: int = 100_000) -> dict:
    all_pcts = {}

    for group_letter, teams in GROUPS.items():
        n = len(teams)
        rank_counts   = {t: [0] * n for t in teams}
        group_matches = [m for m in SCHEDULE if m['group'] == group_letter]

        for _ in range(n_sims):
            stats      = blank_stats(teams)
            h2h        = blank_h2h(teams)
            h2h_maps   = blank_h2h_maps(teams)
            h2h_rounds = blank_h2h_rounds(teams)

            for m in group_matches:
                mid = m['id']
                t1, t2 = m['team1'], m['team2']

                if mid in match_results:
                    res    = match_results[mid]
                    winner = res['winner']
                    loser  = t2 if winner == t1 else t1
                    mw, ml, rw, rl = res['map_w'], res['map_l'], res['rnd_w'], res['rnd_l']
                else:
                    sim    = sim_match()
                    winner, loser = (t1, t2) if random.random() < 0.5 else (t2, t1)
                    mw, ml, rw, rl = sim['map_w'], sim['map_l'], sim['rnd_w'], sim['rnd_l']

                apply_result(stats, h2h, h2h_maps, h2h_rounds,
                             winner, loser, mw, ml, rw, rl)

            ordered = compute_standings(teams, stats, h2h, h2h_maps, h2h_rounds)
            for rank, team in enumerate(ordered):
                rank_counts[team][rank] += 1

        all_pcts[group_letter] = {
            t: {r + 1: rank_counts[t][r] / n_sims * 100 for r in range(n)}
            for t in teams
        }

    return all_pcts


# ============================================================
# 現在の順位計算（確定済み試合のみ）
# ============================================================

def current_standings(group_letter: str, match_results: dict):
    teams      = GROUPS[group_letter]
    stats      = blank_stats(teams)
    h2h        = blank_h2h(teams)
    h2h_maps   = blank_h2h_maps(teams)
    h2h_rounds = blank_h2h_rounds(teams)

    for m in SCHEDULE:
        if m['group'] != group_letter or m['id'] not in match_results:
            continue
        res    = match_results[m['id']]
        winner = res['winner']
        loser  = m['team2'] if winner == m['team1'] else m['team1']
        apply_result(stats, h2h, h2h_maps, h2h_rounds, winner, loser,
                     res['map_w'], res['map_l'], res['rnd_w'], res['rnd_l'])

    # 途中経過の表示は公式に合わせて W→全体MAP差→全体RND差 の単純ソート
    # （H2Hタイブレーカーは全試合消化後にのみ適用するのが正式）
    ordered = sorted(
        teams,
        key=lambda t: (
            stats[t]['wins'],
            stats[t]['map_w'] - stats[t]['map_l'],
            stats[t]['rnd_w'] - stats[t]['rnd_l'],
        ),
        reverse=True,
    )
    return ordered, stats


# ============================================================
# ヒートマップ描画
# ============================================================

def draw_heatmap(all_pcts: dict, n_sims: int) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(20, 9))

    for gi, group_letter in enumerate(['A', 'B']):
        teams   = GROUPS[group_letter]
        pcts    = all_pcts[group_letter]
        n_ranks = len(teams)

        teams_sorted = sorted(
            teams,
            key=lambda t: sum(r * pcts[t].get(r, 0) / 100 for r in range(1, n_ranks + 1))
        )

        data = [[pcts[t].get(r, 0) for r in range(1, n_ranks + 1)]
                for t in teams_sorted]
        df = pd.DataFrame(data,
                          index=teams_sorted,
                          columns=[f"#{r}" for r in range(1, n_ranks + 1)])

        ax = axes[gi]
        sns.heatmap(df, annot=True, fmt=".1f", cmap="YlGnBu",
                    ax=ax, cbar_kws={'label': 'Percentage (%)'},
                    linewidths=0.5, square=True,
                    annot_kws={'size': 12})

        ax.axvline(x=N_ADVANCE, color='crimson', linewidth=2.5, linestyle='--')
        ax.text(N_ADVANCE / 2, -0.4, 'Advance',
                color='crimson', ha='center', fontsize=11, fontweight='bold',
                transform=ax.get_xaxis_transform())
        ax.text(N_ADVANCE + (n_ranks - N_ADVANCE) / 2, -0.4, 'Eliminated',
                color='gray', ha='center', fontsize=11,
                transform=ax.get_xaxis_transform())

        ax.set_title(f"Group {group_letter} - Final Standings % (n={n_sims:,})",
                     fontsize=14, pad=16)
        ax.set_xlabel("Final Rank", fontsize=12, labelpad=8)
        ax.set_ylabel("")
        ax.tick_params(axis='y', rotation=0)

    plt.tight_layout(pad=4)
    return fig


# ============================================================
# Streamlit アプリ本体
# ============================================================

def main():
    st.set_page_config(
        page_title="VCJ 2026 Split2 Advance Stage Sim",
        layout="wide",
        page_icon="🎮",
    )

    st.title("🎮 VCJ 2026 Split2 Advance Stage シミュレーション")
    st.caption(
        "各グループ上位2チームがメインステージへ進出 | "
        "タイブレーク: 公式 11.7 準拠（2チーム/3チーム/4チーム以上で異なる手順）"
    )

    with st.sidebar:
        st.header("⚙️ 設定")
        n_sims = st.selectbox(
            "シミュレーション回数",
            [10_000, 50_000, 100_000],
            index=2,
            format_func=lambda x: f"{x:,} 回",
        )

        st.divider()
        st.header("📂 データ管理")

        results = load_results()

        if st.button("🔄 Day1 のみにリセット", use_container_width=True):
            save_results(dict(DAY1_RESULTS))
            st.session_state.pop('sim_results', None)
            st.rerun()

        st.download_button(
            "💾 結果データをダウンロード (.json)",
            data=json.dumps(results, ensure_ascii=False, indent=2),
            file_name="vcj2026_results.json",
            mime="application/json",
            use_container_width=True,
        )

        uploaded = st.file_uploader("📤 結果データを読み込む (.json)", type=['json'])
        if uploaded:
            new_res = json.load(uploaded)
            new_res.update(DAY1_RESULTS)
            save_results(new_res)
            st.session_state.pop('sim_results', None)
            st.rerun()

        st.divider()
        st.markdown("""
**Colab での起動方法:**
```python
!pip install streamlit pyngrok japanize-matplotlib
import subprocess, threading
def _run():
    subprocess.run(['streamlit','run','app.py',
                    '--server.port','8501','--server.headless','true'])
threading.Thread(target=_run, daemon=True).start()

from pyngrok import ngrok
url = ngrok.connect(8501)
print(url)
```
        """)

    tab_input, tab_sim = st.tabs(["📝 試合結果入力", "📊 シミュレーション結果"])

    # ======================================================
    # TAB 1 : 試合結果入力
    # ======================================================
    with tab_input:
        results = load_results()

        with st.form("results_form", border=True):
            new_inputs: dict = {}

            for group_letter in ['A', 'B']:
                st.subheader(f"グループ {group_letter}")
                group_matches = [m for m in SCHEDULE if m['group'] == group_letter]

                for day in [1, 2, 3]:
                    day_matches = [m for m in group_matches if m['day'] == day]
                    is_day1 = day == 1

                    with st.expander(
                        f"Day {day}  {'（確定済み・変更不可）' if is_day1 else ''}",
                        expanded=not is_day1
                    ):
                        hc = st.columns([3, 2, 1.5, 1.2, 1.2])
                        hc[0].markdown("**試合**")
                        hc[1].markdown("**勝者**")
                        hc[2].markdown("**MAPスコア**")
                        hc[3].markdown("**勝側RND**")
                        hc[4].markdown("**敗側RND**")

                        for m in day_matches:
                            mid = m['id']
                            t1, t2 = m['team1'], m['team2']
                            existing = results.get(mid, {})
                            done = mid in results

                            cols = st.columns([3, 2, 1.5, 1.2, 1.2])

                            status_icon = "✅" if done else "⏳"
                            cols[0].markdown(f"{status_icon} **{t1}**  vs  **{t2}**")

                            winner_opts  = ['---', t1, t2]
                            curr_w       = existing.get('winner', '---')
                            curr_w_idx   = winner_opts.index(curr_w) if curr_w in winner_opts else 0
                            winner = cols[1].selectbox(
                                "勝者", winner_opts, index=curr_w_idx,
                                key=f"w_{mid}", disabled=is_day1,
                                label_visibility='collapsed'
                            )

                            score_opts  = ['2-0', '2-1']
                            curr_score  = f"{existing.get('map_w',2)}-{existing.get('map_l',0)}"
                            curr_s_idx  = score_opts.index(curr_score) if curr_score in score_opts else 0
                            score = cols[2].selectbox(
                                "スコア", score_opts, index=curr_s_idx,
                                key=f"s_{mid}", disabled=is_day1,
                                label_visibility='collapsed'
                            )

                            rw = cols[3].number_input(
                                "勝RND", min_value=0, max_value=300,
                                value=int(existing.get('rnd_w', 26)),
                                key=f"rw_{mid}", disabled=is_day1,
                                label_visibility='collapsed'
                            )
                            rl = cols[4].number_input(
                                "敗RND", min_value=0, max_value=300,
                                value=int(existing.get('rnd_l', 0)),
                                key=f"rl_{mid}", disabled=is_day1,
                                label_visibility='collapsed'
                            )

                            new_inputs[mid] = {
                                'winner': winner, 'score': score,
                                'rnd_w': rw, 'rnd_l': rl, 'is_day1': is_day1
                            }

            st.divider()
            submitted = st.form_submit_button(
                "💾  結果を保存する", type="primary", use_container_width=True
            )

        if submitted:
            for mid, inp in new_inputs.items():
                if inp['is_day1']:
                    continue
                if inp['winner'] == '---':
                    results.pop(mid, None)
                else:
                    mw, ml = (2, 0) if inp['score'] == '2-0' else (2, 1)
                    results[mid] = {
                        'winner': inp['winner'],
                        'map_w': mw, 'map_l': ml,
                        'rnd_w': int(inp['rnd_w']),
                        'rnd_l': int(inp['rnd_l']),
                    }
            save_results(results)
            st.session_state.pop('sim_results', None)
            st.success("✅ 保存しました！シミュレーションタブで再実行してください。")
            st.rerun()

        st.subheader("📋 現在の順位表（確定済み試合のみ）")
        results = load_results()
        played_total = sum(1 for m in SCHEDULE if m['id'] in results)
        st.caption(f"試合済み: {played_total} / {len(SCHEDULE)}")

        gcols = st.columns(2)
        for gi, group_letter in enumerate(['A', 'B']):
            ordered, stats = current_standings(group_letter, results)
            with gcols[gi]:
                st.markdown(f"**グループ {group_letter}**")
                rows = []
                for rank, t in enumerate(ordered, 1):
                    s = stats[t]
                    adv = "✅ 進出圏" if rank <= N_ADVANCE else "❌"
                    rows.append({
                        '順位': rank, 'チーム': t,
                        'W': s['wins'], 'L': s['losses'],
                        'MAP': f"{s['map_w']}/{s['map_l']}",
                        'RND差': s['rnd_w'] - s['rnd_l'],
                        '状況': adv,
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ======================================================
    # TAB 2 : シミュレーション結果
    # ======================================================
    with tab_sim:
        results   = load_results()
        played    = sum(1 for m in SCHEDULE if m['id'] in results)
        remaining = len(SCHEDULE) - played

        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("試合済み", f"{played} / {len(SCHEDULE)}")
        mc2.metric("残り試合数（シミュ対象）", remaining)
        mc3.metric("シミュレーション回数", f"{n_sims:,}")

        run_btn = st.button(
            "🚀  シミュレーション実行",
            type="primary",
            use_container_width=True,
        )

        if run_btn:
            with st.spinner(f"シミュレーション中… {n_sims:,}回 × 2グループ　しばらくお待ちください"):
                all_pcts = run_simulation(results, n_sims=n_sims)
            st.session_state['sim_results'] = all_pcts
            st.session_state['sim_n_sims']  = n_sims
            st.success("✅ 完了！")

        if 'sim_results' not in st.session_state:
            st.info("「シミュレーション実行」ボタンを押してください。")
            return

        all_pcts = st.session_state['sim_results']
        sim_n    = st.session_state.get('sim_n_sims', n_sims)

        st.subheader("📊 最終順位パーセンテージ（ヒートマップ）")
        fig = draw_heatmap(all_pcts, sim_n)
        st.pyplot(fig)

        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        st.download_button(
            "📥 ヒートマップ画像をダウンロード (PNG)",
            data=buf,
            file_name="vcj2026_sim_heatmap.png",
            mime="image/png",
            use_container_width=True,
        )
        plt.close(fig)

        st.subheader("🏆 進出確率サマリー")
        rows = []
        for group_letter in ['A', 'B']:
            teams   = GROUPS[group_letter]
            pcts    = all_pcts[group_letter]
            n_ranks = len(teams)
            sorted_teams = sorted(
                teams,
                key=lambda t: sum(r * pcts[t].get(r, 0) / 100 for r in range(1, n_ranks + 1))
            )
            for t in sorted_teams:
                adv_pct   = sum(pcts[t].get(r, 0) for r in range(1, N_ADVANCE + 1))
                breakdown = "  /  ".join(
                    f"{r}位: {pcts[t].get(r, 0):.1f}%"
                    for r in range(1, n_ranks + 1)
                    if pcts[t].get(r, 0) > 0
                )
                rows.append({
                    'G': group_letter, 'チーム': t,
                    '進出確率': f"{adv_pct:.1f}%",
                    '順位内訳': breakdown,
                })

        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.subheader("📈 グループ別 詳細順位表")
        dcols = st.columns(2)
        for gi, group_letter in enumerate(['A', 'B']):
            teams   = GROUPS[group_letter]
            pcts    = all_pcts[group_letter]
            n_ranks = len(teams)
            sorted_teams = sorted(
                teams,
                key=lambda t: sum(r * pcts[t].get(r, 0) / 100 for r in range(1, n_ranks + 1))
            )
            with dcols[gi]:
                st.markdown(f"**グループ {group_letter}**")
                detail_rows = []
                for t in sorted_teams:
                    adv = sum(pcts[t].get(r, 0) for r in range(1, N_ADVANCE + 1))
                    row = {'チーム': t, '進出確率': f"{adv:.1f}%"}
                    for r in range(1, n_ranks + 1):
                        row[f"{r}位"] = f"{pcts[t].get(r, 0):.1f}%"
                    detail_rows.append(row)
                st.dataframe(pd.DataFrame(detail_rows),
                             use_container_width=True, hide_index=True)


if __name__ == '__main__':
    main()
