# PostgreSQL MCP ツールキット接続検証 - SOP

**Document Type**: SOP
**Version**: 1.1
**Date**: 2026-04-02
**Author**: matsuo（イグアス）
**Source**: draft_sop.md（本ディレクトリ内）
**Status**: Draft

---

## Document Control

**Approvers**:
- Business Owner: TBD
- Process Owner: matsuo（イグアス）
- Compliance: N/A（技術検証用途）

**Review Cycle**: 検証完了時に見直し
**Next Review Date**: 検証完了後

---

## 1. Executive Summary

- **Procedure Name**: PostgreSQL MCP ツールキットを WxO エージェントに接続する手順
- **Business Problem**: IBM watsonx Orchestrate（WxO）のエージェントは、標準ライブラリ以外のパッケージを利用できないため、PostgreSQL に直接接続するネイティブツールを作成できない。Model Context Protocol（MCP）を活用することで、外部サーバー経由での DB 参照が可能になるかを検証する必要がある。
- **Business Objective**: WxO エージェントが自然言語の問いかけに応じて PostgreSQL データベースの内容を参照・回答できることを確認する。
- **Scope**:
  - 対象: 読み取り専用操作（SELECT のみ）
  - データベース: Supabase（クラウド）→ローカル Docker PostgreSQL の順に検証
  - MCP サーバー: `@modelcontextprotocol/server-postgres`（公式 archived 版）
  - 対象外: INSERT / UPDATE / DELETE 操作
- **Key Benefits**:
  1. WxO ネイティブツールの制約を MCP で回避できることを確認できる
  2. 接続文字列の変更だけでクラウド DB とローカル DB を切り替えられることを確認できる
  3. 将来の本格利用（目的別ツール設計・R/W 対応）に向けた技術基盤を得られる
- **Stakeholders**: matsuo（実施者）、イグアス技術チーム（知見共有先）
- **Success Criteria**: WxO チャット上でエージェントが自然言語の問いかけに応じて products テーブルの内容を正しく返すこと

---

## 2. Business Process Flow Diagram

```mermaid
flowchart TD
    Start([開始]):::start --> P1[Supabase に\nサンプルデータ作成]:::step
    P1 --> P2[MCP ツールキット YAML 作成\n+ WxO にインポート]:::step
    P2 --> P3[WxO エージェント作成\n+ インポート]:::step
    P3 --> P4[WxO チャットで\nE2E テスト実施]:::step
    P4 --> D1{テスト\n合格？}:::decision
    D1 -->|Yes| P5[Supabase 検証完了]:::step
    D1 -->|No| E1[問題を記録・調査]:::error
    E1 --> P4
    P5 --> D2{ローカル切り替え\n検証を実施する？}:::decision
    D2 -->|Yes| P6[Connections にローカル URL を登録\n+ TCP トンネル起動]:::step
    P6 --> P7[同一テストを\n再実施]:::step
    P7 --> D3{テスト\n合格？}:::decision
    D3 -->|Yes| End([完了]):::end
    D3 -->|No| E2[問題を記録・調査]:::error
    E2 --> P7
    D2 -->|No| End

    classDef start fill:#4CAF50,color:#fff
    classDef end fill:#f44336,color:#fff
    classDef decision fill:#FFC107,color:#000
    classDef step fill:#fff,stroke:#333
    classDef error fill:#ffcccc,stroke:#f44336
```

**凡例**:
- 緑の角丸: 開始
- 赤の角丸: 終了
- 黄色のひし形: 判断・分岐
- 白の四角: 処理ステップ
- 薄赤の四角: エラー対応

---

## 3. Business Context

### 3.1 Problem Statement

WxO のネイティブツール（Python）は実行環境の制約により、`psycopg2` などの外部パッケージが使用できない。そのため、Python コード内で直接 PostgreSQL に接続するツールは作成できない。この制約を回避し、WxO エージェントが DB の情報を参照するには、外部の MCP サーバーを WxO ツールキットとして登録する方法が有効かどうかを確認する必要がある。

### 3.2 Current State

- WxO ネイティブツールでの DB 直接接続: 不可（標準ライブラリのみ）
- DB 参照の現実的な手段: REST API を介した間接的な呼び出しが必要
- MCP ツールキットとして PostgreSQL サーバーを登録する前例: 本 WxO 環境では未検証

### 3.3 Desired Future State

- WxO エージェントが MCP ツールキット経由で PostgreSQL を参照できる
- Supabase（クラウド）・ローカル Docker の両方で同じ手順が機能することを確認済み
- 将来の本格利用（業務データ参照エージェント）への技術基盤が整う

---

## 4. Procedure Overview

### 4.1 Purpose and Scope

- **Primary Purpose**: WxO エージェントから MCP 経由で PostgreSQL に接続できることを技術検証する
- **In Scope**: Supabase への読み取り接続、ローカル PostgreSQL への切り替え確認
- **Out of Scope**: INSERT / UPDATE / DELETE、本番データの使用、セキュリティ審査
- **Dependencies**: WxO IG 環境が有効であること、Supabase プロジェクトが存在すること

### 4.2 Roles and Responsibilities

| ロール | 責務 |
|---|---|
| 実施者（matsuo） | 全手順の実行、テスト、結果記録 |
| WxO 環境 | ツールキット・エージェントのホスティング |
| Supabase | PostgreSQL データベースの提供 |

### 4.3 Frequency and Timing

- **Trigger**: 本手順は技術検証として1回実施する
- **Frequency**: 単発（検証目的）
- **Business Hours**: 制約なし

---

## 5. Data Requirements

### 5.1 Input Data

**ユーザー発話（自然言語クエリ）**:
- **Description**: エージェントへの問いかけ（「products テーブルの内容を見せて」など）
- **Source**: WxO チャット画面のユーザー入力
- **Format**: 自然言語テキスト
- **Required**: Yes

**データベース接続文字列**:
- **Description**: PostgreSQL への接続情報（ホスト・ポート・DB 名・認証情報）
- **Source**: Supabase ダッシュボード（Project Settings → Database → URI）
- **Format**: `postgresql://user:password@host:port/dbname`
- **Required**: Yes
- **Note**: パスワードを含むため Git 管理対象外

### 5.2 Data Used During Procedure

**products テーブル**:
- **Description**: 検証用サンプル商品データ（5件）
- **Purpose**: MCP 経由のクエリ結果を目視確認するための参照データ
- **Source System**: Supabase / ローカル PostgreSQL
- **Columns**: id, name, price, category, stock

**PostgreSQL スキーマ情報**:
- **Description**: テーブル名・カラム名・型情報
- **Purpose**: LLM が SQL を生成するために参照する（MCP Resources 経由で自動取得）
- **Source System**: PostgreSQL の information_schema

### 5.3 Output Data

**クエリ結果**:
- **Description**: SELECT 実行結果の行データ
- **Purpose**: エージェントがユーザーへの回答を生成するために使用
- **Destination**: WxO チャット画面（ユーザーへの応答として表示）
- **Format**: テキスト（エージェントが整形して返答）

---

## 6. Integration Points

**Integration 1: Supabase（PostgreSQL クラウドサービス）**
- **Purpose**: 検証用 PostgreSQL データベースの提供
- **What We Send**: SQL クエリ（SELECT 文）
- **What We Receive**: クエリ結果（行データ）
- **Timing**: WxO エージェントがクエリを実行するたびに呼び出される
- **Dependency**: Supabase プロジェクトが稼働中であること
- **Business Owner**: matsuo（イグアス）

**Integration 2: `@modelcontextprotocol/server-postgres`（MCP サーバー）**
- **Purpose**: WxO と PostgreSQL の間のプロトコル変換
- **What We Send**: 接続文字列（環境変数 `DATABASE_URL` として WxO Connections 経由で注入）
- **What We Receive**: `query` ツール（SELECT 専用）とテーブルスキーマ情報（Resources）
- **Transport**: STDIO（WxO クラウド上で `npx` により起動）
- **実行場所**: **WxO クラウドインフラ**（ローカル PC ではない）。WxO ドキュメントに明記。
- **Note**: アーカイブ済みリポジトリ。メンテナンスは終了しているが機能は完結している。

**Integration 3: IBM watsonx Orchestrate（WxO）**
- **Purpose**: エージェントのホスティングとユーザーとの対話
- **What We Send**: ツールキット定義 YAML、エージェント定義 YAML
- **What We Receive**: エージェントが利用可能な状態
- **Timing**: インポート操作時（事前設定）
- **Dependency**: IG 環境がアクティブであること

---

## 7. Business Procedure Steps

**Step 1: Supabase にサンプルデータを作成する**
- **What Happens**: 検証用の products テーブルを Supabase に作成し、5件のサンプルデータを投入する
- **Who Does It**: 実施者（matsuo）
- **Why**: MCP 経由のクエリ結果を目視確認するための参照データを用意する
- **Inputs**: Supabase プロジェクトへのアクセス権、SQL スクリプト
- **Outputs**: Supabase 上に products テーブルと 5 件のデータが存在する状態
- **Success Criteria**: `SELECT * FROM products` で 5 件のデータが返ること

**Step 2: WxO Connection に接続文字列を登録する**
- **What Happens**: Supabase の接続文字列を WxO のセキュアストレージ（Connections）に登録する。YAML にパスワードを書かずに済む。
- **Who Does It**: 実施者（matsuo）
- **Why**: MCP サーバープロセス（WxO クラウド上）が環境変数 `DATABASE_URL` として接続文字列を受け取るため
- **Inputs**: Supabase 接続文字列
- **Outputs**: WxO に `m-postgres-conn` 接続が登録された状態
- **Connection Type**: `key_value`（任意のキー名を環境変数として MCP サーバープロセスに渡す汎用型。`DATABASE_URL` キーが環境変数 `$DATABASE_URL` としてサーバーに注入される）
- **Command**:
  ```bash
  orchestrate connections add -a m-postgres-conn
  for env in draft live; do
      orchestrate connections configure -a m-postgres-conn --env $env --type team --kind key_value
      orchestrate connections set-credentials -a m-postgres-conn --env $env \
        -e "DATABASE_URL=postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres"
  done
  ```

**Step 3: MCP ツールキット YAML を作成・WxO にインポートする**
- **What Happens**: 接続文字列を含まない YAML を作成し、WxO CLI でインポートする
- **Who Does It**: 実施者（matsuo）
- **Why**: WxO エージェントがこのツールキットを参照できるようにするため
- **Inputs**: `toolkits/m-postgres-toolkit.yaml`（Git 管理可能）
- **Outputs**: WxO 上に `m-postgres` ツールキットが登録された状態
- **YAML 内容**:
  ```yaml
  spec_version: v1
  kind: mcp
  name: m-postgres
  description: PostgreSQL read-only query toolkit
  command: "sh -c 'npx -y @modelcontextprotocol/server-postgres $DATABASE_URL'"
  connections:
    - m-postgres-conn
  tools: []
  ```
- **Success Criteria**: `orchestrate toolkit list` に `m-postgres` が表示されること

**Step 4: WxO エージェントを作成・インポートする**
- **What Happens**: `m-postgres` ツールキットを使用する WxO エージェントを YAML で定義し、インポートする
- **Who Does It**: 実施者（matsuo）
- **Why**: ユーザーの自然言語入力を受け取り、ツールキットを呼び出す役割が必要
- **Inputs**: `agents/M-postgres-agent.yaml`
- **Outputs**: WxO 上に `M-postgres-agent` が登録された状態
- **Success Criteria**: WxO チャット画面にエージェントが表示されること

**Step 5: WxO チャットでエンドツーエンドテストを実施する**
- **What Happens**: 3種類の自然言語でエージェントに問いかけ、適切なクエリが実行されて結果が返ることを確認する
- **Who Does It**: 実施者（matsuo）
- **Why**: MCP ツールキットが実際に機能することを実証するため
- **Inputs**: テスト発話（下表参照）
- **Outputs**: 各問いかけに対する正しい回答、検証ログへの記録
- **Success Criteria**: 下記「判断基準」を参照

| テスト発話 | 期待動作 |
|---|---|
| 「テーブル一覧を教えて」 | information_schema を参照しテーブル名を返す |
| 「products テーブルの内容を見せて」 | 全 5 件のデータを返す |
| 「価格が 10000 円以上の商品は？」 | WHERE 句を自動生成し条件に合う商品を返す |

**Step 6: ローカル PostgreSQL に切り替える（Supabase 検証完了後）**
- **What Happens**: ① Docker で PostgreSQL を起動、② TCP トンネルで外部公開、③ WxO Connections の URL を更新する。YAML 変更・再インポートは不要。
- **Who Does It**: 実施者（matsuo）
- **Why**: クラウド DB とローカル DB で同一手順が機能することを確認するため
- **Why TCP トンネルが必要か**: MCP サーバーは WxO クラウド上で動作するため、`localhost:5432`（WSL）には直接到達できない
- **Inputs**: Docker、cloudflared（TCP トンネル）
- **Command**:
  ```bash
  # 1. Docker で PostgreSQL 起動
  docker run -d --name pg-test \
    -e POSTGRES_PASSWORD=testpass -e POSTGRES_DB=testdb \
    -p 5432:5432 postgres:16

  # 2. TCP トンネルで 5432 を公開（アカウント不要）
  cloudflared access tcp --hostname tcp.XXXX.trycloudflare.com --url localhost:5432
  # → 発行された tcp.XXXX.trycloudflare.com を控える

  # 3. Connections の URL だけ更新（YAML・再インポート不要）
  orchestrate connections set-credentials -a m-postgres-conn --env draft \
    -e "DATABASE_URL=postgresql://postgres:testpass@tcp.XXXX.trycloudflare.com:5432/testdb"
  ```
- **Outputs**: ローカル環境での同一テスト結果
- **Success Criteria**: Step 5 と同じ結果が得られること

---

## 8. Decision Points

**Decision 1: Supabase テストは合格したか**
- **Question Being Answered**: WxO エージェントが MCP 経由で Supabase に接続し、正しいクエリ結果を返せているか
- **Who Decides**: 実施者（matsuo）が目視確認
- **Decision Criteria**: 3つのテスト発話すべてに対して期待通りの回答が返ること
- **Possible Outcomes**:
  - Yes → Supabase 検証完了。ローカル切り替えに進む
  - No → エラー内容を `blog_draft.md` の検証ログに記録し、原因を調査する
- **Impact**: 合格しなければローカル切り替えには進まない

**Decision 2: ローカル切り替えを実施するか**
- **Question Being Answered**: Supabase 検証後にローカル Docker への切り替えも実施するか
- **Who Decides**: 実施者（matsuo）
- **Decision Criteria**: 技術検証の目的がローカル切り替えの確認も含むかどうか
- **Possible Outcomes**:
  - Yes → Step 6 を実施する
  - No → 検証完了として終了する

---

## 9. Business Rules

**Rule 1: 読み取り専用の徹底**
- **Rule Statement**: この手順で使用する MCP サーバーは SELECT 操作のみを許可する
- **Business Rationale**: 技術検証段階では意図しないデータ変更を防ぐ
- **Applies To**: すべてのクエリ操作
- **Enforced By**: `@modelcontextprotocol/server-postgres`（`BEGIN TRANSACTION READ ONLY` がハードコード済み）
- **Exceptions**: なし（この手順のスコープでは例外なし）

**Rule 2: 認証情報は WxO Connections で管理する**
- **Rule Statement**: 接続文字列（パスワード含む）は WxO Connections のセキュアストレージに格納し、YAML ファイルには記載しない
- **Business Rationale**: 認証情報の漏洩防止。YAML が Git 管理可能になる。
- **Applies To**: `toolkits/m-postgres-toolkit.yaml`、接続文字列を含む全ファイル
- **Enforced By**: Connections を使う設計（`$DATABASE_URL` 参照）。ツールキット YAML は Git コミット可。

---

## 10. Exception Handling

**Exception 1: ツールキットのインポートが失敗する**
- **What Goes Wrong**: `orchestrate toolkit import` がエラーを返す
- **How It's Detected**: CLI のエラーメッセージ
- **Business Impact**: エージェントのテストに進めない
- **Response Procedure**: エラーメッセージを記録し、YAML の文法・接続文字列・WxO 環境の状態を確認する
- **Responsible Party**: 実施者（matsuo）
- **Escalation**: WxO ドキュメント・ADK リポジトリの Issue を参照

**Exception 2: エージェントが `query` ツールを呼ばない**
- **What Goes Wrong**: 自然言語で問いかけてもエージェントが DB を参照せず、回答が返らないか的外れな回答になる
- **How It's Detected**: WxO チャット画面での目視確認
- **Business Impact**: MCP 経由 DB 参照の検証ができない
- **Response Procedure**: エージェントの description を明確化する、または問いかけの表現を変えて再試行する
- **Responsible Party**: 実施者（matsuo）

**Exception 3: ローカル Docker への接続が失敗する**
- **What Goes Wrong**: Connections URL をローカル用に変更後、エージェントが DB に接続できない
- **How It's Detected**: クエリ結果が返らない、またはエラーメッセージが表示される
- **Business Impact**: ローカル切り替えの確認ができない
- **Response Procedure**:
  1. Docker コンテナの起動状態を確認（`docker ps`）
  2. TCP トンネルが起動しており、公開ホスト名が正しいか確認
  3. `DATABASE_URL` のホスト名が `localhost` になっていないか確認（WxO クラウドからは到達不可）
  4. `tcp.XXXX.trycloudflare.com` の `XXXX` 部分が最新のトンネル URL と一致しているか確認
- **Responsible Party**: 実施者（matsuo）

---

## 11. Notes and Observations

### 11.1 Process Characteristics

- **Process Complexity**: 低〜中（ツール構成はシンプルだが MCP プロトコルの理解が必要）
- **Automation Level**: 半自動（セットアップは手動、クエリ実行は WxO エージェントが自動実行）
- **Integration**: WxO / Supabase / Docker という 3 システムの連携

### 11.2 Limitations and Constraints

- **MCP サーバーは WxO クラウドで実行される**: WxO ドキュメントに明記（"watsonx Orchestrate can correctly install dependencies and run your MCP server during tool execution"）。ローカル PC では動作しない。ローカル DB への接続には TCP トンネルが必要。
- **`query` ツール1本のみ**: `@modelcontextprotocol/server-postgres` は SELECT 専用の `query` ツールしか提供しない。テーブル一覧や構造の取得は LLM が information_schema に対するクエリを自力で生成する必要がある。
- **Text2SQL 方式の制約**: LLM が SQL を生成するため、複雑なクエリでは期待通りの結果にならない場合がある。
- **アーカイブ済み**: 使用する MCP サーバーはメンテナンス終了。セキュリティパッチや機能追加は見込めない。

### 11.3 将来の発展（本格利用に向けて）

本手順は技術検証を目的としており、本格利用には以下の発展が推奨される（本手順のスコープ外）:
- **目的別ツールの設計**: `get_products_by_category` など業務特化ツールを持つ独自 MCP サーバーの構築
- **R/W 対応**: INSERT/UPDATE/DELETE が必要になれば `crystaldba/postgres-mcp` への移行を検討
- **本番デプロイ**: MCP サーバーをクラウド環境にデプロイし、TCP トンネルへの依存を解消

---

## チーム命名規則（必須）

複数人で IG 環境を共有しているため、新規定義するリソースには
必ず私（matsuo）のプレフィックスを付与してください：

| リソース種別 | プレフィックス | 例 |
|---|---|---|
| エージェント名 | `M-` | `M-postgres-agent` |
| ツールキット名 | `m-` | `m-postgres` |
| コネクション名 | `m-` | `m-postgres-conn` |
| ツール名・関数名 | `m_` | `m_query_products` |
| YAML ファイル名 | 同上のルールに従う | `m-postgres-toolkit.yaml` |

> YAML ファイル名も同じルールに従うこと。

