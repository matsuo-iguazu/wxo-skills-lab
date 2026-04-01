#!/usr/bin/env bash
# =============================================================================
# 日経新聞 ITインパクトレポート エージェント - インポートスクリプト
# =============================================================================
# 前提条件:
#   1. venv がアクティベートされていること
#      source /home/matsuo/Downloads/wxo-skills-lab/.venv/bin/activate
#   2. WxO 環境が認証済みであること
#      orchestrate env activate IG
#      ※ "IG" は定義済み環境名。初回セットアップ時は以下で環境を定義・認証する:
#        orchestrate env activate -a <IBM_CLOUD_API_KEY> <環境名>
#        （環境名は任意: "IG", "prod", "dev" など）
#   3. Tavily Connection の認証情報が WxO UI で設定済みであること（type: team のため初回のみ管理者が設定）
# =============================================================================

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "=== 日経新聞 ITインパクトレポート エージェント インポート開始 ==="
echo ""

# コネクションのインポート
echo "[1/3] コネクション (Tavily) をインポート中..."
orchestrate connections import -f "${SCRIPT_DIR}/connections/tavily.yaml"

# Python ツールのインポート（--app-id で Tavily コネクションを紐付け）
echo "[2/3] Python ツールをインポート中..."
orchestrate tools import -k python -f "${SCRIPT_DIR}/tools/nikkei_search_tool.py" --app-id tavily

# エージェントのインポート
echo "[3/3] エージェントをインポート中..."
orchestrate agents import -f "${SCRIPT_DIR}/agents/nikkei_it_report_agent.yaml"

echo ""
echo "=== インポート完了 ==="
echo ""
echo "動作確認:"
echo "  orchestrate chat start"
echo "  → エージェント 'nikkei_it_report_agent' を選択"
echo "  → 「今日の日経ニュースをまとめて」と入力"
