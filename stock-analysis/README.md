# Stock Analysis

日本株の銘柄分析・スクリーニング自動化プロジェクトです。

## 目的
- 長期投資目線で日本株のファンダメンタルズを分析
- 銘柄一覧を管理し、スクリーニング条件で絞り込む
- データ取得とレポート生成を自動化する

## ディレクトリ構成
- `config/` : 設定ファイル（監視リスト、スクリーニング条件）
- `data/raw/` : 取得した生データ
- `data/processed/` : 加工済みデータ
- `scripts/` : データ取得・分析スクリプト
- `reports/` : 生成レポート
- `portfolio/` : 保有銘柄・損益記録

## セットアップ
1. Python 3.11 以上をインストール
2. 仮想環境を作成し、有効化
3. `pip install -r requirements.txt`
4. `cp .env.example .env` して環境変数を設定

## 実行方法
- データ取得: `python scripts/fetch_stock_data.py`
- レポート生成: `python scripts/generate_report.py`
- フルパイプライン: `python scripts/run_pipeline.py`

## 出力先
- `data/raw/` : 取得した JSON データ
- `data/processed/summary.csv` : 全銘柄のサマリー
- `data/processed/screened.csv` : スクリーニング合格銘柄
- `reports/screening_report.md` : スクリーン結果レポート
- `reports/screened_symbols.txt` : 合格銘柄リスト
