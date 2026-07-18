# Xserver 不正ファイル設置インシデント対応記録（2026-07-18）

marudellc（サーバーID: sv6099.xserver.jp）配下の3サイトが不正アクセスを受け、SSH経由で調査・復旧を実施。当日中に全サイト復旧完了。

## 被害サイト

- marudellc.com（本体）
- skybase.marudellc.com（SKYBASE神戸案件）
- royal878.jp

## 被害内容

| 項目 | 内容 |
|------|------|
| Webシェル | Tiny File Manager（k.php）がホームディレクトリ全体に83個設置 |
| バックドア | wp-admin/wp-includes内にランダム文字列名PHPが40個以上（`wp`という隠しサブディレクトリに格納、ディレクトリ権限で削除妨害） |
| コア改ざん | `index.php`が難読化バックドアに完全置換（marudellc.com / royal878.jp） |
| .htaccess改ざん | 偽装ファイル名（wp-logln.php等）だけを許可する不正ルールを追加 |
| アカウント乗っ取り | skybaseの管理者メールが`info@maridellc.com`（タイポスクワッティング）に書き換え（5/22） |
| 永続化 | crontabに偽装ジョブ（`/var/tmp/.X11-unix/.ICE-cache/lib-update`、コメントで"sys-perf-monitor"を偽装） |
| 侵入時期 | 最古の痕跡は4/12。侵入経路はアクセスログ未取得のため特定に至らず |
| 事前対策状況 | 被害時点で3サイトともWordfence未導入、royal878.jpとskybaseはAIOSも未導入 |

## 対応内容

1. 不正ファイル1132個を削除（証跡は`~/incident_evidence_20260718*.tar.gz`としてサーバー上にアーカイブ）
2. `index.php`を公式コアに復元、`.htaccess`の不正ルールを除去（3サイト全て）
3. 不正crontabエントリを削除
4. 全WP管理者パスワード・ソルト・セッションを全面ローテーション（4アカウント）
5. skybaseの乗っ取られた管理者メールアドレスを修正
6. 全プラグインを最新版に更新
7. SSH鍵をローテーション（漏洩の可能性があった旧鍵は失効済み）
8. Xserverサーバーパネルのログインパスワードを変更
9. 3サイト全てにWordfence + AIOSを導入・有効化（[wordpress-security-settings.md](wordpress-security-settings.md)の標準構成に準拠）

## 残タスク

- [ ] Wordfenceのファイアウォール学習モード完了確認（設置から1週間後）
- [x] 管理者アカウントへの2FA必須化（確認済み、有効化されている）
- [ ] reCAPTCHA v3キー取得・設定
- [ ] AIOSでログインURL変更、wp-config.phpのアクセス権440化
- [ ] royal878.jpの`really-simple-ssl`プラグインの動作確認（wp-cliでの有効化時に型エラーが出る不具合あり、更新で解消したか要確認）
- [ ] サーバー上の証跡アーカイブ2つ、保管期間経過後に削除を検討

## 補足：Wordfence日本語化

3サイトともWordPressのサイト言語設定が「日本語」だったため、Wordfence有効化時に翻訳ファイル（ja）が自動ダウンロード・適用済み。追加作業は不要だった。

## 追記（2026-07-18）：royal878.jpでPHP 8.1化に伴う障害発生

XserverサーバーパネルでPHPバージョンを8.1以上に上げたところ、royal878.jpが致命的エラーでダウン。

**原因**：`marker-animation`プラグイン同梱のフレームワーク（vendor/wp-content-framework、Technote製、2021年のファイル）が、トレイト名として`Readonly`を使用していた。PHP 8.1から`readonly`が予約語になったため、`use Readonly, ...;`という記述がパースエラーを起こす。PHPバージョンの問題ではなく、**プラグイン側がPHP 8.1以降と根本的に非互換**。

**対応**：`marker-animation`プラグインを無効化して復旧（マーカーアニメーション機能のみ停止、他機能への影響なし）。PHPバージョンは8.1以上を維持する方針（Wordfence等新しいプラグインがPHP 8.1+前提のため、こちらを優先）。

- [ ] `marker-animation`の代替プラグイン、または開発元（Technote）の更新版有無を確認

## 教訓

- 新規サイト公開時は、Wordfence + AIOS導入を初期セットアップの標準手順に組み込む（後回しにすると今回のように無防備な期間が生まれる）
- 侵入検知の初動を早めるため、Xserverの「アクセス解析」ログを定期的に確認する運用を検討
