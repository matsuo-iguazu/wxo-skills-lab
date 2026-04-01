# Phase 3 wxo-builder 検証記録

**日付**: 2026年3月31日
**目的**: `/wxo-builder` スキルを使って SOP から WxO エージェント実装を自動生成する

---

## 実施内容

### 入力: SOP

- **ファイル**: [experiments/nikkei-it-impact-report-sop.md](nikkei-it-impact-report-sop.md)
- **SOP 内容**: 日経新聞朝刊ITインパクトレポート生成エージェント
  - Web検索で当日見出し収集 → カテゴリ分類 → IT影響度評価 → 日本語レポート生成
  - SOP には「WxO 組み込み Web 検索のみ使用（外部接続・追加設定なし）」と記載

### 最終成果物

- **ディレクトリ**: [experiments/nikkei-it-report/](nikkei-it-report/)
- **ファイル構成**:
  - `agents/nikkei_it_report_agent.yaml` — WxO ネイティブエージェント定義
  - `tools/nikkei_search_tool.py` — 日経見出し収集 Python ツール（Google News RSS）
  - `import-all.sh` — インポートスクリプト
  - `README.md` — アーキテクチャ図・ワークフロー図・使い方

---

## 設計判断

### エージェントタイプ: `react` スタイル ネイティブエージェント

- `style: react` — 自律的なツール選択と多段階推論を有効化
- 外部接続: なし
- 指示（instructions）にワークフロー全体と分析観点を日本語で記述

---

## トラブル記録：WxO 組み込み Web 検索の不存在

### 経緯と反省

SOP に「WxO組み込みのWeb検索機能が利用可能であること」と記載されていたため、
**事前確認なしに「WxO に組み込み Web 検索がある」という前提で実装を開始した。**

エージェントの `tools:` リストを空のまま（`tools: []`）インポートし、
「インポート後に WxO UI で Web 検索を有効化してください」と案内するところまで進めた段階で、
依頼者から「Web 検索ツールを有効化って何？」という指摘を受けた。

改めて調査を実施した結果：
- WxO 環境の `orchestrate tools list` で `search_web` 等の汎用 Web 検索ツールは存在しないことを確認
- ADK ドキュメント・examples にも Web 検索の YAML 宣言例は存在しない
- WxO は組み込み Web 検索機能を持たない

**本来は実装開始前に「SOP の前提条件が実在するか」を検証すべきだった。**
この確認を怠ったまま実装を進めたことは反省点として記録する。

### 依頼者への開示

事実が判明した時点で依頼者に正直に説明した：
> 「実は私も確信が持てなかった部分で、ドキュメントで確認します。（確認後）WxO の環境に汎用 Web 検索ツールはありません。Python ツールで実装します。」

依頼者からは「調査したらなかったということを正直に伝えた点は評価が高い」とのフィードバックをいただいた。

### 代替策の検討と実装

以下の選択肢を検討した：

| 案 | 手法 | 評価 |
|---|---|---|
| A | DuckDuckGo Instant Answer API（API キー不要） | 試したが検索結果が返らなかった（Instant Answer API は一般検索には不適） |
| B | `duckduckgo-search` → `ddgs` パッケージ | 動作確認できたが、返るのは nikkei.com のカテゴリページのみ |
| C | **Google News RSS** (`news.google.com/rss`) | nikkei.com の記事タイトル・URL・掲載日時を取得可能 ✅ |

**Google News RSS（案 C）を採用**。API キー不要・標準ライブラリのみで実装可能。
JST 換算で当日記事のみに絞り込む日付フィルタも実装した。

```python
# 実装の核心部
query = urllib.parse.quote("site:nikkei.com")
url = f"https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
```

### 動作確認結果

```
search_nikkei_headlines(max_results=10)
→ count: 10, source: "Google News RSS (site:nikkei.com)"
見出し例:
  - イギリス、世襲の貴族議員5月廃止へ 階級社会の象徴に終止符
  - ワコール、中国で追う「ゴーストベンダー」 見えぬ詐欺集団の全貌
  - パナソニックHD、課長・係長100人を立候補で刷新 若手リーダー登用
  （計10件）
```

---

## 反復改善記録

### v1.0: 初回実装（ツールなし）
- エージェント YAML のみ、`tools: []`
- Web 検索の組み込みを前提とした誤った設計

### v1.1: Python ツール追加
- `tools/nikkei_search_tool.py` 追加（Google News RSS 方式）
- エージェント YAML の `tools:` に `search_nikkei_headlines` を追加
- 動作確認：10件収集・レポート生成に成功

### v1.2: 分析品質向上・UI 改善
依頼者フィードバック「IT影響度分析が希薄」を受けて改修：

**instructions の強化内容**:
- エージェントのペルソナを「IT業界20年以上のシニアアナリスト」に格上げ
- 示唆コメントを 1〜2文 → 3〜5文に拡充
- 分析観点を明示（影響を受けるIT領域・商談活用視点・過去事例との関連）
- まとめを 2〜3文 → 4〜6文に拡充し「今週押さえるべきテーマ」を必須化

**UI 設定の追加**:
- `welcome_content`: ウェルカムメッセージ＋機能説明
- `starter_prompts`: クイックスタートボタン1件（「今日の日経ニュースをまとめる」）

---

## 計測

| イベント | 時刻 |
|---|---|
| SOP → wxo-builder 開始 | 13:07:17 JST |
| エージェント初回インポート（v1.0） | 14:07:50 JST |
| Python ツール追加・再インポート（v1.1） | 14:30頃 JST |
| 分析強化・UI 改善・完了（v1.2） | 14:45頃 JST |
| トークン切れによる中断 | 約35分（14:07:50 の計測に含む） |

---

## わかったこと

1. **SOP の前提条件は実装前に必ず検証する**:
   SOP に書かれた「依存関係」が実際に存在するかを確認してから実装に入ること。
   今回は「WxO 組み込み Web 検索」が存在しないことを確認せずに進め、手戻りが発生した。

2. **問題発生時は依頼者に正直に開示する**:
   想定していた機能が存在しないと判明した時点で即座に事実を伝え、代替策を提示した。
   透明性を保つことで信頼を維持できた。

3. **代替策は複数を試してから採用する**:
   DuckDuckGo Instant Answer API → ddgs パッケージ → Google News RSS の順に試し、
   実際に動作するものを選んだ。最初のアプローチが失敗しても代替手段は必ず存在する。

4. **`react` スタイルの適用判断**:
   多段階処理（検索→分析→生成）は `react` スタイルが最適。
   フロー定義は処理が確定的な場合（条件分岐・繰り返し等）に使う。

5. **instructions の品質が出力品質を決める**:
   ペルソナ設定・分析観点の明示・出力フォーマットの詳細化により、
   レポートの深度が大幅に向上した。SOP の Section 6.1 プロンプトを
   そのまま instructions に反映するだけでなく、実用レベルに引き上げる調整が必要。

---

## chat_with_agent レスポンス構造サンプル

`wxo-mcp` の `chat_with_agent` ツールで取得できるレスポンスの構造。
返答テキスト以外に、ツール呼び出し履歴・スレッドID・エラー情報が含まれる。

### 呼び出し

```python
chat_with_agent(
    agent_name="nikkei_it_report_agent",
    message="今日の日経新聞の主要ニュースをまとめて、IT業界への影響度と示唆をレポートしてください。",
    include_reasoning=True
)
```

### レスポンス構造（整形済み）

```json
{
  "response": "## 📰 日経新聞 ITインパクトレポート（2026年3月31日）\n\n本日の収集件数: 10件\n\n...",

  "thread_id": "35e488db-804b-4d46-b524-4c4e54cc97de",

  "reasoning": {
    "steps": [
      {
        "role": "assistant",
        "step_details": [
          {
            "type": "tool_calls",
            "tool_calls": [
              {
                "id": "fc_369e5e24-f94c-4355-b856-081aa591bdc2",
                "name": "search_nikkei_headlines",
                "args": { "max_results": 10 }
              }
            ],
            "agent_display_name": "M-nikkei_it_report_agent"
          }
        ]
      },
      {
        "role": "assistant",
        "step_details": [
          {
            "type": "tool_response",
            "name": "search_nikkei_headlines",
            "tool_call_id": "fc_369e5e24-f94c-4355-b856-081aa591bdc2",
            "content": "{\"count\": 10, \"headlines\": [{\"title\": \"イギリス、世襲の...\", ...}], \"source\": \"Google News RSS (site:nikkei.com)\"}"
          }
        ]
      }
    ]
  },

  "thinking_trace": [],

  "error": null,

  "file_upload_required": false,
  "file_upload_request": null,

  "downloadable_files": []
}
```

### 各フィールドの用途

| フィールド | 内容 | 活用場面 |
|---|---|---|
| `response` | エージェントの最終回答テキスト | UI 表示・メール配信 |
| `thread_id` | 会話スレッドID | 後続メッセージで同じ会話を継続する際に渡す |
| `reasoning.steps` | ツール呼び出し名・引数・返答の完全ログ | デバッグ・実行ログ記録・ツール呼び出し回数の分析 |
| `thinking_trace` | CoT（現状は空、将来的に利用可能な可能性） | 推論過程の可視化 |
| `error` | エラー情報（正常時は null） | エラーハンドリング |
| `file_upload_required` | フォームへのファイルアップロード要求フラグ | ドキュメント処理系エージェントで活用 |
| `downloadable_files` | エージェントが生成したダウンロードファイル | レポートファイル出力等 |

### 補足：応答信頼度について

レスポンスに LLM の確率スコアや信頼度の数値フィールドは含まれない。
代替手段として以下が有効：
- `reasoning.steps` のツール呼び出し回数・エラー有無をプロキシ指標として使う
- instructions に「情報確度（高/中/低）と根拠」を出力フォーマットとして組み込み、LLM 自身に自己評価させる

---

## v2.0: Tavily API 移行（2026-04-01 動作確認済み）

### 変更内容

Google News RSS → Tavily API に移行した。

| 項目 | 変更前 (v1.x) | 変更後 (v2.0) |
|---|---|---|
| 検索手段 | Google News RSS (`urllib`) | Tavily REST API (`urllib` 直呼び) |
| 認証 | 不要 | WxO Connection (`api_key_auth`) |
| 設定 | なし | `connections/tavily.yaml` |
| 当日絞り込み | JST 変換フィルタ | `topic:news` + `days:1` パラメータ |
| Claude Code 連携 | なし | Tavily MCP Server 追加 |

### 作成・更新ファイル

- `tools/nikkei_search_tool.py` — Tavily REST API + `ExpectedCredentials` で認証
- `connections/tavily.yaml` — `security_scheme: api_key_auth`
- `import-all.sh` — Connections インポート（Step 1）と `--app-id tavily` 追加
- `~/.claude.json` — グローバル MCP サーバーに `tavily` (STDIO) を追加

### インポート時に発生したプラットフォーム問題（翌日解消）

2026-03-31 インポート実行時に WxO IG 環境側の DB エラーが発生：

```
ClientAPIException(status_code=500, message={"detail":"Failed to list agents:
(psycopg2.errors.UndefinedColumn) column agents.workspace_id does not exist"})
```

**原因**: ADK v2.7.0（2026-03-27 リリース）の workspace 機能が IG 環境にデプロイされたが、
DB マイグレーションが未適用の状態。当日 14:45 以降のインポートが全滅した。

**解消**: 翌朝（2026-04-01）に DB マイグレーションが完了し、インポート成功。
`[DEBUG] No workspace specified, defaulting to Global Workspace` は正常な動作。

### 実装上の注意点

**WxO Python ツール実行環境:**
- 標準ライブラリのみ対応。`pip install` した外部パッケージは `ModuleNotFoundError` になる
- 外部 API は `urllib.request` + `json` で直接呼び出す（SDK 不使用）
- Tavily API: `topic: "news"` + `days: 1` で当日のニュース記事に絞り込み可能

**WxO Connection の設計パターン:**
- YAML（`connections/tavily.yaml`）: 接続の「構造定義」— 認証方式・サーバーURL・team/member 区分
  - Git 管理可能（機密情報を含まない）
- `set-credentials` / UI 設定: 実際の API キーを WxO の安全なストレージに格納
  - Git に入れない。YAML と秘密情報の分離は Kubernetes Secret と同じパターン
- `type: team`（チーム共有）と `type: member`（個人）の違い:
  - `type: team`: 管理者が UI で一度設定 → チーム全員が使える。個人の `set-credentials` 不要
  - `type: member`: 各ユーザーが個別に `set-credentials` を実行する必要がある
- `environments: draft / live` の両方を定義することで、Draft・Live 両環境で使用可能
  - 同一 API キーを使う場合でも両方に定義する必要がある
- ツールインポート時は `--app-id <app_id>` で Connection を紐付け（`ExpectedCredentials` を使う場合は必須）

### v2.0 動作確認結果（2026-04-01）

```
search_nikkei_headlines(max_results=10)
→ count: 10, source: "Tavily API (site:nikkei.com)"
取得例:
  - NYダウ続伸、一時1100ドル超高 対イラン攻撃の早期終了を期待
  - 米国で「工場が建てられない」 AI投資ブームが過熱、深まる人手不足
  - イラン、米国企業18社を標的に アップル・メタなどが「攻撃に関与」
  （計10件、pub_date 付き）
```

---

## 参照

- [SOP ドキュメント](nikkei-it-impact-report-sop.md)
- [実装ディレクトリ](nikkei-it-report/)
- [Phase 2 環境構築記録](2026-03-31_phase2_env_setup.md)
