# html2md-crawler

## 概要

本プロジェクトは、指定したウェブページのHTMLを取得し、メインコンテンツを抽出してMarkdown形式に変換するツール群です。複数のURLを再帰的にクロールし、Markdownに変換した結果をまとめて出力することが可能です。

## 構成

### crawler.py

- 指定したURLからリンクを抽出し、同一ドメイン内のページを再帰的にクロールします。
- クロール対象のURLは、ベースURLと同じ階層または子階層に限定可能です。
- URLの正規化や階層判定を行い、不要な外部リンクのクロールを防止します。

### html2md.py

- HTML文字列をOpenAIのAPIを利用してMarkdown形式に変換します。
- メニューやナビゲーションなどの補助的な要素を除外し、メインコンテンツのみを変換対象とします。
- 見出しの階層構造やリスト、画像、テーブル、コードブロックなどを適切にMarkdownに変換します。

### html2md_crawler.py

- `crawler.py`で抽出したURL群に対して`html2md.py`の変換処理を並列で実行します。
- 変換結果をまとめて標準出力またはファイルに保存します。
- クロールの際に同階層のリンクを含めるかどうかをオプションで指定可能です。

## 使い方

### 0. イニシャライズ

```bash
uv sync
```

```bash
# .envにOpenAIのAPIキーを設定する
cp .env.sample .env
```

### 1. クロールとMarkdown変換を一括で実行する

```bash
python html2md_crawler.py <開始URL> [-i] [-o 出力ファイル] [-q]
```

- `<開始URL>`: クロールを開始するURL
- `-i`, `--include_same_level`: ベースURLと同階層のリンクもクロール対象に含める
- `-o`, `--output`: 変換結果のMarkdownを保存するファイルパス（省略時は標準出力）
- `-q`, `--quiet`: ログ出力を抑制

### 2. 単一または複数URLのHTMLをMarkdownに変換する

```bash
python html2md.py <URL1> <URL2> ... [-o 出力ファイル] [-q]
```

- 複数URLを指定可能
- `-o`でまとめてMarkdownをファイルに保存可能
- `-q`でログを抑制

### 3. URLの抽出のみを行う

```bash
python crawler.py <開始URL> [-i] [-q]
```

- クロールしたURL一覧を標準出力に表示
- `-i`で同階層リンクも含める
- `-q`でログを抑制

## 環境変数

- `OPENAI_API_KEY`: OpenAI APIを利用するためのAPIキーを環境変数に設定してください。
