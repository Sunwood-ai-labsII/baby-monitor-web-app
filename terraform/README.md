# Google Cloud VM Terraform 構成ガイド

この Terraform 構成は、Google Compute Engine 上に単一の VM と、SSH 接続に必要なネットワークリソース一式をまとめて作成するよ。プロジェクトの設定値・認証情報・SSH 鍵を差し替えるだけで、すぐにインスタンスを起動できるようファイルを整理してあるんだ✨

## 📁 リポジトリ構成

- `main.tf` – ネットワーク、ファイアウォール、固定 IP、Compute Engine インスタンスなど主要リソース
- `variables.tf` – デプロイをカスタマイズするための入力変数
- `outputs.tf` – 外部 IP や便利な SSH コマンドなどの出力値
- `terraform.tfvars.example` – 変数定義のサンプル。`terraform.tfvars` にコピーして環境に合わせて編集してね

## ✅ 事前準備

1. ローカルに **Terraform v1.3.0 以上** がインストールされていること
2. **Compute Engine API が有効な Google Cloud プロジェクト**
3. Compute Engine・VPC ネットワーク・ファイアウォールを操作できる **サービスアカウントの JSON キー**。安全に保管しつつ、`credentials_file` 変数にパスを指定してね
4. **SSH 鍵ペア**（OpenSSH 形式）。公開鍵と、VM 上でその鍵を持つユーザー名を用意するよ

## 🚀 使い方

1. リポジトリ内の Terraform ディレクトリへ移動：

   ```bash
   cd terraform
   ```

2. 変数ファイルのサンプルをコピーして値を編集：

   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # お好みのエディタで terraform.tfvars を編集
   ```

3. Terraform の作業ディレクトリを初期化：

   ```bash
   terraform init
   ```

4. 作成予定のリソースを確認：

   ```bash
   terraform plan
   ```

5. 構成を適用してリソースをデプロイ：

   ```bash
   terraform apply
   ```

   プロンプトが表示されたら `yes` で確定してね。プロビジョニングが完了すると、VM の外部 IP と SSH コマンドが出力されるよ。

6. 表示されたコマンドで VM に SSH 接続：

   ```bash
   ssh <ssh_username>@<public_ip>
   ```

## 🔒 セキュリティのポイント

- `ssh_source_ranges` は可能な限り信頼できる IP 範囲に絞り、インターネット全体に開放しないようにしよう
- 不要になったサービスアカウントキーは速やかにローテーションまたは失効させる
- スタートアップスクリプトを使う場合は、信頼できる処理のみを記述してね

## 🧹 クリーンアップ

検証が終わったら、課金が続かないよう必ずリソースを削除しよう：

```bash
terraform destroy
```

プロンプトが表示されたら実行を確定して、作成したリソースをすべて削除してね。

