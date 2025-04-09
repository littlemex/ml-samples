# SearXNG MCP Server

このプロジェクトは、SearXNG検索エンジンのAPIをModel Context Protocol（MCP）を通じて利用可能にするサーバーを提供します。

## システムアーキテクチャ

```mermaid
graph TB
    subgraph "MCP Server"
        Server[MCP Server]
        WS[Web Search Tool]
        UR[URL Reader Tool]
        
        Server -->|Tool Registration| WS
        Server -->|Tool Registration| UR
    end

    subgraph "External Services"
        SearXNG[SearXNG API]
        Web[Web Content]
    end

    WS -->|Search Request| SearXNG
    SearXNG -->|JSON Response| WS
    UR -->|Fetch Content| Web
    Web -->|HTML Content| UR
```

## データフロー

```mermaid
sequenceDiagram
    participant Client
    participant MCP as MCP Server
    participant SX as SearXNG
    participant Web as Web Pages

    Client->>MCP: Web Search Request
    MCP->>SX: Search Query
    SX-->>MCP: Search Results (JSON)
    MCP-->>Client: Formatted Results

    Client->>MCP: URL Read Request
    MCP->>Web: Fetch Content
    Web-->>MCP: HTML Content
    MCP->>MCP: Convert to Markdown
    MCP-->>Client: Markdown Content
```

## ツール仕様

### Web Search Tool
```mermaid
graph LR
    Input[/"query: string<br/>count: number<br/>offset: number"/]
    -->Process[/"SearXNG API Call"/]
    -->Output[/"Formatted Results<br/>Title, Description, URL"/]
```

### URL Reader Tool
```mermaid
graph LR
    Input[/"url: string"/]
    -->Process[/"Fetch & Convert<br/>HTML to Markdown"/]
    -->Output[/"Markdown Content"/]
```

## エラーハンドリング

```mermaid
graph TD
    Error[Error Types]
    -->API[API Errors]
    -->|400-500|HandleAPI[Return Error Message]
    
    Error-->Timeout[Timeout Errors]
    -->|>10s|HandleTimeout[Abort Request]
    
    Error-->Parse[Parse Errors]
    -->|Invalid JSON/HTML|HandleParse[Return Error Status]
```

## 実装の詳細

1. **初期化フロー**
```mermaid
graph LR
    A[Create Server]-->B[Register Tools]
    B-->C[Setup Transport]
    C-->D[Start Server]
```

2. **リクエスト処理**
```mermaid
graph TD
    A[Receive Request]
    -->B{Tool Type?}
    B-->|Web Search|C[Process Search]
    B-->|URL Read|D[Process URL]
    C-->E[Format Response]
    D-->E
    E-->F[Return Result]
```

## セットアップ

1. 依存関係のインストール：
```bash
npm install
```

2. 環境変数の設定：
```bash
export SEARXNG_URL=http://localhost:8888  # SearXNG APIのURL
```

3. MCPサーバーの設定：

MCPサーバーを登録するには、以下の設定をMCP設定ファイルに追加します。

- VSCode拡張機能の場合: `~/.local/share/code-server/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- Claude Desktop Appの場合: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

```json
{
  "mcpServers": {
    "searxng": {
      "command": "node",
      "args": ["/path/to/mcp-searxng/build/index.js"],
      "env": {
        "SEARXNG_URL": "http://localhost:8888"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

4. サーバーのビルドと起動：
```bash
# ビルド
npm run build

# 起動
npm start
```

## エラーハンドリング

- API接続エラー：SearXNG APIへの接続に失敗した場合
- タイムアウト：リクエストが10秒を超えた場合
- パースエラー：JSONやHTMLの解析に失敗した場合

各エラーは適切なエラーメッセージとともに返されます。
