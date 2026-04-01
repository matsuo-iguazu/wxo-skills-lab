# 日経新聞 ITインパクトレポート エージェント

## 概要

日経新聞の当日朝刊主要見出しを自動収集・分析し、IT業界への影響度と示唆コメントを含む
日本語レポートを即座に提供する WxO ネイティブエージェント。

**生成日**: 2026年3月31日
**対象SOP**: [experiments/nikkei-it-impact-report-sop.md](../nikkei-it-impact-report-sop.md)
**設計規模**: XS（カスタムツールなし、WxO 組み込み機能のみ）

---

## アーキテクチャ図

```mermaid
graph TB
    User[["👤 ユーザー<br/>（IT コンサルタント・営業）"]]
    Agent[["🤖 nikkei_it_report_agent<br/>WxO Native Agent<br/>style: react"]]
    WebSearch[["🔍 Web 検索<br/>（WxO 組み込み）"]]
    LLM[["🧠 LLM<br/>groq/openai/gpt-oss-120b"]]
    Report[["📰 ITインパクトレポート<br/>（日本語）"]]

    User -->|「今日の日経ニュースをまとめて」| Agent
    Agent -->|見出し収集| WebSearch
    WebSearch -->|検索結果| Agent
    Agent -->|分析・レポート生成| LLM
    LLM -->|生成結果| Agent
    Agent -->|レポート返却| Report
    Report --> User

    style User fill:#90EE90,stroke:#333,color:#000
    style Agent fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style WebSearch fill:#F39C12,stroke:#D68910,color:#fff
    style LLM fill:#9B59B6,stroke:#7D3C98,color:#fff
    style Report fill:#FFB6C1,stroke:#333,color:#000
```

---

## ワークフロー図

```mermaid
flowchart TD
    Start([ユーザーが依頼]):::green
    S1["🔍 Step 1: Web 検索\n日経新聞から当日見出しを最大10件収集\nクエリ: 日経新聞 今日 ニュース"]:::blue
    S2["📂 Step 2: カテゴリ分類\n経済・政治・テクノロジー・国際・その他"]:::blue
    S3["📊 Step 3: IT影響度評価\n高・中・低 で相対評価"]:::blue
    S4["✍️ Step 4: レポート生成\n見出し + カテゴリ + 影響度 + 示唆コメント"]:::blue
    E1{"見出し取得できた？"}:::yellow
    AltSearch["🔄 代替検索\nGoogle News 等で再試行"]:::orange
    End([レポートを返却]):::red

    Start --> S1
    S1 --> E1
    E1 -->|Yes| S2
    E1 -->|No| AltSearch
    AltSearch --> S2
    S2 --> S3
    S3 --> S4
    S4 --> End

    classDef green fill:#90EE90,stroke:#333,color:#000
    classDef blue fill:#ADD8E6,stroke:#333,color:#000
    classDef yellow fill:#FFD700,stroke:#333,color:#000
    classDef orange fill:#FFA07A,stroke:#333,color:#000
    classDef red fill:#FFB6C1,stroke:#333,color:#000
```

---

## プロジェクト構成

```
nikkei-it-report/
├── __init__.py
├── README.md                          # このファイル
├── import-all.sh                      # インポートスクリプト
├── agents/
│   └── nikkei_it_report_agent.yaml   # エージェント定義
└── generated/                         # （将来のフロースペック用）
```

---

## 使用方法

### 前提条件

```bash
# 1. venv をアクティベート
source /home/matsuo/Downloads/wxo-skills-lab/.venv/bin/activate

# 2. WxO 環境に認証
orchestrate env activate IG
```

### インポート

```bash
cd /home/matsuo/Downloads/wxo-skills-lab/experiments/nikkei-it-report
./import-all.sh
```

### チャットで試す

```bash
orchestrate chat start
# エージェント「nikkei_it_report_agent」を選択
# 「今日の日経ニュースをまとめて」と入力
```

### WxO Web 検索の有効化について

本エージェントは WxO の組み込み Web 検索機能を使用します。
インポート後、WxO UI からエージェント設定を開き、
**Web 検索ツールが有効になっていることを確認**してください。

> WxO の react スタイルエージェントは、利用可能なツールを自律的に選択して
> 多段階の推論を行います。Web 検索ツールが有効な状態で使用してください。

---

## エージェント仕様

| 項目 | 値 |
|---|---|
| エージェント名 | `nikkei_it_report_agent` |
| スタイル | `react`（多段階推論・自律ツール選択） |
| LLM | `groq/openai/gpt-oss-120b` |
| カスタムツール | なし（WxO 組み込み機能のみ） |
| 対象データ | 当日の日経新聞ウェブ掲載記事（最大10件） |
| 出力言語 | 日本語 |

---

## 出力サンプル

```
## 📰 日経新聞 ITインパクトレポート（2026年3月31日）

本日の収集件数: 8件

---

### 【政府、AI規制法案を国会提出へ】
- **カテゴリ**: 政治
- **IT影響度**: 高
- **示唆**: AI開発・利用に対する法的規制が強化される可能性があり、
  AI関連事業を展開するIT企業は対応コストの増加が見込まれる。
  コンプライアンス体制の早期整備が急務となる。

---

### 【自動車大手、EV向け半導体調達を国内回帰】
- **カテゴリ**: 経済
- **IT影響度**: 高
- **示唆**: 国内半導体需要の拡大により、半導体商社・組み込みシステムベンダーに
  新たなビジネス機会が生まれる。サプライチェーン再編への対応が求められる。

---

### 📊 本日のまとめ
本日はAI規制と半導体サプライチェーンに関する動向が注目された。
規制対応と国内調達シフトという2つのテーマが、IT業界の中期戦略に
大きな影響を与える可能性がある。特にAI事業者はコンプライアンス対応を
急ぐ必要がある。
```

---

## 関連ファイル

- [SOP ドキュメント](../nikkei-it-impact-report-sop.md)
- [Phase 2 環境構築記録](../2026-03-31_phase2_env_setup.md)
