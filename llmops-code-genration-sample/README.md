# LLMOps Code Generation Evaluation

## プロジェクト概要

このプロジェクトは、Clineリポジトリを題材としたLLMのコード生成能力の評価と、効率的なファインチューニングによるトークン使用量の最適化を目的としています。

主な目標：
1. **コード生成能力の定量的評価**
   - 生成されたコードの品質測定
   - ベストプラクティスへの準拠度確認
   - エラー率と修正必要性の分析

2. **トークン使用量の最適化**
   - 効率的なプロンプト設計
   - コンテキスト管理の改善
   - 応答生成の最適化

3. **観測性（Observability）の向上**
   - 詳細な実行トレースの収集
   - パフォーマンス指標の測定
   - 問題箇所の特定と改善

## システムアーキテクチャ

### 全体構成

```mermaid
graph TB
    subgraph "評価環境アーキテクチャ"
        subgraph "Docker Compose環境"
            A[Clineリポジトリ] --> B[ベースライン評価]
            B --> C[ファインチューニング]
            C --> D[改善評価]
            
            subgraph "Observabilityレイヤー"
                E1[Langfuse] --> M[メトリクス集約]
                E2[MLflow] --> M
                E3[OpenLLMetry] --> M
            end
            
            subgraph "評価指標収集"
                M --> F1[コード品質]
                M --> F2[トークン効率]
                M --> F3[タスク完了率]
            end
        end
    end
```

### 評価指標収集システム

```mermaid
graph TB
    subgraph "評価指標収集システム"
        subgraph "データ収集"
            CD[コード生成] --> FM[FMEval]
            CD --> QA[品質分析]
            
            subgraph "FMEval処理"
                FM --> |コード評価| FMM[メトリクス生成]
                FM --> |品質スコア| FMS[スコアリング]
            end
            
            subgraph "品質分析処理"
                QA --> |静的解析| SA[構文チェック]
                QA --> |動的テスト| DT[実行テスト]
                QA --> |メトリクス| CM[複雑度分析]
            end
        end
        
        subgraph "結果集約"
            FMM --> AGG[集約処理]
            FMS --> AGG
            SA --> AGG
            DT --> AGG
            CM --> AGG
            
            AGG --> DB[(評価結果DB)]
        end
        
        subgraph "分析・レポート"
            DB --> VIZ[可視化]
            DB --> REP[レポート生成]
            DB --> COMP[比較分析]
        end
    end
```

### ベースライン評価・ファインチューニングフロー

```mermaid
graph TB
    subgraph "評価フロー"
        subgraph "ベースライン評価"
            B1[データセット準備] --> B2[初期評価実行]
            B2 --> B3[メトリクス収集]
            B3 --> B4[ベースラインスコア算出]
        end

        subgraph "ファインチューニング"
            F1[学習データ準備] --> F2[モデル調整]
            F2 --> F3[中間評価]
            F3 --> |要改善| F2
            F3 --> |OK| F4[最終評価]
        end

        subgraph "改善評価"
            I1[比較データセット準備] --> I2[改善後評価実行]
            I2 --> I3[メトリクス収集]
            I3 --> I4[改善度分析]
        end

        B4 --> F1
        F4 --> I1
    end
```

### Observabilityレイヤー詳細

```mermaid
graph TB
    subgraph "Observabilityレイヤーの構成"
        subgraph "データ収集"
            LF[Langfuse SDK] --> LFS[Langfuse Server]
            ML[MLflow SDK] --> MLS[MLflow Server]
            OT[OpenLLMetry SDK] --> OTS[OpenLLMetry Collector]
        end

        subgraph "データストレージ"
            LFS --> LDB[(Langfuse DB)]
            MLS --> MDB[(MLflow DB)]
            OTS --> |転送| LFS
            OTS --> |転送| MLS
        end

        subgraph "分析・可視化"
            LDB --> VL[Langfuse UI]
            MDB --> VM[MLflow UI]
        end
    end
```

### 評価システム構成

```mermaid
graph LR
    subgraph "データフロー"
        D[データ生成] --> E[評価実行]
        E --> R[結果収集]
        R --> A[分析・集計]
    end

    subgraph "ソースコード構成"
        DG[src/data/] --> EV[src/evaluation/]
        EV --> IN[src/integrations/]
        IN --> DG
    end
```

## ツールの役割と関係性

### 機能比較

| 機能 | Langfuse | MLflow | OpenLLMetry |
|------|----------|--------|-------------|
| トレース収集 | ✅ LLM特化 | ❌ | ✅ 汎用 |
| メトリクス収集 | ✅ | ✅ | ✅ |
| プロンプト管理 | ✅ | ❌ | ❌ |
| 実験管理 | ❌ | ✅ | ❌ |
| モデル管理 | ❌ | ✅ | ❌ |
| 分散トレーシング | ❌ | ❌ | ✅ |
| コスト分析 | ✅ | ❌ | ❌ |
| カスタムメトリクス | ✅ | ✅ | ✅ |
| ログ収集 | ✅ LLM特化 | ✅ 実験ログ | ✅ システムログ |

### データフロー

1. **OpenLLMetry**
   - システム全体の分散トレーシングを担当
   - 各コンポーネント間の通信を監視
   - システムレベルのログとトレースを収集
   - 収集したデータをLangfuseとMLflowに転送

2. **Langfuse**
   - LLM実行の詳細なトレースを保存
   - プロンプトとレスポンスの履歴を管理
   - LLM特化のログとトレースを収集
   - コストとトークン使用量を追跡

3. **MLflow**
   - 実験結果とメトリクスを保存
   - モデルのバージョンを管理
   - 実験関連のログを収集
   - ファインチューニングの進捗を追跡

## プロジェクト構成

```
.
├── docs/                          # プロジェクトドキュメント
│   ├── evaluation-plan.md         # 評価計画の詳細
│   └── progress.md               # 進捗状況の追跡
├── llmops-evaluation/            # LLM評価実装ディレクトリ
│   ├── src/                      # ソースコード
│   │   ├── data/                # データ生成・管理
│   │   ├── evaluation/          # 評価ロジック
│   │   └── integrations/        # 外部ツール統合
│   ├── data/                    # 生成されたデータ
│   └── results/                 # 評価結果
├── docker-compose.yml           # Docker環境設定
└── openllmetry-collector-config.yaml  # OpenLLMetry設定
```

## セットアップ手順

### 1. 基本環境構築

```bash
# リポジトリのクローン - 評価環境の基盤を準備
git clone [repository-url]
cd llmops-code-generation-sample

# Docker Compose環境の起動 - 各ツールのサーバーを起動
docker-compose up -d
```

### 2. 各ツールの設定

#### Langfuse設定
```bash
# Langfuse環境変数の設定 - LLMのトレース収集を有効化
cp .env.example .env
# .envファイルを編集してLangfuseの認証情報を設定
```

#### MLflow設定
```bash
# MLflow用のデータディレクトリ作成 - 実験データの保存先を準備
mkdir -p mlflow/data

# MLflow環境変数の設定 - 実験管理サーバーへの接続を設定
export MLFLOW_TRACKING_URI=http://localhost:5000
```

#### OpenLLMetry設定
```bash
# OpenLLMetry Collector設定の確認 - トレース収集の設定を確認
cat openllmetry-collector-config.yaml
```

### 3. 依存関係のインストール

```bash
# 評価スクリプト実行に必要なパッケージをインストール
cd llmops-evaluation
pip install -r requirements.txt
```

### 4. 評価環境の準備

```bash
# 評価データと結果の保存先を作成
mkdir -p data/raw data/processed results

# 評価スクリプトの実行権限を設定
chmod +x src/evaluation/runner.py
```

## 評価指標

### コード品質メトリクス

| カテゴリ | メトリクス | 説明 |
|---------|------------|------|
| コードの一貫性 | 命名規則遵守率 | 定義された命名規則に従っているコードの割合 |
| | コードスタイル一貫性 | スタイルガイドラインへの準拠度 |
| | 構造化度 | コードの論理的な構造化の度合い |
| ベストプラクティス | デザインパターン適用 | 適切なデザインパターンの使用率 |
| | エラーハンドリング | 例外処理の適切な実装率 |
| | ドキュメント充実度 | ドキュメントの完全性と品質 |
| エラー率 | 構文エラー | 発生した構文エラーの数 |
| | ランタイムエラー | 実行時に発生したエラーの数 |
| | 修正必要箇所 | 修正が必要なコード箇所の数 |

### 効率性メトリクス

| カテゴリ | メトリクス | 説明 |
|---------|------------|------|
| トークン使用量 | プロンプトトークン数 | 入力プロンプトのトークン数 |
| | レスポンストークン数 | 生成された応答のトークン数 |
| | コンテキスト効率 | コンテキストウィンドウの使用効率 |
| タスク完了時間 | プロンプト生成時間 | プロンプト作成に要した時間 |
| | レスポンス生成時間 | 応答生成に要した時間 |
| | 修正時間 | コード修正に要した時間 |
| メモリ使用量 | ピークメモリ | 最大メモリ使用量 |
| | 平均メモリ | 平均メモリ使用量 |
| | メモリリーク | 検出されたメモリリークの数 |

### Observabilityメトリクス

| カテゴリ | メトリクス | 説明 |
|---------|------------|------|
| トレーサビリティ | エラー特定 | エラー発生箇所の特定精度 |
| | ボトルネック検出 | パフォーマンス問題の検出率 |
| | 依存関係可視化 | システム依存関係の把握度 |
| デバッグ容易性 | ログ詳細度 | ログ情報の詳細さと有用性 |
| | エラーメッセージ | エラーメッセージの明確さ |
| | トレース連続性 | トレース情報の連続性 |
| メトリクス粒度 | データ収集間隔 | メトリクス収集の時間間隔 |
| | イベント捕捉率 | システムイベントの捕捉率 |
| | カスタムメトリクス | カスタム定義された指標の数 |

## 実装フロー

```mermaid
sequenceDiagram
    participant U as ユーザー
    participant A as エージェント
    participant O as Observabilityツール
    participant E as 評価システム
    
    Note over U,E: フェーズ1: ベースライン評価
    U->>A: コード生成タスク実行
    A->>O: メトリクス収集開始
    A->>A: タスク実行
    A->>O: 実行データ記録
    O->>E: メトリクス集約
    
    Note over U,E: フェーズ2: ファインチューニング
    E->>A: フィードバック提供
    A->>A: モデル調整
    
    Note over U,E: フェーズ3: 改善評価
    U->>A: 同様のタスク実行
    A->>O: メトリクス収集
    A->>A: 改善されたタスク実行
    A->>O: 実行データ記録
    O->>E: 比較メトリクス生成
```

## 注意事項

- 各ステップでのメトリクス収集を確実に実施
- ツール間の比較データを適切に保存
- 各ツールの設定値を適切に管理
- Docker Compose環境の状態を定期的に確認
- 各ツールのログを定期的に確認し、問題の早期発見に努める