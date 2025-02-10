# Background Removal Tool

画像から背景を自動的に削除するPythonツールです。ディレクトリ内の複数の画像を一括処理することができ、画像ごとに異なるモデルを指定することも可能です。

## 特徴

- ディレクトリ内の全画像を一括処理
- 画像ごとに異なるモデルを指定可能（config.json）
- 処理結果は元の画像と同じディレクトリに `output_` プレフィックス付きで保存
- 詳細なログ出力でエラー追跡が容易
- サポートする画像形式: PNG, JPG, JPEG, WebP

## インストール

https://docs.astral.sh/uv/getting-started/installation/#installation-methods

2. Python 3.9環境の作成とパッケージのインストール:

```bash
uv venv
source .venv/bin/activate  # Linux/macOS

uv pip install -r pyproject.toml
```

## 使用方法

### 基本的な使用方法

```bash
uv run rembg_python.py /path/to/image/directory --model u2net
```

デフォルトでは `u2net` モデルが使用されます。

### サンプルの実行

`examples` ディレクトリには以下のサンプル画像が用意されています：

- 人物画像（girl-1.jpg, girl-2.jpg, girl-3.jpg）
- アニメキャラクター（anime-girl-1.jpg, anime-girl-2.jpg, anime-girl-3.jpg）
- 動物（animal-1.jpg, animal-2.jpg, animal-3.jpg）
- 車（car-1.jpg, car-2.jpg, car-3.jpg）
- 食べ物（food-1.jpg）
- 植物（plants-1.jpg）

サンプルを実行するには：

事前にモデルをダウンロードしている必要があります。

```bash
uv run rembg_python.py examples
```

### モデルの設定（config.json）

`examples/config.json` には、画像の種類に応じて最適なモデルを設定しています：

- 人物・アニメキャラクター画像 → isnet-general-use（より精細な人物抽出が可能）
- その他の画像（動物、車、食べ物、植物）→ u2net（一般的な用途に適した汎用モデル）

config.jsonの例：
```json
{
    "girl-1.jpg": {
        "model": "isnet-general-use"
    },
    "anime-girl-1.jpg": {
        "model": "isnet-general-use"
    },
    "animal-1.jpg": {
        "model": "u2net"
    }
}
```

## サポートされているモデル

- u2net (デフォルト): 一般的な用途に適した汎用モデル
- isnet-general-use: より高精度な背景除去が可能なモデル。特に人物画像に効果的
- その他のモデルについては [rembg公式ドキュメント](https://github.com/danielgatis/rembg) を参照してください

## 出力

- 処理された画像は入力画像と同じディレクトリに保存されます
- 出力ファイル名は元のファイル名の前に `output_` が付加されます
  - 例: `girl-1.jpg` → `output_girl-1.jpg`

## ログ

処理の進行状況やエラーは標準出力とログに記録されます：
- 処理開始・完了の通知
- 各画像の処理状況
- エラーが発生した場合の詳細情報

## モデルファイルの配置

モデルファイルは `download_models.py` スクリプトによって自動的にダウンロードされます：

1. 初回実行時に必要なモデルが自動的にダウンロードされます
   ```bash
   uv run download_models.py
   ```

2. ダウンロードされるモデル：
   - u2net.onnx（デフォルトの汎用モデル）
   - isnet-general-use.onnx（人物画像用の高精度モデル）
   - その他のモデル

モデルは `models` ディレクトリに自動的に保存されます。既にダウンロード済みのモデルはスキップされます。

## トラブルシューティング

1. モデルファイルが見つからない場合
   - `download_models.py` を実行して、必要なモデルを再ダウンロードしてください
   - インターネット接続を確認してください

2. メモリエラーが発生する場合
   - 大きなサイズの画像を処理する場合は、十分なメモリが必要です
   - 必要に応じて画像サイズを縮小してから処理してください

3. config.jsonの形式エラー
   - JSON形式が正しいことを確認してください
   - モデル名が正しく指定されているか確認してください
