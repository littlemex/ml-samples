# SearXNG と Livebook による検索アプリケーション

このプロジェクトは、SearXNG検索エンジン、Livebook、Ollamaを組み合わせて、ウェブ検索とLLMを統合したアプリケーションを構築します。

## システムアーキテクチャ

```mermaid
graph TB
    subgraph "検索・質問応答システム"
        LB[Livebook<br/>ノートブック実行環境]
        SX[SearXNG<br/>メタ検索エンジン]
        OL[Ollama<br/>ローカルLLM]
        
        LB -->|1. 検索クエリ| SX
        SX -->|2. 検索結果| LB
        LB -->|3. テキスト埋め込み<br/>質問応答| OL
        OL -->|4. 応答生成| LB
    end

    subgraph "外部サービス"
        GS[Google検索]
        BS[Brave検索]
        DS[DuckDuckGo検索]
    end

    SX -->|検索リクエスト| GS
    SX -->|検索リクエスト| BS
    SX -->|検索リクエスト| DS
```

## データフロー

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant LB as Livebook
    participant SX as SearXNG
    participant OL as Ollama
    participant SE as 検索エンジン

    User->>LB: 質問入力
    LB->>SX: 検索クエリ送信
    SX->>SE: 複数の検索エンジンに<br/>クエリを送信
    SE-->>SX: 検索結果返却
    SX-->>LB: JSON形式で結果返却
    LB->>LB: テキストチャンキング
    LB->>OL: テキスト埋め込み要求
    OL-->>LB: 埋め込みベクトル返却
    LB->>LB: 類似度検索
    LB->>OL: 質問応答要求
    OL-->>LB: 回答生成
    LB-->>User: 回答表示
```

## システム構成の詳細

### コンポーネントの役割

1. **Livebook**
   - 対話型Elixir開発環境
   - 検索処理のオーケストレーション
   - テキストチャンキングと埋め込み処理
   - 類似度検索による関連情報抽出
   - ユーザーインターフェース提供

2. **SearXNG**
   - プライバシー重視のメタ検索エンジン
   - 複数の検索エンジンの結果を統合
   - JSON形式でのレスポンス提供
   - 検索結果のランキングとフィルタリング

3. **Ollama**
   - ローカルLLMサーバー
   - テキスト埋め込みベクトルの生成
   - 質問応答機能の提供
   - 高速なモデル推論

### ディレクトリ構造の説明

```mermaid
graph TD
    Root[ml-samples/oss-apps/searxng/] -->|設定| DC[docker-compose.yml<br/>コンテナ構成定義]
    Root -->|ドキュメント| RM[README.md<br/>プロジェクト説明]
    Root -->|Livebook| NB[notebooks/<br/>Livebookノートブック]
    Root -->|モデル| MD[models/<br/>モデル関連ファイル]
    Root -->|検索設定| SX[searxng/<br/>SearXNG設定]

    NB -->|実装| SC[search_chat.livemd<br/>検索・質問応答実装]
    MD -->|tokenizer| RB[ruri_base/<br/>Ruri Base tokenizer]
    SX -->|設定| CF[settings.yml<br/>SearXNG設定ファイル]

    style Root fill:#f9f,stroke:#333,stroke-width:4px
    style DC fill:#bbf,stroke:#333
    style RM fill:#bbf,stroke:#333
    style NB fill:#bfb,stroke:#333
    style MD fill:#bfb,stroke:#333
    style SX fill:#bfb,stroke:#333
```

### 処理フローの説明

1. **検索フェーズ**
   - ユーザーの質問をSearXNGに送信
   - 複数の検索エンジンから結果を取得
   - JSON形式で結果を受け取り

2. **テキスト処理フェーズ**
   - 検索結果からウェブサイトの内容を取得
   - HTMLタグの除去とテキストクリーニング
   - Chunxによるセマンティックチャンキング

3. **埋め込みフェーズ**
   - Ollamaを使用してテキストの埋め込みベクトルを生成
   - HNSWLibによるベクトルインデックスの作成
   - 質問文の埋め込みベクトル生成

4. **質問応答フェーズ**
   - 類似度検索による関連情報の抽出
   - コンテキスト情報の生成
   - Gemma 2による回答の生成

## 環境構成

以下のコンポーネントを Docker コンテナとして実行します：

- SearXNG: メタ検索エンジン
- Livebook: 対話型 Elixir 開発環境
- Ollama: ローカル LLM サーバー

### ディレクトリ構造

```
ml-samples/oss-apps/searxng/
├── docker-compose.yml
├── README.md
├── notebooks/          # Livebook ノートブック
│   └── search_chat.livemd
├── models/            # モデル関連ファイル
│   └── ruri_base/    # Ruri Base モデルの tokenizer
└── searxng/          # SearXNG の設定ファイル
    └── settings.yml
```

## セットアップ手順

1. リポジトリをクローンし、プロジェクトディレクトリに移動します：

```bash
cd ml-samples/oss-apps/searxng
```

2. 必要なディレクトリを作成します：

```bash
mkdir -p searxng models/ruri_base notebooks
```

3. Ruri Base モデルの tokenizer をダウンロードします：

```bash
curl -o models/ruri_base/tokenizer.json https://huggingface.co/ku-nlp/deberta-v2-base-japanese/raw/main/tokenizer.json
```

4. SearXNGの設定ファイルを作成します：

```bash
cat > searxng/settings.yml << 'EOL'
use_default_settings: false
server:
  secret_key: "searxng_secret_key"
  bind_address: "0.0.0.0"
  port: 8080
  base_url: "http://searxng_host:8080/"
  image_proxy: false
  cors_alloworigin: "*"
  public_instance: true
  limiter: false
  http_protocol_version: "1.0"

search:
  safe_search: 0
  autocomplete: 'google'
  default_lang: 'ja'

ui:
  query_in_title: false

general:
  debug: true
  instance_name: "SearXNG"

engines:
  - name: google
    use_mobile_ui: false
    disabled: false
  - name: duckduckgo
    disabled: false
  - name: brave
    disabled: false

outgoing:
  request_timeout: 5.0
  max_request_timeout: 15.0

result_proxy:
  url: ""
  key: ""

formats:
  - html
  - json
EOL
```

5. docker-compose.yml ファイルを使用してコンテナを起動します：

```bash
docker compose up -d
```

6. 各サービスの起動を確認します：

```bash
# SearXNGの動作確認
curl 'http://localhost:8888/search?q=test&format=json'

# Ollamaの動作確認
curl http://localhost:21434/api/version
```

## 使用するポート

各サービスは以下のポートで利用可能です：

- Livebook: http://localhost:8082 (管理用ポート : 8083)
- SearXNG: http://localhost:8888
- Ollama API: http://localhost:21434

![](./images/searxng-ui.png)

## SearXNG API の使用方法

JSON 形式で検索結果を取得する例：

```bash
curl 'http://localhost:8888/search?q=検索キーワード&format=json'
```

## Livebook での開発

1. ブラウザで http://localhost:8082 にアクセス
2. 新しいノートブックを作成
3. 必要なパッケージをインストール：

```elixir
Mix.install([
  {:req, "~> 0.5"},
  {:ollama, "~> 0.8"},
  {:chunx, github: "preciz/chunx"},
  {:hnswlib, "~> 0.1"},
  {:kino, "~> 0.15"}
])
```

## 設定ファイル

- `docker-compose.yml`: コンテナの設定
- `searxng/settings.yml`: SearXNG の設定（ JSON 形式のレスポンスが有効化済み）

## モデルの準備

1. Ruri Base モデルの tokenizer をダウンロードします：
```bash
curl -o models/ruri_base/tokenizer.json https://huggingface.co/ku-nlp/deberta-v2-base-japanese/raw/main/tokenizer.json
```

2. Ollama で必要なモデルをダウンロードします：
```bash
curl http://localhost:21434/api/pull -d '{"name": "kun432/cl-nagoya-ruri-base"}'
curl http://localhost:21434/api/pull -d '{"name": "hf.co/alfredplpl/gemma-2-2b-jpn-it-gguf"}'
```

## Livebook の使用方法

1. ブラウザで http://localhost:8082 にアクセスします
   - パスワード: `livebook-password-012`
2. `notebooks/search_chat.livemd` を開きます
3. 各セルを順番に実行していきます：
   - セットアップ（必要なパッケージのインストール）
   - 検索機能の実装と動作確認
   - ドキュメントの取得とチャンキング処理
   - インデックス作成
   - 質問応答機能の実行

## 注意事項

- コンテナの初回起動時にはイメージのダウンロードが必要なため、時間がかかる場合があります
- Ollama を使用する場合は、必要なモデルを別途ダウンロードする必要があります
