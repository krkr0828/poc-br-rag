# プロジェクトディレクトリ構造

本ドキュメントでは、Bedrock RAG Learning Project のディレクトリ構造とその役割を説明します。

## ルートディレクトリ

```
poc-br-rag/
├── src/                        # アプリケーションソースコード
├── terraform/                  # インフラ定義（IaC）
├── scripts/                    # デプロイ・運用スクリプト
├── docs/                       # ドキュメント
├── sample-docs/                # サンプルドキュメント（Knowledge Base用）
├── .gitignore                  # Git除外設定
├── .gitattributes              # Git属性設定
├── README.md                   # プロジェクト概要
├── requirements.txt            # Python依存関係（本番環境）
└── requirements-dev.txt        # Python依存関係（開発環境）
```

---

## 詳細構造

### `src/`
AWS Lambda関数のソースコード（Python 3.11+）

```
src/
├── config/                     # 設定とプロンプト
│   ├── __init__.py
│   ├── settings.py            # 環境変数と設定管理
│   └── prompts.py             # Bedrockプロンプトテンプレート
├── handlers/                   # Lambda関数ハンドラー
│   ├── __init__.py
│   ├── api_handler.py         # API Gateway エントリーポイント
│   ├── bedrock_invoke.py      # Bedrock Claude 3 Haiku呼び出し
│   ├── cache_response.py      # DynamoDBキャッシュ書き込み
│   ├── guardrails_check.py    # Guardrailsチェック（入出力）
│   └── kb_query.py            # Knowledge Base クエリ実行
├── models/                     # データモデル（Pydantic）
│   ├── __init__.py
│   ├── request.py             # リクエストモデル（QueryRequest）
│   ├── response.py            # レスポンスモデル（QueryResponse, ErrorResponse）
│   └── cache.py               # キャッシュモデル
├── services/                   # サービス層（ビジネスロジック）
│   ├── __init__.py
│   ├── bedrock_service.py     # Bedrock API連携
│   ├── kb_service.py          # Knowledge Base API連携
│   ├── guardrails_service.py  # Guardrails API連携
│   └── cache_service.py       # DynamoDBキャッシュ管理
└── utils/                      # ユーティリティ
    ├── __init__.py
    ├── logger.py              # 構造化ログ（CloudWatch対応）
    ├── error_handler.py       # エラーハンドリング
    └── validators.py          # 入力バリデーション
```

**主な機能:**
- **API Handler**: API Gateway からのリクエストを受け取り、Step Functions を起動
- **Step Functions ワークフロー連携**: 5つのLambda関数がStep Functionsで連携
  1. `guardrails_check.py`: 入力コンテンツの安全性チェック
  2. `kb_query.py`: Knowledge Base から関連ドキュメントを検索
  3. `bedrock_invoke.py`: Claude 3 Haiku で回答生成（出力Guardrailsチェック含む）
  4. `cache_response.py`: 結果をDynamoDBにキャッシュ
- **データモデル**: Pydantic による型安全なリクエスト/レスポンス定義
- **サービス層**: AWS SDK (boto3) を使った Bedrock, Knowledge Base, Guardrails API連携
- **構造化ログ**: CloudWatch Logs にJSON形式で出力

### `terraform/`
インフラストラクチャ定義（Infrastructure as Code）

```
terraform/
├── main.tf                     # プロバイダー設定とメインリソース
├── providers.tf                # AWS プロバイダー設定
├── variables.tf                # 変数定義
├── outputs.tf                  # 出力値定義（API URL等）
├── api_gateway.tf              # API Gateway REST API
├── lambda.tf                   # Lambda関数定義（5つ）
├── step_functions.tf           # Step Functions ステートマシン
├── dynamodb.tf                 # DynamoDB テーブル（キャッシュ用）
├── s3.tf                       # S3 バケット（Lambdaデプロイパッケージ）
├── iam.tf                      # IAM ロール・ポリシー
├── cloudwatch.tf               # CloudWatch Logs ロググループ
├── bedrock.tf                  # Bedrock関連リソース（データソース）
├── TERRAFORM_GUIDE.md          # Terraform 使用ガイド
├── terraform.tfvars.example    # 変数設定サンプル
└── .terraform.lock.hcl         # Terraform 依存関係ロックファイル
```

**主要リソース:**
- **API Gateway (REST API)**: HTTP エンドポイント（POST /query）
- **Lambda Functions**: 5つの Lambda 関数（512MB メモリ、300秒タイムアウト）
- **Step Functions**: RAG ワークフローのオーケストレーション
- **DynamoDB**: クエリ結果キャッシュ（24時間TTL、オンデマンド課金）
- **S3 Bucket**: Lambda デプロイパッケージの保存
- **IAM Roles**: 最小権限の原則に基づくロール設計
  - Lambda実行ロール（Bedrock, Knowledge Base, Guardrails, DynamoDB アクセス）
  - Step Functions 実行ロール（Lambda 呼び出し）
- **CloudWatch Logs**: ログ集約（30日間保持）
- **Bedrock リソース**: Knowledge Base と Guardrails（手動作成、IDを変数で参照）

**変数設定:**
- `terraform.tfvars.example` をコピーして `terraform.tfvars` を作成
- `knowledge_base_id`, `guardrails_id` を設定（SETUP.md参照）

### `scripts/`
デプロイと運用のための自動化スクリプト（Bash）

```
scripts/
├── validate.sh                 # 環境検証（AWS CLI, Terraform, Python）
├── package_lambdas.sh          # Lambda デプロイパッケージ作成
├── deploy.sh                   # インフラデプロイ（Terraform apply）
├── test_api.sh                 # API エンドポイントテスト
├── logs.sh                     # CloudWatch Logs 閲覧
└── destroy.sh                  # インフラ削除（Terraform destroy）
```

**スクリプト機能:**
- **validate.sh**: 必須ツールとAWS認証情報の確認、Bedrock モデルアクセス確認
- **package_lambdas.sh**: Python 依存関係をパッケージング、Lambda デプロイパッケージ（ZIP）作成
- **deploy.sh**: Lambda パッケージング → S3 アップロード → Terraform apply の自動化
- **test_api.sh**: デプロイ後の疎通確認（クエリ実行とレスポンス確認）
- **logs.sh**: 指定した Lambda 関数のログをリアルタイム表示
- **destroy.sh**: 全リソースの削除（コスト最適化のため、テスト後に実行推奨）

### `docs/`
プロジェクトドキュメント

```
docs/
├── DIRECTORY_STRUCTURE.md      # ディレクトリ構造説明（本ドキュメント）
├── DESIGN.md                   # システム設計ドキュメント
├── SETUP_GUIDE.md              # 詳細セットアップガイド
├── architecture.drawio         # アーキテクチャ図（draw.io形式）
└── 構成図スクリーンショット.png   # アーキテクチャ図画像
```

**含まれるドキュメント:**
- **DIRECTORY_STRUCTURE.md**: プロジェクトのディレクトリ構造とその役割の説明
- **DESIGN.md**: アーキテクチャ、設計方針、技術選定の詳細
- **SETUP_GUIDE.md**: Bedrock リソースの手動作成手順（Knowledge Base, Guardrails）、変数設定、トラブルシューティング
- **architecture.drawio**: システムアーキテクチャの図解（編集可能）
- **構成図スクリーンショット.png**: アーキテクチャ図の画像版

### `sample-docs/`
Knowledge Base 用のサンプルドキュメント

```
sample-docs/
└── bedrock-intro.txt           # AWS Bedrock 紹介テキスト
```

**用途:**
- Knowledge Base のデータソースとして使用
- RAG システムの動作確認用サンプルデータ

---

## ルートレベルの設定ファイル

### `README.md`
プロジェクトの概要と使い方

**含まれる内容:**
- プロジェクトの特徴とアーキテクチャ図
- クイックスタートガイド
- 使用例（API クエリ、ログ閲覧）
- コスト見積もり（クエリ単価 ~$0.005 USD）
- 学習リソースへのリンク

### `.gitattributes`
Git属性設定ファイル

**用途:**
- ファイルタイプごとの属性設定
- 改行コードの自動変換設定

### `requirements.txt`
本番環境（Lambda）のPython依存関係

**主な依存関係:**
- `boto3`: AWS SDK for Python（Bedrock, Knowledge Base, Guardrails API）
- `pydantic`: データバリデーションと型安全性
- `aws-lambda-powertools`: 構造化ログ、トレーシング、メトリクス

### `requirements-dev.txt`
開発環境の追加依存関係

**主な依存関係:**
- `pytest`: ユニットテスト・統合テスト
- `black`: コードフォーマッター
- `flake8`: リンター
- `mypy`: 型チェッカー

### `.gitignore`
バージョン管理から除外するファイル・ディレクトリの指定

**主な除外対象:**
- **Python関連**: `__pycache__/`, `*.pyc`, `venv/`, `*.egg-info/`
- **Terraformキャッシュ・状態**: `.terraform/`, `*.tfstate`, `*.tfstate.*`, `terraform.tfvars`, `tfplan`
- **ビルド成果物**: `build/`, `*.zip` (Lambda デプロイパッケージ)
- **環境変数**: `.env`, `.env.local`
- **ログファイル**: `*.log`
- **IDE設定**: `.vscode/`, `.idea/`
- **OS ファイル**: `.DS_Store`, `Thumbs.db`
- **AWS 設定**: `.aws/`
- **AI ツール設定**: `.spec-workflow/`, `.claude/`

**Git管理に含まれる重要ファイル:**
- `.terraform.lock.hcl`: Terraform 依存関係バージョン固定
- `terraform.tfvars.example`: 変数設定サンプル（機密情報なし）
- `.gitattributes`: Git属性設定

---

## 注意事項

### セキュリティ
- **機密情報の除外**: `terraform.tfvars` には `knowledge_base_id`, `guardrails_id` が含まれます。Git には含めず、`.gitignore` で除外してください
- **AWS 認証情報**: AWS CLI の認証情報（`~/.aws/credentials`）を使用します。コードに直接記載しないでください
- **Terraform 状態ファイル**: `*.tfstate` ファイルには AWS リソースの詳細情報が含まれます。必ず `.gitignore` で除外してください

### コスト管理
- **テスト後の削除**: 学習・テスト終了後は必ず `./scripts/destroy.sh` を実行してください
- **サーバーレス構成**: Lambda, API Gateway, DynamoDB はオンデマンド課金で、アイドル時のコストはゼロです
- **手動作成リソース**: Knowledge Base と Guardrails は Terraform で削除されません。AWS Console から手動削除が必要です

### デプロイ
- **前提条件**: Bedrock の Knowledge Base と Guardrails を事前に手動作成する必要があります（SETUP.md 参照）
- **リージョン**: デフォルトは `ap-northeast-1` (東京リージョン)。Bedrock サービスが利用可能なリージョンを選択してください
- **ビルド成果物**: `lambda_deployment.zip` はローカルでビルドされ、S3 にアップロードされます。Git には含めません
