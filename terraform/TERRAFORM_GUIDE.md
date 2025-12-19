# Terraformディレクトリ説明

このドキュメントでは、`terraform/`ディレクトリ配下のファイル構成と各ファイルの役割、記載内容について説明します。

---

## 📁 ディレクトリ構造

```
terraform/
├── providers.tf              # Terraform・プロバイダー設定（22行）
├── main.tf                   # エントリーポイント（14行）
├── variables.tf              # 変数定義ファイル（53行）
├── outputs.tf                # 出力値定義ファイル（10行）
├── dynamodb.tf               # DynamoDBテーブル定義（40行）
├── s3.tf                     # S3バケット定義（96行）
├── bedrock.tf                # Bedrockリソース参照（53行）
├── iam.tf                    # IAMロール・ポリシー定義（216行）
├── lambda.tf                 # Lambda関数定義（179行）
├── step_functions.tf         # Step Functionsステートマシン（194行）
├── api_gateway.tf            # API Gateway REST API（156行）
├── cloudwatch.tf             # CloudWatch Logsロググループ（99行）
├── terraform.tfvars.example  # 変数設定サンプル
└── .terraform.lock.hcl       # 依存関係ロックファイル（自動生成）
```

**合計**: 約1,132行のTerraformコード、20個以上のAWSリソースを定義

---

## 📄 各ファイルの役割と内容

### 1. `providers.tf` - Terraform・プロバイダー設定（22行）

**役割**: Terraformのバージョン要件とAWSプロバイダーの設定を定義します。

#### 記載内容

```hcl
terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
```

**設定内容**:
- Terraform最小バージョン: `>= 1.5`
- AWSプロバイダーバージョン: `~> 5.0`
- デフォルトタグ: すべてのリソースに自動的にProject、Environment、ManagedByタグを付与

---

### 2. `main.tf` - エントリーポイント（14行）

**役割**: Terraformコードのエントリーポイント。各リソース定義ファイルへの参照コメントが記載されています。

**内容**:
- 各tfファイルの役割説明（コメントのみ）
- 実際のリソース定義は各専用ファイルに分割

---

### 3. `variables.tf` - 変数定義ファイル（53行）

**役割**: Terraformコードで使用する変数を定義し、デフォルト値を設定します。

#### 定義されている変数一覧

| 変数名 | 型 | デフォルト値 | 説明 |
|-------|-----|-----------|------|
| `aws_region` | string | `"ap-northeast-1"` | AWSリージョン（東京） |
| `project_name` | string | `"bedrock-rag"` | プロジェクト名（リソース名のプレフィックス） |
| `environment` | string | `"dev"` | 環境名（dev/stg/prod） |
| `log_retention_days` | number | `30` | CloudWatch Logsの保持期間（日数） |
| `cache_ttl_seconds` | number | `86400` | DynamoDBキャッシュのTTL（24時間） |
| `lambda_timeout` | number | `300` | Lambda関数のタイムアウト（秒） |
| `lambda_memory_size` | number | `512` | Lambda関数のメモリサイズ（MB） |
| `knowledge_base_id` | string | `""` | Bedrock Knowledge Base ID（手動作成） |
| `guardrails_id` | string | `""` | Bedrock Guardrails ID（手動作成） |

#### 変数の使い方

**1. terraform.tfvarsファイルで設定する場合**:
```hcl
# terraform.tfvars
aws_region        = "ap-northeast-1"
project_name      = "bedrock-rag"
environment       = "dev"
knowledge_base_id = "YOUR_KB_ID"
guardrails_id     = "YOUR_GUARDRAILS_ID"
```

**2. コマンドラインで上書きする場合**:
```bash
terraform apply -var="aws_region=us-east-1" -var="lambda_memory_size=1024"
```

---

### 4. `outputs.tf` - 出力値定義ファイル（10行）

**役割**: Terraform実行後に、デプロイされたリソースの情報を出力します。

#### 定義されている出力値

| 出力値名 | 説明 | 使用例 |
|---------|------|-------|
| `project_info` | プロジェクト情報（名前、環境、リージョン） | 環境確認 |

**注**: 各リソースファイル（dynamodb.tf、s3.tfなど）にも個別の出力値が定義されています。

#### 出力値の確認方法

```bash
# すべての出力値を表示
terraform output

# 特定の出力値を表示
terraform output project_info

# 出力値をJSON形式で表示
terraform output -json
```

---

### 5. `dynamodb.tf` - DynamoDBテーブル定義（40行）

**役割**: RAGシステムのクエリ結果をキャッシュするDynamoDBテーブルを定義します。

#### リソース定義

| リソース | リソース名 | 説明 |
|---------|----------|------|
| `aws_dynamodb_table` | cache | クエリ結果キャッシュテーブル |

**主要設定**:
- テーブル名: `${project_name}-${environment}-cache`
- 課金モード: `PAY_PER_REQUEST`（オンデマンド、コスト最適化）
- ハッシュキー: `query_hash`（クエリのハッシュ値）
- TTL: 有効（`ttl`属性、24時間後に自動削除）
- Point-in-Time Recovery: 無効（学習用のためコスト削減）

**用途**:
- 同じクエリの重複実行を防止
- Bedrock API呼び出しコストの削減
- レスポンス時間の短縮

---

### 6. `s3.tf` - S3バケット定義（96行）

**役割**: Lambda関数のデプロイパッケージを保存するS3バケットを定義します。

#### リソース定義

| リソース | リソース名 | 説明 |
|---------|----------|------|
| `aws_s3_bucket` | lambda_deployments | Lambdaデプロイパッケージ用バケット |
| `aws_s3_bucket_versioning` | lambda_deployments | バージョニング設定 |
| `aws_s3_bucket_public_access_block` | lambda_deployments | パブリックアクセスブロック |
| `aws_s3_object` | lambda_package | Lambda ZIPファイルのアップロード |

**主要設定**:
- バケット名: `${project_name}-lambda-deployments-${environment}-${account_id}`
- バージョニング: 有効
- パブリックアクセス: 完全ブロック
- 強制削除: 有効（`terraform destroy`時にオブジェクトがあっても削除可能）

**セキュリティ**:
- すべてのパブリックアクセスをブロック
- Lambda実行ロールのみアクセス可能

---

### 7. `bedrock.tf` - Bedrockリソース参照（53行）

**役割**: 手動作成したBedrock Knowledge BaseとGuardrailsをTerraformから参照するためのデータソース定義です。

#### 記載内容

```hcl
/**
 * Bedrock Resources
 *
 * Note: Knowledge Base and Guardrails must be created manually
 * This file uses data sources to reference existing resources
 */
```

**重要**:
- Bedrock Knowledge BaseとGuardrailsは**手動で作成**する必要があります（SETUP.md参照）
- TerraformではIDを変数で受け取り、Lambda関数の環境変数に設定します
- データソースはコメントアウトされており、変数による直接参照を使用

**設定される環境変数**:
- `KNOWLEDGE_BASE_ID`: Knowledge BaseのID
- `GUARDRAILS_ID`: GuardrailsのID

---

### 8. `iam.tf` - IAMロール・ポリシー定義（216行）

**役割**: Lambda関数とStep Functions実行ロールの権限を定義します。最小権限の原則に基づいた設計です。

#### 定義されているIAMリソース

| リソース | リソース名 | 説明 |
|---------|----------|------|
| `aws_iam_role` | lambda_execution | Lambda実行ロール（5つの関数で共通使用） |
| `aws_iam_role_policy` | lambda_bedrock | Bedrock API アクセス権限 |
| `aws_iam_role_policy` | lambda_dynamodb | DynamoDB アクセス権限 |
| `aws_iam_role_policy` | lambda_step_functions | Step Functions 起動権限 |
| `aws_iam_role_policy` | lambda_logs | CloudWatch Logs 書き込み権限 |
| `aws_iam_role` | step_functions_execution | Step Functions 実行ロール |
| `aws_iam_role_policy` | step_functions_lambda | Lambda 呼び出し権限 |

#### Lambda実行ロールの権限

**1. Bedrock API アクセス**:
- `bedrock:InvokeModel` - Claude 3 Haiku モデルの呼び出し
- `bedrock:Retrieve` - Knowledge Base からのドキュメント検索
- `bedrock:ApplyGuardrail` - Guardrails によるコンテンツチェック

**2. DynamoDB アクセス**:
- `dynamodb:PutItem` - キャッシュの書き込み
- `dynamodb:GetItem` - キャッシュの読み取り
- `dynamodb:Query` - クエリ実行

**3. Step Functions アクセス**:
- `states:StartExecution` - ステートマシンの起動
- `states:DescribeExecution` - 実行状態の確認

**4. CloudWatch Logs**:
- `logs:CreateLogStream` - ログストリームの作成
- `logs:PutLogEvents` - ログの書き込み

#### Step Functions実行ロールの権限

**Lambda 呼び出し**:
- `lambda:InvokeFunction` - Lambda関数の呼び出し（すべてのワークフロー関数）

---

### 9. `lambda.tf` - Lambda関数定義（179行）

**役割**: RAGワークフローを構成する5つのLambda関数を定義します。

#### 定義されているLambda関数

| 関数名 | ファイル | 説明 | タイムアウト |
|-------|---------|------|------------|
| `api_handler` | `src/handlers/api_handler.py` | API Gatewayエントリーポイント | 300秒 |
| `guardrails_check` | `src/handlers/guardrails_check.py` | Guardrailsチェック（入出力） | 300秒 |
| `kb_query` | `src/handlers/kb_query.py` | Knowledge Base クエリ実行 | 300秒 |
| `bedrock_invoke` | `src/handlers/bedrock_invoke.py` | Bedrock Claude 3 Haiku 呼び出し | 300秒 |
| `cache_response` | `src/handlers/cache_response.py` | DynamoDB キャッシュ書き込み | 300秒 |

**共通設定**:
- Runtime: `python3.11`
- Memory: `512 MB`（変数で変更可能）
- Timeout: `300秒`（変数で変更可能）
- デプロイパッケージ: S3バケットから取得（`lambda_deployment.zip`）

**環境変数**（すべての関数共通）:
- `DYNAMODB_TABLE_NAME` - DynamoDBテーブル名
- `KNOWLEDGE_BASE_ID` - Knowledge Base ID
- `GUARDRAILS_ID` - Guardrails ID
- `STATE_MACHINE_ARN` - Step Functions ARN（api_handlerのみ）
- `CACHE_TTL_SECONDS` - キャッシュTTL秒数

---

### 10. `step_functions.tf` - Step Functionsステートマシン（194行）

**役割**: RAGワークフローをオーケストレーションするステートマシンを定義します。

#### ワークフロー構成

```
1. GuardrailsCheck (入力チェック)
   ↓
2. KnowledgeBaseQuery (関連ドキュメント検索)
   ↓
3. BedrockInvoke (Claude 3 Haiku で回答生成)
   ↓
4. CacheResponse (結果をDynamoDBにキャッシュ)
```

**主要機能**:

**1. リトライ設定**:
- サービスエラー時の自動リトライ（最大3回）
- 指数バックオフ（2秒 → 4秒 → 8秒）

**2. エラーハンドリング**:
- `GuardrailsError`: Guardrailsブロック時の専用処理
- `ValidationError`: 入力バリデーションエラー
- `States.ALL`: その他のエラーのキャッチ

**3. 終了ステート**:
- `GuardrailsBlocked`: 不適切なコンテンツ検出時
- `HandleError`: エラー発生時
- `Success`: 正常終了

---

### 11. `api_gateway.tf` - API Gateway REST API（156行）

**役割**: HTTPエンドポイントを提供し、Lambda関数（api_handler）を呼び出します。

#### リソース定義

| リソース | リソース名 | 説明 |
|---------|----------|------|
| `aws_api_gateway_rest_api` | main | REST API |
| `aws_api_gateway_resource` | query | `/query`リソース |
| `aws_api_gateway_method` | query_post | `POST /query`メソッド |
| `aws_api_gateway_integration` | query_lambda | Lambda統合（AWS_PROXY） |
| `aws_api_gateway_deployment` | main | デプロイメント |
| `aws_api_gateway_stage` | main | ステージ（dev/prod） |

**エンドポイント構成**:
- **POST /query**: RAGクエリの実行
  - 統合タイプ: `AWS_PROXY`
  - 認証: `NONE`（学習用、本番環境では要認証設定）

**CORS設定**:
- `OPTIONS /query`: CORSプリフライトリクエスト対応
- レスポンスヘッダー: `Access-Control-Allow-*`

**デプロイ設定**:
- ステージ名: `${environment}`（例: dev）
- ログ設定: CloudWatch Logsにアクセスログを出力

---

### 12. `cloudwatch.tf` - CloudWatch Logsロググループ（99行）

**役割**: Lambda関数のログを集約するロググループを定義します。

#### 定義されているロググループ

| ロググループ名 | 保持期間 | 説明 |
|-------------|---------|------|
| `/aws/lambda/${project_name}-api-handler-${environment}` | 30日 | API Handlerログ |
| `/aws/lambda/${project_name}-guardrails-check-${environment}` | 30日 | Guardrailsチェックログ |
| `/aws/lambda/${project_name}-kb-query-${environment}` | 30日 | Knowledge Baseクエリログ |
| `/aws/lambda/${project_name}-bedrock-invoke-${environment}` | 30日 | Bedrock呼び出しログ |
| `/aws/lambda/${project_name}-cache-response-${environment}` | 30日 | キャッシュ書き込みログ |

**設定内容**:
- 保持期間: 30日間（変数で変更可能）
- コスト最適化: 古いログを自動削除

---

## 🔄 ファイル間の関係図

```
┌─────────────────────────────────────────────────────────┐
│                   terraform apply                         │
└───────────────────────────┬─────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
    ┌──────────────────┐        ┌──────────────────┐
    │  providers.tf    │        │  variables.tf    │
    │ （プロバイダー）   │        │  （変数定義）     │
    └──────────────────┘        └─────────┬────────┘
              │                           │
              │                           ▼
              │                 ┌──────────────────┐
              │                 │terraform.tfvars  │
              │                 │（変数値設定）     │
              │                 └──────────────────┘
              │                           │
              └───────────────┬───────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  main.tf         │
                    │ （エントリー）     │
                    └─────────┬────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │dynamodb.tf  │  │   s3.tf     │  │ bedrock.tf  │
    │  iam.tf     │  │ lambda.tf   │  │api_gateway.tf│
    │cloudwatch.tf│  │step_functions.tf│ │            │
    └─────────────┘  └─────────────┘  └─────────────┘
              │               │               │
              └───────────────┼───────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  AWS Resources   │
                    │ (20個以上)        │
                    └─────────┬────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   outputs.tf     │
                    │ （出力値定義）     │
                    └──────────────────┘
                              │
                              ▼
                        terraform output
```

---

## 🛠 使用方法

### 基本的なワークフロー

```bash
# 1. 初期化（プロバイダーのダウンロード）
cd terraform
terraform init

# 2. 変数ファイルの作成（必須）
cp terraform.tfvars.example terraform.tfvars

# 3. terraform.tfvarsを編集してKnowledge BaseとGuardrails IDを設定
vim terraform.tfvars

# 4. 実行計画の確認
terraform plan

# 5. リソースのデプロイ
terraform apply

# 6. 出力値の確認
terraform output

# 7. リソースの削除
terraform destroy
```

### スクリプトを使用したデプロイ

```bash
# プロジェクトルートから実行
./scripts/deploy.sh    # Lambda パッケージング + Terraform apply
./scripts/destroy.sh   # すべてのリソースを削除
```

---

## 📊 作成されるAWSリソースの一覧

`terraform plan`を実行すると、以下のリソースが作成されます：

### API Gateway（6個）
- REST API × 1
- Resource × 1（/query）
- Method × 2（POST、OPTIONS）
- Integration × 2
- Deployment × 1
- Stage × 1

### Lambda（6個）
- Lambda Function × 5（api_handler、guardrails_check、kb_query、bedrock_invoke、cache_response）
- Lambda Permission × 1（API Gateway呼び出し許可）

### Step Functions（1個）
- State Machine × 1（RAGワークフロー）

### DynamoDB（1個）
- Table × 1（キャッシュテーブル）

### S3（4個）
- Bucket × 1
- Bucket Versioning × 1
- Public Access Block × 1
- Object × 1（Lambda ZIPファイル）

### IAM（7個）
- Role × 2（Lambda実行ロール、Step Functions実行ロール）
- Role Policy × 5（Bedrock、DynamoDB、Step Functions、CloudWatch Logs、Lambda呼び出し）

### CloudWatch Logs（5個）
- Log Group × 5（各Lambda関数用）

**合計**: 約30個のリソース

---

## 🔍 リソースの依存関係

主要な依存関係の流れ：

```
S3 Bucket (Lambda ZIPファイル)
 └─> Lambda Functions (5個)
      └─> IAM Role (実行ロール)
           └─> IAM Policies (Bedrock、DynamoDB、Step Functions、Logs)

Lambda Functions
 └─> Step Functions State Machine
      └─> IAM Role (Step Functions実行ロール)
           └─> IAM Policy (Lambda呼び出し)

Lambda (api_handler)
 └─> API Gateway
      └─> REST API
           └─> Resource (/query)
                └─> Method (POST)
                     └─> Integration (Lambda)

Lambda Functions
 └─> CloudWatch Log Groups (5個)

Lambda Functions
 └─> DynamoDB Table (キャッシュ)
```

---

## 📝 カスタマイズ方法

### よくあるカスタマイズ例

#### 1. リージョンを変更

```hcl
# terraform.tfvars
aws_region = "us-east-1"
```

#### 2. Lambda関数のリソースを増強

```hcl
# terraform.tfvars
lambda_memory_size = 1024  # 1 GB
lambda_timeout     = 600   # 10分
```

#### 3. キャッシュTTLを変更

```hcl
# terraform.tfvars
cache_ttl_seconds = 3600  # 1時間
```

#### 4. ログ保持期間を変更

```hcl
# terraform.tfvars
log_retention_days = 7  # 7日間
```

#### 5. 本番環境用の設定

```hcl
# terraform.tfvars
environment        = "prod"
project_name       = "bedrock-rag-prod"
lambda_memory_size = 1024
log_retention_days = 90
```

---

## ⚠️ 注意事項

### 1. Bedrockリソースの手動作成

**重要**: 以下のリソースは事前に手動作成が必要です：
- **Knowledge Base**: AWS Console で作成（SETUP.md参照）
- **Guardrails**: AWS Console で作成（SETUP.md参照）

作成後、IDを`terraform.tfvars`に設定：
```hcl
knowledge_base_id = "YOUR_KB_ID"
guardrails_id     = "YOUR_GUARDRAILS_ID"
```

### 2. State管理

- 現在はローカルにstateファイルを保存（`terraform.tfstate`）
- **本番環境では**: S3バックエンド + DynamoDBロックを推奨

```hcl
# backend.tf（本番環境用）
terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "bedrock-rag/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "terraform-lock"
    encrypt        = true
  }
}
```

### 3. 機密情報の管理

- `terraform.tfvars`をGitにコミットしない（.gitignoreで除外済み）
- Knowledge Base IDとGuardrails IDは機密情報ではないが、環境固有の情報
- AWS認証情報は環境変数やAWS CLI設定を使用

### 4. リソース削除時の注意

`terraform destroy`実行前の確認事項：
- S3バケットにLambda ZIPファイルが残っている（`force_destroy = true`で自動削除）
- DynamoDBテーブルのデータは削除される（バックアップ不要の場合のみ実行）
- **Knowledge BaseとGuardrailsは削除されません**（手動削除が必要）

### 5. コスト

**主な課金対象**:
- Lambda: 実行時間とメモリに応じた従量課金
- API Gateway: APIリクエスト数に応じた従量課金
- DynamoDB: オンデマンド課金（リクエスト数とストレージ）
- S3: ストレージとリクエスト数
- CloudWatch Logs: ログストレージ
- Bedrock: モデル呼び出しとKnowledge Base検索

**アイドル時コスト**: ほぼゼロ（サーバーレス構成）

**テスト後の削除**: `./scripts/destroy.sh`で全リソース削除推奨

---

## 🔗 関連ドキュメント

- **[README.md](README.md)** - プロジェクト全体の概要
- **[docs/SETUP.md](docs/SETUP.md)** - Bedrockリソースのセットアップ手順
- **[DIRECTORY_STRUCTURE.md](DIRECTORY_STRUCTURE.md)** - プロジェクト構造の詳細
- **[Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)** - 公式ドキュメント
- **[AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)** - Bedrock公式ドキュメント

---

## 📚 参考: Terraformの基本コマンド

| コマンド | 説明 |
|---------|------|
| `terraform init` | プロバイダーのダウンロードと初期化 |
| `terraform fmt` | コードのフォーマット整形 |
| `terraform validate` | 構文チェック |
| `terraform plan` | 実行計画の確認（変更内容のプレビュー） |
| `terraform apply` | リソースのデプロイ |
| `terraform destroy` | リソースの削除 |
| `terraform output` | 出力値の表示 |
| `terraform show` | 現在のstateを表示 |
| `terraform state list` | 管理中のリソース一覧 |
| `terraform state show <resource>` | 特定リソースの詳細表示 |

---

このドキュメントにより、Terraformディレクトリ内の各ファイルの役割と内容を理解できます。実際の運用では、[docs/SETUP.md](docs/SETUP.md)を参照して、ステップバイステップでデプロイを進めてください。
