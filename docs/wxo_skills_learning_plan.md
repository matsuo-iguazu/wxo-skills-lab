# WxO × Claude Agent Skills 学習・検証計画

**作成日**: 2026年3月31日  
**対象者**: matsuo さん（イグアス）  
**背景**: 2026年3月31日の朝の会話から着想。WxO の最新アップデート・Agent Skills オープンスタンダード・IBM Bob の接続関係を体系的に理解・検証するための計画。

---

## 全体像：今日わかったこと

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

## フェーズ構成

| フェーズ | テーマ | 期間目安 | 主な成果物 |
|---|---|---|---|
| Phase 1 | 理解の整理 | 〜1週間 | 整理ノート・比較表 |
| Phase 2 | 環境構築 | 〜2週間 | 動く環境 |
| Phase 3 | Skills 検証 | 〜3週間 | 検証レポート |
| Phase 4 | 実業務適用 | 〜1ヶ月 | 提案資料・デモ |

---

## Phase 1：理解の整理

### 目標
今日の会話で得た知識を自分の言葉で説明できるようにする。

### タスク

#### 1-1. Agent Skills 3者比較の整理
- [ ] Anthropic Claude Skills・WxO ADK Skills・Bob Skills の比較表を自分で書いてみる
- [ ] 「オープンスタンダード」としての意味を説明できるようにする
- [ ] agentskills.io を読む

#### 1-2. WxO の3つの SKILL.md 精読
- [ ] `sop-builder/SKILL.md`（722行）を通読・ポイントをメモ
- [ ] `wxo-builder/SKILL.md`（1739行）を通読・ポイントをメモ
- [ ] `customercare-mcp-builder/SKILL.md`（537行）を通読・ポイントをメモ
- [ ] 3つの使い分けを1枚の図で整理

#### 1-3. MCP Server 2種の理解
- [ ] Documentation Server と CLI Server の役割の違いを説明できるようにする
- [ ] STDIO トランスポートの仕組みを理解する
- [ ] Claude Code + bash 実行との違いを整理する

#### 1-4. WxO 2026年3月アップデートの整理
- [ ] ユーザーピッカー・日時フィールドなど今回のアップデートを自分のユースケースで考える
- [ ] ADK 2.6.0 の新機能（統一コネクション・複数ファイルアップロード等）を整理

---

## Phase 2：環境構築

### 目標
Claude Code から WxO ADK Skills + MCP Server が全部つながる状態にする。

### タスク

#### 2-1. ADK MCP Server のインストール
```bash
# venv をアクティベート
source /path/to/your/venv/bin/activate

# MCP Server パッケージを追加
pip install --upgrade ibm-watsonx-orchestrate-mcp-server

# パスを確認
which ibm-watsonx-orchestrate-mcp-server
```
- [ ] インストール完了
- [ ] `which` でパスを確認

#### 2-2. Claude Code の MCP 設定に CLI Server を追加
```json
{
  "mcpServers": {
    "wxo-docs": {
      "type": "stdio",
      "command": "/home/matsuo/.local/bin/mcp-proxy",
      "args": ["--transport", "streamablehttp",
               "https://developer.watson-orchestrate.ibm.com/mcp"],
      "env": {}
    },
    "wxo-mcp": {
      "type": "stdio",
      "command": "<which の結果>",
      "args": [],
      "env": {
        "WXO_MCP_WORKING_DIRECTORY": "<プロジェクトディレクトリ>"
      }
    }
  }
}
```
- [ ] 設定ファイルへの追記完了
- [ ] Claude Code 再起動後に CLI Server が認識されることを確認

#### 2-3. ADK リポジトリのクローンと Skills の配置
```bash
git clone https://github.com/IBM/ibm-watsonx-orchestrate-adk.git

mkdir -p ~/.claude/skills/sop-builder
mkdir -p ~/.claude/skills/wxo-builder
mkdir -p ~/.claude/skills/customercare-mcp-builder

cp ibm-watsonx-orchestrate-adk/skills/sop-builder/SKILL.md \
   ~/.claude/skills/sop-builder/
cp ibm-watsonx-orchestrate-adk/skills/wxo-builder/SKILL.md \
   ~/.claude/skills/wxo-builder/
cp ibm-watsonx-orchestrate-adk/skills/customercare-mcp-builder/SKILL.md \
   ~/.claude/skills/customercare-mcp-builder/
```
- [ ] Skills の配置完了
- [ ] Claude Code で `/sop-builder` が認識されることを確認

#### 2-4. Claude.ai（Web）への Skills アップロード（任意）
- [ ] sop-builder フォルダを zip 化
- [ ] Settings > Features からアップロード
- [ ] Claude.ai 上で動作確認

#### 2-5. Bob の環境確認
- [ ] IBM Bob をインストール（または確認）
- [ ] Bob に同じ SKILL.md を配置（`.bob/skills/`）
- [ ] Advanced モードで動作確認

---

## Phase 3：Skills 検証

### 目標
3つの SKILL.md が実際にどう動くかを体験し、Claude Code・Bob での違いを把握する。

### タスク

#### 3-1. sop-builder の検証
- [ ] 既存の業務フロー（例：通話記録→Salesforce 登録）を渡してみる
- [ ] BPMN または Langflow JSON を入力してみる
- [ ] 生成された SOP の品質を評価する
- [ ] 「怖い」ポイント（ハルシネーション防止ルール等）が実際に機能しているか確認

#### 3-2. wxo-builder の検証
- [ ] sop-builder で生成した SOP を wxo-builder に渡す
- [ ] 生成された YAML・Python コードを確認
- [ ] `import-all.sh` でデプロイまで実行する
- [ ] エラーが出た場合の対処を記録する

#### 3-3. customercare-mcp-builder の検証
- [ ] カスタマーケアシナリオを作って渡してみる
- [ ] TypeScript / Python どちらで生成するか選択
- [ ] 生成された MCP サーバーコードを確認
- [ ] WxO に接続して動作確認

#### 3-4. CLI Server の検証（Phase 2 完了後）
- [ ] Claude Code から `orchestrate agents list` を MCP 経由で実行
- [ ] bash 直接実行との挙動の違いを比較
- [ ] エラーハンドリングの違いを記録

#### 3-5. Claude Code vs Bob の比較
- [ ] 同じ SKILL.md・同じ指示で両者に WxO エージェントを作らせる
- [ ] 生成品質・速度・操作感の違いを記録
- [ ] どちらが WxO 開発に向いているかを評価

---

## Phase 4：実業務適用

### 目標
検証で得た知識をお客様への提案・社内業務に活かす。

### タスク

#### 4-1. ユースケース整理
- [ ] 自社（イグアス）内での適用候補を列挙
- [ ] お客様への提案候補を列挙
- [ ] WxO × Claude Code が特に有効なシナリオを特定

#### 4-2. デモシナリオ作成
- [ ] sop-builder → wxo-builder の一気通貫デモを作る
- [ ] 所要時間・精度・従来手順との比較を測定

#### 4-3. 提案資料への落とし込み
- [ ] 「Claude Code で WxO を開発する」という新しい開発スタイルの説明資料
- [ ] Agent Skills オープンスタンダードの意義を説明するスライド

#### 4-4. フィードバックと反復
- [ ] IBM へのフィードバック（ADK の改善要望等）を整理
- [ ] 社内勉強会・共有の機会を作る

---

## 参照リンク集

| カテゴリ | リンク |
|---|---|
| WxO What's New | https://www.ibm.com/docs/en/watsonx/watson-orchestrate/base?topic=notes-whats-new |
| WxO ADK リリースノート | https://developer.watson-orchestrate.ibm.com/release/release |
| WxO ADK Skills ドキュメント | https://developer.watson-orchestrate.ibm.com/agents/skills |
| ADK MCP Server 概要 | https://developer.watson-orchestrate.ibm.com/mcp_server/wxOmcp_overview |
| ADK GitHub | https://github.com/IBM/ibm-watsonx-orchestrate-adk |
| sop-builder SKILL.md | https://github.com/IBM/ibm-watsonx-orchestrate-adk/blob/main/skills/sop-builder/SKILL.md |
| wxo-builder SKILL.md | https://github.com/IBM/ibm-watsonx-orchestrate-adk/blob/main/skills/wxo-builder/SKILL.md |
| customercare-mcp-builder SKILL.md | https://github.com/IBM/ibm-watsonx-orchestrate-adk/blob/main/skills/customercare-mcp-builder/SKILL.md |
| IBM Bob Skills ドキュメント | https://bob.ibm.com/docs/ide/features/skills |
| Anthropic Agent Skills | https://www.anthropic.com/news/skills |
| Agent Skills 公式ドキュメント | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview |
| Agent Skills オープンスタンダード | https://agentskills.io |

---

## 今日の会話リンク

この計画の元になった会話：  
https://claude.ai/chat/8cad6720-8373-43be-930e-1bc9149dd5e2

---

## メモ欄

検証中に気づいたこと・ハマったこと・面白かったことを随時記録する。

---

*この計画は随時更新する。完了したタスクは ✅ に変更。*
