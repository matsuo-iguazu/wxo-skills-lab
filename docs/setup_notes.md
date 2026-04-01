# WxO ADK MCP Server セットアップ注意点

**記録日**: 2026年3月31日
**環境**: Python 3.12.4 / Ubuntu (WSL2) / Claude Code VSCode Extension

---

## TL;DR

`pip install ibm-watsonx-orchestrate-mcp-server` のデフォルトインストールでは
Claude Code から `wxo-mcp` が **failed** になる。
`fastmcp` を `2.13.3` に固定することで解決する。

---

## 症状

1. `~/.claude.json` に `wxo-mcp` を設定
2. Claude Code を再起動
3. `/mcp` ステータスが `connected` にならず **failed** と表示される

---

## 原因

`ibm-watsonx-orchestrate-mcp-server==2.7.0` は `fastmcp~=2.10`（2.x系全般）を要求するが、
pip が最新の `fastmcp==2.14.6` をインストールする。
これが実際にはバグを含んでおり、`tools/list` の JSON-RPC レスポンス時に
Pydantic がシリアライズエラーを起こしてサーバーがクラッシュする。

```
ValueError: Circular reference detected (id repeated)
```

バージョンダウンして `fastmcp==2.10.6` を試みたが、
今度は pydantic 2.12.x との非互換で別のエラーが発生：

```
TypeError: cannot specify both default and default_factory
```

**動作確認済みの組み合わせ**:

| パッケージ | バージョン | 備考 |
|---|---|---|
| ibm-watsonx-orchestrate-mcp-server | 2.7.0 | |
| fastmcp | **2.13.3** | ← ここが重要 |
| mcp | 1.22.0 | fastmcp 2.13.3 が自動的に選択 |
| pydantic | 2.12.5 | |

---

## 解決手順

```bash
# 1. venv 作成 & アクティベート
python3 -m venv .venv
source .venv/bin/activate

# 2. MCP Server をインストール（この時点では fastmcp 2.14.6 が入る）
pip install ibm-watsonx-orchestrate-mcp-server

# 3. fastmcp を 2.13.3 に固定（★ これが必要）
pip install "fastmcp==2.13.3"

# 4. 動作確認
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' \
  | WXO_MCP_WORKING_DIRECTORY=$(pwd) .venv/bin/ibm-watsonx-orchestrate-mcp-server 2>/dev/null
# → JSON-RPC レスポンスが返れば OK
```

---

## requirements.txt（再現用）

```
ibm-watsonx-orchestrate-mcp-server==2.7.0
fastmcp==2.13.3
```

---

## Claude Code の MCP 設定

`~/.claude.json` の `mcpServers` に追加：

```json
"wxo-mcp": {
  "type": "stdio",
  "command": "/path/to/your/.venv/bin/ibm-watsonx-orchestrate-mcp-server",
  "args": [],
  "env": {
    "WXO_MCP_WORKING_DIRECTORY": "/path/to/your/project"
  }
}
```

---

## その他の注意点

### 認証トークンの有効期限

WxO の認証トークンは定期的に切れる。
MCP Server が接続できても、実際のツール呼び出し時にエラーになる場合は：

```bash
source .venv/bin/activate
orchestrate env activate <環境名>
```

で再認証してから Claude Code を再起動する。

### DEBUG ログが stderr に出る

`orchestrate` コマンド実行時に大量の `[DEBUG]` ログが stderr に出るが、
MCP の JSON-RPC 通信は stdout のみなので **通信自体は問題ない**。
気になる場合は `WXO_MCP_DEBUG=false` を env に追加する（デフォルトで false）。

---

---

## MCP Inspector での動作確認

### 起動方法

`fastmcp dev` を使う場合、**Python ファイルパスではなく実行ファイルを直接指定する**必要がある。

```bash
# NG: Python ファイルを指定すると tools: [] になる
fastmcp dev .venv/lib/python3.12/site-packages/ibm_watsonx_orchestrate_mcp_server/server.py

# OK: 実行ファイルを MCP Inspector の UI から直接指定する（下記参照）
```

#### 手順

```bash
# Inspector を起動（--no-banner で fastmcp 経由で起動）
WXO_MCP_WORKING_DIRECTORY=$(pwd) fastmcp dev \
  .venv/lib/python3.12/site-packages/ibm_watsonx_orchestrate_mcp_server/server.py
```

ターミナルに表示される URL（トークン付き）をブラウザで開く：
```
http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=<token>
```

### tools が空になる問題

`fastmcp dev <python_file>` はモジュールを **import するだけ** で、
ツールを登録する `start_server()` → `_load_tools()` が呼ばれない。
そのため `tools/list` のレスポンスが `tools: []` になる。

**解決策**: Inspector の UI 左側のフォームを書き換えて直接接続する。

| フィールド | 値 |
|---|---|
| Command | `.venv/bin/ibm-watsonx-orchestrate-mcp-server` のフルパス |
| Arguments | （空欄） |
| Environment Variables | `WXO_MCP_WORKING_DIRECTORY` = プロジェクトパス |

→ Disconnect → Connect で再接続するとツール一覧が表示される。

### 接続時の認証について

Inspector の「Connected」は **Inspector ↔ MCP Server プロセス間の接続**であり、
WxO への認証とは無関係。ツールを実際に実行した時に初めて WxO に接続する。

---

## 関連リンク

- [ibm-watsonx-orchestrate-adk GitHub](https://github.com/IBM/ibm-watsonx-orchestrate-adk)
- [ADK MCP Server ドキュメント](https://developer.watson-orchestrate.ibm.com/mcp_server/wxOmcp_overview)
- [fastmcp PyPI](https://pypi.org/project/fastmcp/)
