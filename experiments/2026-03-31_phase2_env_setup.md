# Phase 2 環境構築 検証記録

**日付**: 2026年3月31日
**目的**: WxO ADK MCP Server を Claude Code から使える状態にする

---

## 実施内容と結果

### ✅ ADK リポジトリ クローン

```bash
git clone https://github.com/IBM/ibm-watsonx-orchestrate-adk.git
```

- 問題なし
- `ibm-watsonx-orchestrate-adk/skills/` 以下に3つの SKILL.md を確認

---

### ✅ `.claude/skills/` への Skills 配置

```bash
cp -r ibm-watsonx-orchestrate-adk/skills/sop-builder .claude/skills/
cp -r ibm-watsonx-orchestrate-adk/skills/wxo-builder .claude/skills/
cp -r ibm-watsonx-orchestrate-adk/skills/customercare-mcp-builder .claude/skills/
```

- Claude Code が即座に認識
- `/sop-builder`, `/wxo-builder`, `/customercare-mcp-builder` が使用可能になった

---

### ✅ venv 作成

```bash
python3 -m venv .venv
source .venv/bin/activate
```

- Python 3.12.4
- `.gitignore` に `.venv/` 追加済み

---

### ⚠️ MCP Server インストール → fastmcp バージョン問題

```bash
pip install ibm-watsonx-orchestrate-mcp-server
# → fastmcp 2.14.6 が入り、Claude Code から failed になる
```

**症状**: Claude Code の `/mcp` で `wxo-mcp` が **failed**

**原因調査**:
1. まずトークン切れを疑ったが `orchestrate env activate IG` 後も改善せず
2. JSON-RPC を手動送信して確認 → `tools/list` で `ValueError: Circular reference detected` が発生してサーバーがクラッシュ
3. `fastmcp==2.10.6` にダウングレード → 今度は `TypeError: cannot specify both default and default_factory`（pydantic 2.12.x 非互換）
4. `fastmcp==2.13.3` で解決

```bash
pip install "fastmcp==2.13.3"
```

→ Claude Code で **Connected** になることを確認

---

### ✅ orchestrate CLI 動作確認

```bash
source .venv/bin/activate
orchestrate agents list
```

- WxO IG 環境のエージェント一覧が取得できることを確認
- 大量の `[DEBUG]` ログが出るが通信には影響なし

---

### ✅ MCP Inspector での動作確認

```bash
WXO_MCP_WORKING_DIRECTORY=$(pwd) fastmcp dev \
  .venv/lib/python3.12/site-packages/ibm_watsonx_orchestrate_mcp_server/server.py
```

- ターミナルのトークン付き URL でブラウザから接続
- デフォルト設定（`fastmcp` + Python ファイル）では `tools: []` になる
- Inspector UI の Command を実行ファイルのフルパスに変更して再接続 → ツール一覧表示
- `list_agents` ツールを実行 → WxO のエージェント一覧が返ることを確認

---

## わかったこと

1. **`fastmcp==2.13.3` 固定が必須**（2.14.x はバグ、2.10.x は pydantic 非互換）
2. **MCP Inspector の「Connected」は WxO 認証と無関係**（ツール実行時に初めて WxO に接続）
3. **`fastmcp dev` に Python ファイルを渡すと tools が空になる**（`_load_tools()` が呼ばれないため）
4. **`orchestrate` の DEBUG ログは stderr** なので MCP 通信（stdout）には影響しない

---

## 参照

- [docs/setup_notes.md](../docs/setup_notes.md) - 詳細なセットアップ手順・注意点
