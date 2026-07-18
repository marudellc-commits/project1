# xbizサーバー（xb134062）マルウェアチェック記録（2026-07-19）

xb134062.xbiz.jp（実体: sv163.xbiz.ne.jp、SSHユーザー: xb134062）配下の約44サイトについて、SSH経由でマルウェアチェックを実施。

## サーバー概要

- 神戸エリアの店舗・法人サイトを中心に約44のWordPressサイトを収容するマルチサイト構成
- 2025年12月〜2026年6月にかけて、このサーバー固有の侵害インシデントが過去に発生していた形跡あり（`_quarantine/`隔離フォルダ、`wp_recovery_backup/`、既存のスキャンスクリプト`wp_security_check.sh`等が残存）
- システムのデフォルトPHP CLIは5.4系で古く、wp-cli実行時は`/usr/bin/php8.2`等バージョン別バイナリを明示指定する必要がある

## チェック内容と結果

| 項目 | 結果 |
|------|------|
| 構造的Webシェル検索（`goto`難読化・`eval+base64_decode`等） | ライブサイト上はゼロ検出。ヒット7件は全て`_quarantine/`内（Web非公開、過去の隔離分） |
| 偽装「wp」ディレクトリ | `wp-content/uploads/`配下9箇所で発見（stazio54.com、seigororin-group.com×3、perform-kobe.com、nicebar-kobe.com、imuyak.jp×2、jandwnet.jp×2）。バックドア本体のPHPは既に削除済みで、特定ファイル名のみを許可する不正`.htaccess`の残骸のみ現存。該当ファイル名をサーバー全体で検索しても実体なし＝再侵入なし |
| crontab | 全ジョブがキャッシュ自動削除の定型パターンのみ。偽装永続化ジョブなし |
| パーミッション | 777ファイルなし。wp-config.phpは全サイト600で適正 |
| WPコア更新状況 | ikoi-llc.jp・carmax-kobe.comは7.0.2で最新。他22サイトは7.0.2への軽微な更新が未適用 |

## 重大発見：2サイトが停止中

**glt-trustee.com** と **aube73infinity.com** のwp-config.phpが、全行に誤って`exit;`が前置された状態になっており、サイトが完全にダウン中（HTTPレスポンスがリテラル文字列「exit;」5バイトのみ）。

- glt-trustee.com: wp-config.php更新日時 2025-12-12（過去のインシデント隔離作業と同時期）
- aube73infinity.com: wp-config.php更新日時 2026-06-02（前回スキャンと同日）
- ファイル内容を目視確認済み。マルウェアコードは含まれず、DB接続情報・認証キー・DISALLOW設定のみの正規の内容。過去のインシデント対応で緊急停止措置として`sed`等の一括置換を行った際に、誤って全行に`exit;`が付加されたまま放置されたと推測される
- 各行先頭の`exit;`を除去すれば復元可能だが、**2026-07-19時点ではユーザーの判断で復旧を保留**

## 対応内容

- 隔離フォルダ`_quarantine/`（2.7GB、約53,000ファイル、過去に隔離されたバックドアPHPの生データ）を`quarantine_evidence_20260719.tar.gz`（約1.99GB）に圧縮し、整合性確認後に元フォルダを削除
  - 一部ファイルはパーミッション000（削除耐性のための設定）になっており、`chmod -R u+rwX`で読み取り可能にしてから圧縮
  - アーカイブは`/home/xb134062/quarantine_evidence_20260719.tar.gz`に保管

## 残タスク

- [ ] glt-trustee.com / aube73infinity.comの復旧（`exit;`除去、ユーザー承認待ち）
- [ ] uploads配下の不正`.htaccess`残骸9箇所の削除
- [ ] 22サイトのWordPressコア更新（→7.0.2）
- [ ] 管理契約下の他サーバーへの同様の月次チェック展開（[Xserver不正アクセスインシデント対応記録](xserver-incident-202607.md)のsv6099.xserver.jpも対象）

## 教訓

- `wp core check-update`実行時に`Error: Strange wp-config.php file: wp-settings.php is not loaded directly.`が出た場合は、wp-config.phpが改変されている可能性のサイン。`sed -n '1,20p'`で先頭行を目視し、`curl`でレスポンスサイズを確認する2点セットで、マルウェアか過去の応急処置の残骸かを切り分ける
- 隔離フォルダに生の不正PHPファイルを長期間放置しない。Web非公開でも、証跡保全用にtar.gz化して生ファイルは削除するのが望ましい
- 削除耐性のためパーミッション000にされたファイルは、`chmod -R u+rwX`しないと`tar`コマンド自体が失敗する
