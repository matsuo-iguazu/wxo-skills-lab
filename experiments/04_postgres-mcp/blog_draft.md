# ブログ下書き: PostgreSQL MCP を WxO に繋いでみた

> **ステータス**: 執筆中（検証完了）
> **トーン**: あっさりめ・技術者向け・手順重視

---

## タイトル案

- 「WxO エージェントから PostgreSQL を自然言語で参照する — MCP Toolkit 接続手順」
- 「公式 MCP サーバーを watsonx Orchestrate のツールキットに登録してみた」

---

## 構成メモ

### 1. はじめに（2〜3 行）

- WxO エージェントから DB を参照したいユースケースはよくある
- MCP（Model Context Protocol）のサーバーを WxO toolkit として使えるか試した
- 「PCで Node.js が動くMCPサーバーが必要」という先入観が崩れた話

### 2. 使ったもの

- IBM watsonx Orchestrate（WxO）: IG 環境
- MCP サーバー: `@modelcontextprotocol/server-postgres`（公式 archived）
- DB: Supabase（クラウド PostgreSQL）

### 3. アーキテクチャ

```
ユーザー発話
  ↓
WxO エージェント（M_postgres_agent）
  ↓ MCP Toolkit 呼び出し（STDIO）
WxO クラウド内で npx が起動
  ↓  @modelcontextprotocol/server-postgres
Supabase / ローカル PostgreSQL
```

**重要: MCP サーバーは WxO クラウド上で動く**

WxO の MCP Toolkit（STDIO モード）は、`npx` や `python` コマンドを
**ユーザーの PC ではなく WxO クラウド（OpenShift コンテナ）上で**実行する。

エラーメッセージのパスが `/opt/app-root/lib64/python3.12/` であることからも確認できる。
これは以前の「MCPサーバーは手元のPCで動かす必要がある」という説明を覆す大きな発見だった。

### 4. 手順サマリー

1. Supabase にサンプルテーブル作成（`scripts/setup_supabase.sql`）
2. WxO Connections 定義（`connections/m-postgres-conn.yaml`）
3. toolkit YAML 作成 → `orchestrate connections import` → 認証情報を登録 → `orchestrate toolkits import`
4. agent YAML 作成 → `orchestrate agents import`
5. WxO チャットでテスト

### 5. ハマりポイント・気づき

今回の検証で遭遇した5つのハマりポイントを記録する。

---

#### ハマり① コマンド文字列がスペースで分割される問題

toolkit YAML の `command:` フィールドに文字列で書くと、WxO がスペース区切りで分割してしまう。

```yaml
# ❌ これはダメ（sh が -c の後の文字列を受け取れない）
command: "sh -c 'npx -y @modelcontextprotocol/server-postgres $DATABASE_URL'"

# ✅ JSON リスト形式で書く
command: '["sh", "-c", "npx -y @modelcontextprotocol/server-postgres $DATABASE_URL"]'
```

環境変数（`$DATABASE_URL`）を展開するためにシェル経由（`sh -c`）で起動する必要があり、
この形式が必要になる。

---

#### ハマり② `toolkits:` フィールドは `react` スタイルのエージェントで使えない

エージェント YAML に `toolkits: - m-postgres` と書いたところ：

```
Toolkits are only supported for experimental_customer_care style agents
```

`react` スタイル（や `default` スタイル）では `toolkits:` は使えず、
MCP ツールを `toolkit名:tool名` 形式で `tools:` に列挙する必要がある。

```yaml
# ❌ react スタイルでは使えない
toolkits:
  - m-postgres

# ✅ tools に toolkit名:tool名 形式で指定する
tools:
  - m-postgres:query
```

ツール名は toolkit インポート後に `orchestrate tools list` で確認できる。

---

#### ハマり③ エージェント名にハイフンは使えない

`M-postgres-agent` という名前でインポートしようとしたら：

```
Name must start with a letter and contain only alphanumeric characters and underscores
```

エージェント名はアルファベット・数字・アンダースコアのみ。ハイフン不可。
`M_postgres_agent` に変更して解決した。

（Toolkit 名や Connection 名はハイフン OK なので要注意）

---

#### ハマり④ Supabase の接続文字列は Session Pooler を使う

Supabase のデフォルト接続文字列（Direct connection）は IPv6 アドレスに解決されることがある。
WxO クラウドから IPv6 は到達不能で `ENETUNREACH` エラーになった。

```
# ❌ Direct connection（IPv6 の可能性がある）
postgresql://postgres:pass@db.xxxxx.supabase.co:5432/postgres

# ✅ Session Pooler（IPv4、aws-x-xx.pooler.supabase.com）
postgresql://postgres.xxxxx:pass@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres
```

Supabase ダッシュボードの「Connect」→「Session pooler」から取得。
ユーザー名が `postgres.{project-ref}` 形式になる点に注意。

---

#### ハマり⑤ toolkit インポート前に認証情報の登録が必要

`orchestrate toolkits import` を先にやったら失敗した。
WxO は toolkit インポート時に実際に MCP サーバーを起動してツール一覧を取得しにいくため、
**インポート前に `DATABASE_URL` が登録済みでないとサーバーが起動できない**。

手順：
1. `orchestrate connections import`（接続定義をインポート）
2. `orchestrate connections configure`（接続タイプを設定）
3. `orchestrate connections set-credentials`（`DATABASE_URL` を登録）
4. `orchestrate toolkits import`（ここで初めてサーバーが起動する）

`import-all.sh` に正しい順序を反映済み。

---

### 6. archived サーバーについて

- `query` ツール1本のみ（`SELECT` 専用、`BEGIN TRANSACTION READ ONLY` ハードコード）
- R/W が必要になったら `crystaldba/postgres-mcp` に乗り換え or 独自 FastMCP を検討
- 技術検証用途には十分
- archived なのでセキュリティアップデートは期待できない

### 7. 本格利用に向けて

今回の archived サーバーは `query` ツール1本（Text2SQL 方式）で、REST API との差は薄い。
MCP の本来の価値は**目的別ツールが複数あるとき**に出てくる。

次のステップとしては：

- **目的別ツールを設計する**: `get_products_by_category`、`get_low_stock_items` など
  → 独自 FastMCP サーバー（STDIO モードなら PC 不要）または `crystaldba/postgres-mcp` を採用
- **R/W が必要になったら**: `crystaldba/postgres-mcp`（Python、アクティブ維持）に乗り替え
- **接続先の切り替え**: `DATABASE_URL` を変更するだけで Supabase → ローカル Docker に切り替え可能

### 8. まとめ

- WxO の MCP Toolkit（STDIO）は **WxO クラウド上で** npx/python を実行する。手元に MCP サーバーは不要
- Supabase へは **Session Pooler URL（IPv4）** を使う
- toolkit YAML の `command:` は **JSON リスト形式** で書く
- `react` スタイルのエージェントは `tools: - toolkit名:tool名` 形式
- エージェント名は **アンダースコアのみ**（ハイフン不可）
- toolkit インポート前に **認証情報の登録が必須**

---

## 検証ログ（時系列メモ）

### 2026-04-02
- 方針策定: Track A（archived server）+ Supabase 先行
- SOP 作成完了
- WxO IG への全コンポーネント deploy 完了
- E2E テスト（テーブル一覧・全データ取得・価格フィルター）成功
- 5つのハマりポイントを記録

---

## スクリーンショット置き場

> ※ WxO チャット画面など、ブログに使えそうな画像をここにメモ

