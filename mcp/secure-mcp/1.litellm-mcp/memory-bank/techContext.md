# 技術コンテキスト: LiteLLM MCP

## 使用技術

### コア技術

1. **LiteLLM Proxy**
   - バージョン: 最新（ghcr.io/berriai/litellm:main-latest）
   - 役割: LLMモデルへのアクセス提供、MCPサーバー管理
   - 設定: YAML形式の設定ファイル

2. **Docker & Docker Compose**
   - 役割: コンテナ化と環境管理
   - 設定: docker-compose.yml

3. **PostgreSQL**
   - バージョン: 15
   - 役割: データストア
   - 設定: 環境変数による設定

### MCP サーバー

1. **Context7 MCP**
   - 実装: Node.js
   - パッケージ: @upstash/context7-mcp
   - 役割: ライブラリドキュメントの提供
   - インストール方法: npx -y @upstash/context7-mcp@latest

2. **AWS Documentation MCP**
   - 実装: Python
   - パッケージ: awslabs.aws-documentation-mcp-server
   - 役割: AWSドキュメントの提供
   - インストール方法: uvx awslabs.aws-documentation-mcp-server@latest

### LLM モデル

1. **Amazon Bedrock**
   - モデル: Claude 3.5 Sonnet, Claude 3.7 Sonnet
   - アクセス方法: AWS IAM認証
   - リージョン: us-east-1, ap-northeast-1

## 開発環境セットアップ

### 前提条件

1. **Docker & Docker Compose**
   - インストール済みであること
   - Docker Composeプラグインが利用可能であること

2. **AWS認証情報**
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - AWS_REGION_NAME

### セットアップ手順

1. **環境変数の設定**
   ```bash
   cp .env.example .env
   # .envファイルを編集して必要な値を設定
   ```

2. **サービスの起動**
   ```bash
   ./manage-litellm.sh start
   ```

3. **状態確認**
   ```bash
   ./manage-litellm.sh status
   ```

4. **ログの確認**
   ```bash
   ./manage-litellm.sh logs litellm
   ./manage-litellm.sh logs context7-mcp
   ./manage-litellm.sh logs aws-docs-mcp
   ```

## 技術的制約

1. **ネットワーク**
   - MCPサーバーは外部ネットワークにアクセスする必要がある
   - コンテナ間通信はDockerネットワーク内で行われる
   - ポート4000がホストマシンで利用可能である必要がある

2. **リソース**
   - MCPサーバーはメモリを消費する（特にContext7 MCP）
   - キャッシュサイズは設定可能だが、ディスク容量に注意
   - 同時リクエスト数に応じたCPUリソースが必要

3. **認証**
   - LiteLLM Proxyは認証を必要とする（開発環境では無効化可能）
   - AWS認証情報が必要（IAMロール or アクセスキー）
   - MCPサーバーへの直接アクセスは制限されている

## 依存関係

1. **外部サービス**
   - Amazon Bedrock API
   - Context7のライブラリドキュメントサービス
   - AWSドキュメントサービス

2. **パッケージ依存関係**
   - Node.js (Context7 MCP用)
   - Python (AWS Documentation MCP用)
   - PostgreSQL クライアントライブラリ

3. **設定依存関係**
   - iam_role_config.yml: LiteLLM設定
   - .env: 環境変数設定
   - docker-compose.yml: コンテナ設定

## デプロイ戦略

1. **開発環境**
   - ローカルDockerでの実行
   - 環境変数による設定
   - ログの詳細表示

2. **テスト環境**
   - CI/CDパイプラインでの自動デプロイ
   - テスト用の認証情報
   - モニタリングの有効化

3. **本番環境**
   - セキュリティ強化（認証の有効化）
   - スケーリング設定の最適化
   - バックアップ戦略の実装

## トラブルシューティング

1. **一般的な問題**
   - MCPサーバーの接続エラー: ネットワーク設定を確認
   - 認証エラー: 環境変数と認証情報を確認
   - タイムアウト: タイムアウト設定とネットワーク状態を確認

2. **ログ確認**
   ```bash
   ./manage-litellm.sh logs <service-name>
   ```

3. **キャッシュクリア**
   ```bash
   ./manage-litellm.sh clear-cache
   ```

4. **サービス再起動**
   ```bash
   ./manage-litellm.sh restart
