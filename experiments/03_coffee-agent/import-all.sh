#!/usr/bin/env bash
# =============================================================================
# コーヒー給仕リクエスト受付エージェント - インポートスクリプト
# =============================================================================
# 前提条件:
#   1. venv がアクティベートされていること
#      source /home/matsuo/Downloads/wxo-skills-lab/.venv/bin/activate
#   2. WxO 環境が認証済みであること
#      orchestrate env activate IG
# =============================================================================

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "=== コーヒー給仕リクエスト受付エージェント インポート開始 ==="
echo ""

# Python ツールのインポート
echo "[1/2] Python ツールをインポート中..."
orchestrate tools import -k python -f "${SCRIPT_DIR}/tools/m_coffee_request_tools.py"

# エージェントのインポート
echo "[2/2] エージェントをインポート中..."
orchestrate agents import -f "${SCRIPT_DIR}/agents/M-coffee-request-agent.yaml"

echo ""
echo "=== インポート完了 ==="
echo ""
echo "動作確認:"
echo "  orchestrate chat start"
echo "  → エージェント 'M-coffee-request-agent' を選択"
echo "  → 「会議室Aにブラックコーヒーを2杯持ってきて」と入力"
