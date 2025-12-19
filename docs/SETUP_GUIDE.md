# セットアップガイド

このドキュメントでは、Bedrock RAG Learning Project の初回セットアップ手順を説明します。
本ガイドに従って、AWS Bedrock を使用した RAG（Retrieval-Augmented Generation）システムを構築し、動作確認まで完了できます。

## 📖 目次

セットアップガイドでは、以下の内容を説明しています：

1. **クイックスタート**
   - すぐに試したい方向けの簡易手順

2. **前提条件**
   - 必要なツールのインストール（Terraform、Python、AWS CLI）
   - AWS認証情報の設定
   - Bedrockサービスアクセスの確認

3. **セットアップ手順**
   - ステップ1: 環境検証
   - ステップ2: Bedrockモデルアクセスの有効化
   - ステップ3: Knowledge Baseの作成（手動）
   - ステップ4: Guardrailsの作成（手動）
   - ステップ5: Terraform変数の設定
   - ステップ6: インフラのデプロイ
   - ステップ7: デプロイの検証
   - ステップ8: APIのテスト

4. **クリーンアップ**
   - リソースの削除手順
   - コスト削減のための完全クリーンアップ

5. **トラブルシューティング**
   - よくある問題と解決方法
   - ログの確認方法
   - デバッグ手順

6. **参考情報**
   - コスト見積もり
   - デフォルト設定値
   - アーキテクチャ概要

---

## 🚀 クイックスタート

すぐに試したい方向けの簡易手順：

```bash
# 1. 環境検証
./scripts/validate.sh

# 2. AWS Bedrock Console で以下を手動作成:
#    - Claude 3 Haiku のモデルアクセスを有効化
#    - Knowledge Base を作成（IDをメモ）
#    - Guardrails を作成（IDをメモ）

# 3. Terraform変数を設定
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# terraform.tfvars を編集して knowledge_base_id と guardrails_id を設定

# 4. インフラをデプロイ
./scripts/deploy.sh

# 5. APIをテスト
./scripts/test_api.sh "What is AWS Bedrock?"
```

**注意**: クイックスタートでは詳細を省略しています。初めての方は「セットアップ手順」セクションを参照してください。

---

## 📋 前提条件

以下のツールがインストールされていることを確認してください：

### 必須ツール

| ツール | バージョン | 確認コマンド | インストール方法 |
|--------|-----------|------------|----------------|
| **AWS CLI** | >= 2.0 | `aws --version` | [公式サイト](https://aws.amazon.com/cli/) |
| **Terraform** | >= 1.5 | `terraform version` | [公式サイト](https://www.terraform.io/downloads) |
| **Python** | >= 3.11 | `python3 --version` | [公式サイト](https://www.python.org/downloads/) |
| **pip** | >= 20.0 | `pip3 --version` | Pythonに同梱 |

### オプションツール

| ツール | 用途 | 確認コマンド | インストール方法 |
|--------|------|------------|----------------|
| **jq** | JSONレスポンスの整形 | `jq --version` | `apt install jq` / `brew install jq` |

### AWS認証情報の設定

AWS CLIが認証情報を使用できるように設定します：

```bash
# 認証情報の設定（まだ設定していない場合）
aws configure

# 入力が求められる項目:
# - AWS Access Key ID: <YOUR_ACCESS_KEY>
# - AWS Secret Access Key: <YOUR_SECRET_KEY>
# - Default region name: ap-northeast-1
# - Default output format: json

# 認証情報の確認
aws sts get-caller-identity
```

出力例：
```json
{
    "UserId": "AIDACKCEVSQ6C2EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-username"
}
```

### AWS Bedrock アクセス

Bedrockサービスが利用可能なリージョンを使用してください：
- **推奨**: `ap-northeast-1` (東京)
- その他: `us-east-1`, `us-west-2` など

**重要**: Bedrock にアクセスするには、AWSアカウントで Bedrock サービスが有効になっている必要があります。

---

## 🔧 セットアップ手順

### ステップ1: 環境検証

まず、環境が整っているか検証スクリプトで確認します：

```bash
# プロジェクトルートで実行
./scripts/validate.sh
```

このスクリプトは以下を確認します：
- [1/7] AWS CLI のインストール
- [2/7] AWS 認証情報の設定
- [3/7] Terraform のインストール
- [4/7] Python のインストール
- [5/7] pip のインストール
- [6/7] terraform.tfvars の存在と設定
- [7/7] Bedrock モデルアクセス

**出力例（成功）**：
```
=================================== ✓ Validation passed!
===================================

Ready to deploy:
  ./scripts/deploy.sh
```

**エラーが出る場合**:
- 不足しているツールをインストール
- AWS認証情報を設定
- 後述のステップで terraform.tfvars を作成

---

### ステップ2: Bedrock モデルアクセスの有効化

AWS Bedrock Console でモデルアクセスを有効化します：

#### 2-1. Bedrock Console にアクセス

1. AWS Management Console にログイン
2. リージョンを **ap-northeast-1** (東京) に変更
3. サービス検索で「Bedrock」を検索
4. Amazon Bedrock Console を開く

#### 2-2. モデルアクセスを有効化

1. 左サイドバーの **「Model access」** をクリック
2. 右上の **「Manage model access」** または **「Enable specific models」** をクリック
3. モデル一覧から以下を選択:
   - ✅ **Anthropic Claude 3 Haiku**
   - ✅ **Amazon Titan Embeddings G1 - Text** (Knowledge Base 用)
4. 下部の **「Save changes」** または **「Request model access」** をクリック
5. ステータスが **「Access granted」** になるまで待つ（通常1-2分）

**確認方法**：
```bash
# Claude 3 Haiku のアクセスを確認
aws bedrock list-foundation-models \
  --region ap-northeast-1 \
  --by-provider anthropic \
  --query 'modelSummaries[?modelId==`anthropic.claude-3-haiku-20240307-v1:0`]' \
  --output table
```

---

### ステップ3: Knowledge Base の作成

Bedrock Knowledge Base を手動で作成します。

#### 3-1. S3バケットの準備（オプション）

Knowledge Base のデータソースとして S3 バケットを使用する場合：

```bash
# アカウントIDを取得
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# S3バケットを作成
aws s3 mb s3://bedrock-rag-kb-data-${AWS_ACCOUNT_ID} --region ap-northeast-1

# サンプルドキュメントをアップロード
aws s3 cp sample-docs/ s3://bedrock-rag-kb-data-${AWS_ACCOUNT_ID}/ --recursive
```

**注意**: S3バケット名はグローバルで一意である必要があります。アカウントIDを含めることで重複を防ぎます。

#### 3-2. Bedrock Console で Knowledge Base を作成

1. **Bedrock Console → 左サイドバー「Knowledge bases」→「Create knowledge base」**

2. **Knowledge base details**:
   - Knowledge base name: `bedrock-rag-learning-kb`
   - Description: `Learning project for RAG with Bedrock`
   - IAM role: **「Create and use a new service role」** を選択
   - 次へ

3. **Data source**:
   - Data source name: `bedrock-rag-data-source`
   - S3 URI: `s3://bedrock-rag-kb-data-${AWS_ACCOUNT_ID}/`（手順3-1で作成）
   - Chunking strategy: **Default chunking** (300 tokens, 20% overlap)
   - 次へ

4. **Embeddings model**:
   - Embeddings model: **Titan Embeddings G1 - Text**
   - Vector database: **Quick create a new vector store**
   - 次へ

5. **Review and create**:
   - 設定を確認
   - **「Create knowledge base」** をクリック

6. **データソースの同期**:
   - 作成完了後、**「Sync」** ボタンをクリック
   - 同期が完了するまで待つ（数分）

7. **Knowledge Base ID をコピー**:
   - Knowledge base の詳細ページで **Knowledge base ID** を確認
   - 形式: `XXXXXXXXXX` (10文字の英数字)
   - **このIDをメモしてください**（後で使用します）

**確認方法**：
```bash
# Knowledge Base 一覧を確認
aws bedrock-agent list-knowledge-bases --region ap-northeast-1 --output table
```

---

### ステップ4: Guardrails の作成

Bedrock Guardrails を手動で作成します。

#### 4-1. Bedrock Console で Guardrails を作成

1. **Bedrock Console → 左サイドバー「Guardrails」→「Create guardrail」**

2. **Guardrail details**:
   - Name: `bedrock-rag-learning-guardrail`
   - Description: `Content safety for RAG learning project`
   - 次へ

3. **Content filters** (コンテンツフィルター設定):

   以下の項目をそれぞれ設定します：

   | フィルタータイプ | 強度 | 説明 |
   |---------------|------|------|
   | Hate speech（ヘイトスピーチ） | Medium | 憎悪表現の検出 |
   | Insults（侮辱） | Medium | 侮辱的表現の検出 |
   | Sexual content（性的コンテンツ） | Medium | 性的な内容の検出 |
   | Violence（暴力） | Medium | 暴力的な内容の検出 |
   | Misconduct（不正行為） | Medium | 不正行為の検出 |

   **強度の選択**:
   - **Low**: 最も許容的（誤検知が少ない）
   - **Medium**: バランス型（推奨）
   - **High**: 最も厳格（誤検知が多い可能性）

4. **Denied topics** (拒否トピック - オプション):
   - 特定のトピックを拒否したい場合に設定
   - 学習用途では設定不要（スキップ可）
   - 次へ

5. **Sensitive information filters** (機密情報フィルター - オプション):
   - PII（個人情報）検出を有効化する場合に設定
   - 例: メールアドレス、電話番号、クレジットカード番号
   - 学習用途では設定不要（スキップ可）
   - 次へ

6. **Review and create**:
   - 設定を確認
   - **「Create guardrail」** をクリック

7. **Guardrail ID をコピー**:
   - 作成完了後、Guardrail の詳細ページで **Guardrail ID** を確認
   - 形式: `xxxxxxxxxxxx` (12文字の英数字)
   - **Version**: `DRAFT` または `1`
   - **このIDをメモしてください**（後で使用します）

**確認方法**：
```bash
# Guardrails 一覧を確認
aws bedrock list-guardrails --region ap-northeast-1 --output table
```

---

### ステップ5: Terraform 変数の設定

Knowledge Base ID と Guardrails ID を Terraform に設定します。

#### 5-1. terraform.tfvars ファイルの作成

```bash
# サンプルファイルをコピー
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
```

#### 5-2. terraform.tfvars の編集

エディタで `terraform/terraform.tfvars` を開き、以下を設定します：

```hcl
# Project Configuration
aws_region   = "ap-northeast-1"  # 東京リージョン
project_name = "bedrock-rag"
environment  = "dev"

# Bedrock Resources (ステップ3とステップ4で取得したIDを設定)
knowledge_base_id = "XXXXXXXXXX"      # ステップ3で取得した Knowledge Base ID
guardrails_id     = "xxxxxxxxxxxx"    # ステップ4で取得した Guardrails ID
```

**重要**:
- `knowledge_base_id` と `guardrails_id` を**必ず設定**してください
- IDは引用符で囲みます（例: `"JTFYBA8V1S"`）
- 設定しないと、Lambda関数がBedrockリソースにアクセスできません

#### 5-3. 設定の確認

```bash
# 設定内容を確認
cat terraform/terraform.tfvars
```

---

### ステップ6: インフラのデプロイ

デプロイスクリプトを使用して、Lambda パッケージのビルドと Terraform デプロイを一括実行します。

#### 6-1. デプロイスクリプトの実行

```bash
# プロジェクトルートで実行
./scripts/deploy.sh
```

このスクリプトは以下を自動実行します：
1. `terraform.tfvars` の存在確認
2. Lambda 関数のパッケージング（`package_lambdas.sh`）
3. Terraform の初期化（`terraform init`）
4. インフラのデプロイ（`terraform apply`）

#### 6-2. デプロイ内容の確認

Terraform が実行計画を表示します。以下のリソースが作成されることを確認してください：

**主要リソース**:
- API Gateway REST API × 1
- Lambda Functions × 5（api_handler, guardrails_check, kb_query, bedrock_invoke, cache_response）
- Step Functions State Machine × 1
- DynamoDB Table × 1（キャッシュ用）
- S3 Bucket × 1（Lambda デプロイパッケージ用）
- IAM Roles and Policies × 7
- CloudWatch Log Groups × 5

**合計**: 約30個のリソース

#### 6-3. デプロイの承認

```
Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value:
```

`yes` を入力してEnterキーを押します。

#### 6-4. デプロイの完了待ち

デプロイには約5-10分かかります。完了すると以下のような出力が表示されます：

```
Apply complete! Resources: 30 added, 0 changed, 0 destroyed.

Outputs:

api_gateway_url = "https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/dev/query"
cache_table_arn = "arn:aws:dynamodb:ap-northeast-1:123456789012:table/bedrock-rag-dev-cache"
cache_table_name = "bedrock-rag-dev-cache"
project_info = {
  environment = "dev"
  project_name = "bedrock-rag"
  region = "ap-northeast-1"
}

===================================
Deployment complete!
===================================

API Endpoint:
https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/dev/query

Test with:
./scripts/test_api.sh "What is AWS Bedrock?"
```

#### 6-5. API エンドポイントの保存

後で使用するため、API Gateway URL を環境変数に保存します（オプション）：

```bash
export API_URL=$(terraform -chdir=terraform output -raw api_gateway_url)
echo "API URL: $API_URL"
```

---

### ステップ7: デプロイの検証

#### 7-1. Lambda 関数の確認

```bash
# Lambda 関数一覧を確認
aws lambda list-functions \
  --region ap-northeast-1 \
  --query 'Functions[?starts_with(FunctionName, `bedrock-rag`)].FunctionName' \
  --output table
```

期待される出力（5つの関数）：
```
-------------------------------------------
|              ListFunctions              |
+-----------------------------------------+
|  bedrock-rag-api-handler-dev           |
|  bedrock-rag-bedrock-invoke-dev        |
|  bedrock-rag-cache-response-dev        |
|  bedrock-rag-guardrails-check-dev      |
|  bedrock-rag-kb-query-dev              |
+-----------------------------------------+
```

#### 7-2. Step Functions の確認

```bash
# Step Functions ステートマシンを確認
aws stepfunctions list-state-machines \
  --region ap-northeast-1 \
  --query 'stateMachines[?starts_with(name, `bedrock-rag`)].name' \
  --output table
```

#### 7-3. DynamoDB テーブルの確認

```bash
# DynamoDB テーブルを確認
aws dynamodb list-tables \
  --region ap-northeast-1 \
  --query 'TableNames[?starts_with(@, `bedrock-rag`)]' \
  --output table
```

---

### ステップ8: API のテスト

#### 8-1. テストスクリプトの実行

```bash
# デフォルトクエリでテスト
./scripts/test_api.sh

# カスタムクエリでテスト
./scripts/test_api.sh "What is Amazon Bedrock?"
```

#### 8-2. 期待される出力

**成功時のレスポンス例**:
```json
{
  "answer": "Amazon Bedrock は、高性能な基盤モデル（FM）を提供するフルマネージドサービスです...",
  "sources": [
    {
      "content": "AWS Bedrock は...",
      "score": 0.85
    }
  ],
  "cached": false,
  "processing_time_ms": 3245.67
}
```

**レスポンスの説明**:
- `answer`: Claude 3 Haiku が生成した回答
- `sources`: Knowledge Base から取得した関連ドキュメント
- `cached`: キャッシュが使用されたか（2回目以降は `true`）
- `processing_time_ms`: 処理時間（ミリ秒）

#### 8-3. curl による手動テスト

```bash
# API URL を取得
API_URL=$(terraform -chdir=terraform output -raw api_gateway_url)

# POST リクエストを送信
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AWS Bedrock?"}' | python3 -m json.tool
```

#### 8-4. キャッシュ動作の確認

同じクエリを2回実行して、キャッシュが機能していることを確認します：

```bash
# 1回目（キャッシュなし）
./scripts/test_api.sh "What is AWS Bedrock?"
# → "cached": false, 処理時間: 約3000ms

# 2回目（キャッシュあり）
./scripts/test_api.sh "What is AWS Bedrock?"
# → "cached": true, 処理時間: 約100ms
```

#### 8-5. Guardrails 動作の確認

不適切なコンテンツが検出されることを確認します：

```bash
# 不適切な内容でテスト（Guardrails がブロックするはず）
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"query": "How to hack a system?"}' | python3 -m json.tool
```

期待される出力（Guardrails ブロック）:
```json
{
  "error": "Content blocked by Guardrails",
  "type": "GuardrailsError"
}
```

#### 8-6. CloudWatch Logs の確認

```bash
# API Handler のログを確認
aws logs tail /aws/lambda/bedrock-rag-api-handler-dev \
  --region ap-northeast-1 \
  --follow

# Ctrl+C でログ監視を終了
```

---

## 🧹 クリーンアップ

使用後は、リソースを削除して AWS 利用料金を削減します。

### ステップ1: Terraform でインフラを削除

```bash
# 削除スクリプトを実行
./scripts/destroy.sh
```

または、手動で削除：

```bash
cd terraform

# インフラを削除
terraform destroy

# 確認プロンプトで "yes" を入力
```

削除には約5分かかります。

### ステップ2: 手動作成したリソースの削除

Terraform では削除されないリソースを手動で削除します：

#### 2-1. Knowledge Base の削除

**AWS Console**:
1. Bedrock Console → Knowledge bases
2. 作成した Knowledge Base を選択
3. **「Delete」** をクリック

**AWS CLI**:
```bash
# Knowledge Base ID を確認
aws bedrock-agent list-knowledge-bases --region ap-northeast-1

# Knowledge Base を削除
aws bedrock-agent delete-knowledge-base \
  --knowledge-base-id XXXXXXXXXX \
  --region ap-northeast-1
```

#### 2-2. Guardrails の削除

**AWS Console**:
1. Bedrock Console → Guardrails
2. 作成した Guardrail を選択
3. **「Delete」** をクリック

**AWS CLI**:
```bash
# Guardrails ID を確認
aws bedrock list-guardrails --region ap-northeast-1

# Guardrail を削除
aws bedrock delete-guardrail \
  --guardrail-identifier xxxxxxxxxxxx \
  --region ap-northeast-1
```

#### 2-3. OpenSearch Serverless コレクションの削除

Knowledge Base で作成された Vector Store を削除します：

```bash
# OpenSearch Serverless コレクション一覧を確認
aws opensearchserverless list-collections --region ap-northeast-1

# コレクションを削除（コレクションIDを確認して実行）
aws opensearchserverless delete-collection \
  --id <COLLECTION_ID> \
  --region ap-northeast-1
```

#### 2-4. S3 バケットの削除

Knowledge Base のデータソース用 S3 バケットを削除します：

```bash
# バケット内のオブジェクトを削除
aws s3 rm s3://bedrock-rag-kb-data-${AWS_ACCOUNT_ID}/ --recursive

# バケットを削除
aws s3 rb s3://bedrock-rag-kb-data-${AWS_ACCOUNT_ID}
```

### ステップ3: クリーンアップの確認

```bash
# Lambda 関数が削除されたことを確認
aws lambda list-functions \
  --region ap-northeast-1 \
  --query 'Functions[?starts_with(FunctionName, `bedrock-rag`)].FunctionName'
# → 空の配列 [] が返ればOK

# DynamoDB テーブルが削除されたことを確認
aws dynamodb list-tables \
  --region ap-northeast-1 \
  --query 'TableNames[?starts_with(@, `bedrock-rag`)]'
# → 空の配列 [] が返ればOK

# S3 バケットが削除されたことを確認
aws s3 ls | grep bedrock-rag
# → 何も表示されなければOK
```

すべてのコマンドで空の結果が返れば、クリーンアップ完了です。

---

## 🔧 トラブルシューティング

### 問題1: terraform.tfvars が見つからない

**症状**: `./scripts/deploy.sh` 実行時に以下のエラーが出る
```
ERROR: terraform/terraform.tfvars not found!
```

**原因**: terraform.tfvars ファイルが作成されていない

**対処**:
```bash
# サンプルファイルをコピー
cp terraform/terraform.tfvars.example terraform/terraform.tfvars

# エディタで編集して knowledge_base_id と guardrails_id を設定
vim terraform/terraform.tfvars
```

---

### 問題2: Knowledge Base ID または Guardrails ID が無効

**症状**: Lambda 関数実行時に以下のエラーが出る
```
{
  "error": "Resource not found",
  "type": "ResourceNotFoundException"
}
```

**原因**: terraform.tfvars に設定したIDが間違っているか、リソースが存在しない

**対処**:
```bash
# Knowledge Base ID を確認
aws bedrock-agent list-knowledge-bases --region ap-northeast-1

# Guardrails ID を確認
aws bedrock list-guardrails --region ap-northeast-1

# terraform.tfvars を修正
vim terraform/terraform.tfvars

# 再デプロイ
cd terraform
terraform apply
```

---

### 問題3: Bedrock モデルアクセスが拒否される

**症状**: API テスト時に以下のエラーが出る
```
{
  "error": "You don't have access to the model",
  "type": "AccessDeniedException"
}
```

**原因**: Claude 3 Haiku のモデルアクセスが有効化されていない

**対処**:
1. Bedrock Console → Model access
2. Claude 3 Haiku のステータスを確認
3. 「Access granted」でない場合、「Enable specific models」から有効化
4. 数分待ってから再テスト

---

### 問題4: Lambda がタイムアウトする

**症状**: API レスポンスが遅い、またはタイムアウトエラーが出る

**原因**: Bedrock API の応答が遅い、またはネットワークの問題

**対処**:
```bash
# CloudWatch Logs でエラー内容を確認
aws logs tail /aws/lambda/bedrock-rag-bedrock-invoke-dev \
  --region ap-northeast-1 \
  --since 10m

# Lambda タイムアウトを延長する場合（terraform/variables.tf を編集）
lambda_timeout = 600  # 10分に延長

# 再デプロイ
cd terraform
terraform apply
```

---

### 問題5: Knowledge Base の同期が失敗する

**症状**: Knowledge Base の同期ステータスが「Failed」になる

**原因**: S3バケットへのアクセス権限が不足している

**対処**:
```bash
# S3 バケットの存在確認
aws s3 ls s3://bedrock-rag-kb-data-${AWS_ACCOUNT_ID}/

# IAM ロールの確認（Bedrock Console で確認）
# Knowledge Base の IAM ロールに s3:GetObject 権限があるか確認

# 再同期
# Bedrock Console → Knowledge bases → Sync をクリック
```

---

### 問題6: API Gateway エンドポイントが404を返す

**症状**: `curl` コマンドが 404 Not Found を返す

**原因**: API Gateway のデプロイメントが完了していない

**対処**:
```bash
# API Gateway の確認
aws apigateway get-rest-apis --region ap-northeast-1

# ステージの確認
aws apigateway get-stages \
  --rest-api-id <API_ID> \
  --region ap-northeast-1

# Terraform で再デプロイ
cd terraform
terraform apply
```

---

### 問題7: DynamoDB キャッシュが機能しない

**症状**: 同じクエリを実行しても `"cached": false` のまま

**原因**: キャッシュの書き込みに失敗している

**対処**:
```bash
# DynamoDB テーブルの確認
aws dynamodb scan \
  --table-name bedrock-rag-dev-cache \
  --region ap-northeast-1 \
  --limit 5

# CloudWatch Logs で cache_response 関数のログを確認
aws logs tail /aws/lambda/bedrock-rag-cache-response-dev \
  --region ap-northeast-1 \
  --since 10m

# IAM ポリシーの確認（Lambda に dynamodb:PutItem 権限があるか）
```

---

## 📚 参考情報

### コスト見積もり

このシステムを運用した場合の概算コスト（ap-northeast-1 リージョン）：

#### クエリあたりのコスト（1クエリ）

| サービス | 使用量 | 単価 | 費用 |
|---------|--------|------|------|
| **API Gateway** | 1リクエスト | $0.0000035/リクエスト | $0.0000035 |
| **Lambda (api_handler)** | 100ms実行 | $0.0000002/100ms | $0.0000002 |
| **Step Functions** | 5ステート遷移 | $0.000025/遷移 | $0.000125 |
| **Lambda (guardrails_check)** | 200ms実行 | $0.0000002/100ms | $0.0000004 |
| **Lambda (kb_query)** | 500ms実行 | $0.0000002/100ms | $0.000001 |
| **Lambda (bedrock_invoke)** | 2000ms実行 | $0.0000002/100ms | $0.000004 |
| **Lambda (cache_response)** | 100ms実行 | $0.0000002/100ms | $0.0000002 |
| **Bedrock Knowledge Base** | 1クエリ | $0.00001/クエリ | $0.00001 |
| **Bedrock Claude 3 Haiku** | 1000トークン入力<br>500トークン出力 | $0.00025/1K入力<br>$0.00125/1K出力 | $0.00025<br>$0.000625 |
| **DynamoDB** | 1読み取り<br>1書き込み | $0.00000025/RCU<br>$0.00000125/WCU | $0.0000015 |
| **CloudWatch Logs** | 1KB取り込み | $0.0005/GB | 約$0.0000005 |
| **合計** | - | - | **約$0.0011 USD** |

#### 月間コスト見積もり（使用量別）

| 使用量 | クエリ数/月 | 月額コスト | 備考 |
|--------|-----------|-----------|------|
| **軽量使用** | 1,000 | 約$1.10 | 1日約33クエリ |
| **中程度使用** | 10,000 | 約$11.00 | 1日約333クエリ |
| **重度使用** | 100,000 | 約$110.00 | 1日約3,333クエリ |

**アイドル時コスト**: **$0/日**（サーバーレス、完全従量課金）

**注意事項**:
- キャッシュヒット時は Bedrock API 呼び出しがスキップされ、コストが大幅に削減されます
- OpenSearch Serverless（Knowledge Base のベクトルDB）には別途月額コストが発生します（約$50-100/月）
- データ転送費用は別途発生します

---

### デフォルト設定値

| 項目 | デフォルト値 | 説明 |
|------|------------|------|
| **AWS Region** | ap-northeast-1 | 東京リージョン |
| **Project Name** | bedrock-rag | プロジェクト名（リソース名のプレフィックス） |
| **Environment** | dev | 環境名 |
| **Lambda Memory** | 512 MB | Lambda 関数のメモリサイズ |
| **Lambda Timeout** | 300秒 | Lambda 関数のタイムアウト |
| **Cache TTL** | 86400秒 | DynamoDB キャッシュのTTL（24時間） |
| **Log Retention** | 30日 | CloudWatch Logs の保持期間 |
| **Bedrock Model** | Claude 3 Haiku | 回答生成モデル |
| **Embedding Model** | Titan Embeddings G1 | Knowledge Base 埋め込みモデル |
| **Chunking Strategy** | Default | 300トークン、20%オーバーラップ |
| **Guardrails Level** | Medium | コンテンツフィルターの強度 |

---

### アーキテクチャ概要

```
                 ┌─────────────────┐
                 │  User / Client  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  API Gateway    │
                 │   (REST API)    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Lambda:         │
                 │ api_handler     │◄───── Check cache (DynamoDB)
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Step Functions  │
                 │  (RAG Workflow) │
                 └────────┬────────┘
                          │
          ┌───────────────┼───────────────┬────────────────┐
          ▼               ▼               ▼                ▼
  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
  │ Lambda:      │ │ Lambda:      │ │ Lambda:      │ │ Lambda:      │
  │ guardrails_  │ │ kb_query     │ │ bedrock_     │ │ cache_       │
  │ check        │ │              │ │ invoke       │ │ response     │
  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
         │                │                │                │
         ▼                ▼                ▼                ▼
  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
  │ Bedrock      │ │ Bedrock      │ │ Bedrock      │ │  DynamoDB    │
  │ Guardrails   │ │ Knowledge    │ │ Claude 3     │ │  (Cache)     │
  │              │ │ Base         │ │ Haiku        │ │              │
  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │ OpenSearch   │
                   │ Serverless   │
                   │ (Vector DB)  │
                   └──────────────┘
```

**ワークフローの流れ**:
1. **API Gateway**: HTTPリクエストを受信
2. **api_handler**: キャッシュをチェック → Step Functions を起動
3. **guardrails_check**: 入力コンテンツの安全性チェック
4. **kb_query**: Knowledge Base から関連ドキュメントを検索
5. **bedrock_invoke**: Claude 3 Haiku で回答生成（出力Guardrailsチェック含む）
6. **cache_response**: 結果を DynamoDB にキャッシュ
7. **api_handler**: クライアントにレスポンスを返す

---

このガイドを完了すると、AWS Bedrock を使用した本格的な RAG システムが構築されます。不明な点があれば、[README.md](../README.md) や [TERRAFORM_GUIDE.md](../terraform/TERRAFORM_GUIDE.md) も参照してください。
