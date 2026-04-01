# WxO Skills Lab

WxO ADK の Skills・MCP Server の学習・検証用ワークスペース。

**作成日**: 2026年3月31日
**対象者**: matsuo さん（イグアス）

---

## このリポジトリの目的

Claude Code から IBM watsonx Orchestrate (WxO) ADK の Skills を使って
エージェント開発を学習・検証する環境。

```
Agent Skills オープンスタンダード（Anthropic 発・2025年12月）
        ↓ IBM が採用
  Bob Skills ／ WxO ADK Skills（sop-builder・wxo-builder・customercare-mcp-builder）
        ↓ Claude Code / Bob が読んで
  WxO エージェントを構築・デプロイ（orchestrate CLI）
        ↓ MCP で連携
  ビジネス業務が動く
```

---

## ディレクトリ構成

```
wxo-skills-lab/
├── .claude/
│   └── skills/                         # Claude Code が読む Skills
│       ├── sop-builder/SKILL.md        # ワークフロー → SOP 生成
│       ├── wxo-builder/SKILL.md        # SOP → WxO エージェント生成
│       └── customercare-mcp-builder/   # MCP Server 生成
│           ├── SKILL.md
│           └── references/
├── docs/
│   └── wxo_skills_learning_plan.md    # 学習計画（詳細）
├── experiments/                        # 検証ログ・生成物
├── ibm-watsonx-orchestrate-adk/       # ADK リポジトリ（クローン済み）
└── README.md                           # このファイル
```

---

## Skills の使い方

Claude Code で以下のスラッシュコマンドが使える：

| コマンド | 用途 |
|---|---|
| `/sop-builder` | ワークフロー図・Langflow JSON・BPMN → SOP を生成 |
| `/wxo-builder` | SOP / プロンプト → WxO エージェント YAML・Python を生成 |
| `/customercare-mcp-builder` | カスタマーケア向け MCP Server を生成 |

---

## 学習フェーズ

詳細は [docs/wxo_skills_learning_plan.md](docs/wxo_skills_learning_plan.md) を参照。

| フェーズ | テーマ | 主な成果物 |
|---|---|---|
| Phase 1 | 理解の整理 | 整理ノート・比較表 |
| Phase 2 | 環境構築 | 動く環境 |
| Phase 3 | Skills 検証 | 検証レポート |
| Phase 4 | 実業務適用 | 提案資料・デモ |

---

## 参照リンク

| カテゴリ | リンク |
|---|---|
| WxO ADK GitHub | https://github.com/IBM/ibm-watsonx-orchestrate-adk |
| WxO ADK ドキュメント | https://developer.watson-orchestrate.ibm.com/agents/skills |
| ADK MCP Server | https://developer.watson-orchestrate.ibm.com/mcp_server/wxOmcp_overview |
| Agent Skills オープンスタンダード | https://agentskills.io |
| sop-builder SKILL.md | https://github.com/IBM/ibm-watsonx-orchestrate-adk/blob/main/skills/sop-builder/SKILL.md |
| wxo-builder SKILL.md | https://github.com/IBM/ibm-watsonx-orchestrate-adk/blob/main/skills/wxo-builder/SKILL.md |
| customercare-mcp-builder SKILL.md | https://github.com/IBM/ibm-watsonx-orchestrate-adk/blob/main/skills/customercare-mcp-builder/SKILL.md |

---

## この計画の元になった会話

https://claude.ai/chat/8cad6720-8373-43be-930e-1bc9149dd5e2

---

*experiments/ に検証ログを随時追加していく。*
