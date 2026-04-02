# SOP: PostgreSQL MCP Server を WxO ツールキットとして接続する

## 目的

Model Context Protocol（MCP）の PostgreSQL サーバーを IBM watsonx Orchestrate（WxO）のツールキットとして登録し、エージェントが自然言語で PostgreSQL データベースを参照できることを検証する。

## スコープ

- **操作範囲**: 読み取り専用（SELECT のみ）
- **MCP サーバー**: `@modelcontextprotocol/server-postgres`（公式 archived 版）
- **データベース**: Supabase（検証完了後、ローカル PostgreSQL に切り替え）
- **スコープ外**: INSERT / UPDATE / DELETE（将来必要になれば community 版に移行）

## 前提条件

| 項目 | 内容 |
|---|---|
| WxO 環境 | `IG` 環境がアクティブであること（`orchestrate env activate IG`） |
| Supabase | アカウント・プロジェクトが存在し、接続文字列（URI）が取得できること |
| Node.js | WSL 上で `npx` が実行できること |
| WxO CLI | `orchestrate` コマンドが使えること |

---

## 手順

### Phase 1: Supabase にサンプルデータを作成する

**目的**: MCP 経由のクエリを検証するためのテストテーブルを用意する。

1. Supabase ダッシュボードにログインする
2. 対象プロジェクトの **SQL Editor** を開く
3. 以下の SQL を実行してサンプルデータを作成する

```sql
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price INTEGER NOT NULL,
    category VARCHAR(50),
    stock INTEGER DEFAULT 0
);

INSERT INTO products (name, price, category, stock) VALUES
  ('ノートPC',    98000, 'PC',         15),
  ('マウス',       2500, 'peripheral',  50),
  ('モニター',    45000, 'display',      8),
  ('キーボード',   8000, 'peripheral',  30),
  ('USB ハブ',    3200, 'accessory',   25);
```

4. `SELECT * FROM products;` でデータが挿入されていることを確認する

**接続文字列の取得**:
- Project Settings → Database → Connection string (URI)
- 形式: `postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres`

---

### Phase 2: WxO ツールキット YAML を作成・インポートする

**目的**: archived PostgreSQL MCP サーバーを WxO のツールキットとして登録する。

1. `toolkits/m-postgres-toolkit.yaml` を作成する（本ディレクトリ参照）

```yaml
spec_version: v1
kind: mcp
name: m-postgres
description: PostgreSQL read-only query toolkit (via @modelcontextprotocol/server-postgres)
language: node
command: npx -y @modelcontextprotocol/server-postgres postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
tools: []
```

> **注意**: 接続文字列にパスワードが含まれるため、このファイルは Git に含めない（`.gitignore` に追加済みの `.env` と同様に管理すること）

2. WxO にインポートする

```bash
orchestrate toolkit import --file toolkits/m-postgres-toolkit.yaml
```

3. インポートが成功したことを確認する

```bash
orchestrate toolkit list
```

---

### Phase 3: WxO エージェントを作成・テストする

**目的**: MCP ツールキットを使うエージェントを作成し、自然言語でのDB参照を確認する。

1. `agents/M-postgres-agent.yaml` を作成する（本ディレクトリ参照）

```yaml
spec_version: v1
style: react
name: M-postgres-agent
description: PostgreSQL データベースを自然言語で参照するエージェント。products テーブルの内容を確認できる。
toolkits:
  - m-postgres
```

2. WxO にインポートする

```bash
orchestrate agent import --file agents/M-postgres-agent.yaml
```

3. WxO チャットでエンドツーエンドテストを実施する

| テスト発話 | 期待動作 |
|---|---|
| 「テーブル一覧を教えて」 | `query` ツールで `information_schema` を参照し、テーブル名を返す |
| 「products テーブルの内容を見せて」 | `SELECT * FROM products` を実行し、商品一覧を返す |
| 「価格が 10000 円以上の商品は？」 | 適切な WHERE 句を生成・実行して結果を返す |

---

### Phase 4: ローカル PostgreSQL に切り替える（Supabase 検証完了後）

**目的**: 接続先を Supabase からローカル Docker に変更し、同じ MCP・エージェントで動作することを確認する。

1. ローカル PostgreSQL を Docker で起動する

```bash
docker run -d --name pg-test \
  -e POSTGRES_PASSWORD=testpass \
  -e POSTGRES_DB=testdb \
  -p 5432:5432 postgres:16
```

2. サンプルデータを投入する

```bash
docker exec -i pg-test psql -U postgres testdb < scripts/setup_local_db.sql
```

3. `toolkits/m-postgres-toolkit.yaml` の接続文字列をローカル用に書き換える

```yaml
command: npx -y @modelcontextprotocol/server-postgres postgresql://postgres:testpass@localhost:5432/testdb
```

4. ツールキットを再インポートする

```bash
orchestrate toolkit import --file toolkits/m-postgres-toolkit.yaml
```

5. WxO チャットで Phase 3 と同じテストを実施し、同じ結果が返ることを確認する

---

## 判断基準（成功条件）

| 確認項目 | 成功基準 |
|---|---|
| ツールキット登録 | `orchestrate toolkit list` に `m-postgres` が表示される |
| エージェント動作 | 自然言語の問いかけに対してエージェントが `query` ツールを呼び出す |
| クエリ結果 | products テーブルのデータが正しく返される |
| ローカル切り替え | Supabase と同じ操作でローカル DB にも接続できる |

---

## 選択経緯メモ

- archived サーバーは `query` ツール（SELECT 専用）のみ。`BEGIN TRANSACTION READ ONLY` がハードコード。
- 将来 INSERT/UPDATE が必要になれば `crystaldba/postgres-mcp`（Python, R/W対応）に乗り換えるか、独自 FastMCP サーバーを構築する。
- 独自実装（FastMCP）は `.env` 変更のみで接続先を切り替えられる利点があるが、今回の技術検証スコープでは不要と判断した。
