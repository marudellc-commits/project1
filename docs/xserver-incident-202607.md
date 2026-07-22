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

## 追記（2026-07-18）：wp-content配下に追加バックドア8個を発見・除去

管理画面の「Could not create .../ai1wm-backups/.htaccess file」エラーをきっかけに、`wp-content`配下（テーマ・プラグインフォルダ内）が広範囲に読み取り専用化されていたことが判明。これは`wp core verify-checksums`の対象外（コアファイルのみチェックする仕組みのため）で、初回の復旧作業では見逃していた領域。

- 読み取り専用ファイル1885個（.htaccess/index.php等）の権限を復旧
- 隠しバックドアディレクトリ「wp」を8個発見・削除（テーマ・Smart Sliderプラグイン・アップグレード一時フォルダ内に偽装設置、証跡は`~/incident_evidence_20260718_part3.tar.gz`）
- 削除後、3サイトともコア整合性チェック成功・正常表示を再確認

**教訓**：`wp core verify-checksums`はwp-admin/wp-includesのみが対象で、`wp-content`（テーマ・プラグイン）配下は検証対象外。今後同様の侵害対応では、`wp-content`配下も含めて「`wp`という名前の不審なサブディレクトリ」を明示的に検索する必要がある。

## 追記（2026-07-19）：royal878.jpで大規模な再感染が発生・根本原因を特定

WP管理画面で`wp-conffg.php`が復活していると報告があり調査したところ、**パスワード・SSH鍵の全面ローテーション後にもかかわらず再感染**していたことが判明。

**根本原因**：royal878.jpのWordPress本体が**6.7.5のまま更新されていなかった**（プラグインは更新済みだったが、コア本体の更新を見落としていた）。自動化された再感染ツールがこの未パッチの脆弱性を突いて、`index.php`・`.htaccess`・`wp-admin`/`wp-includes`配下、さらに`cgi-bin`・`img`・`inquiry`・`script`・`secure`などWordPress外の領域にも一括で30個以上のバックドアを再展開していた。marudellc.com/skybaseは元々コアが最新だったため無事だった。

**対応**：
- WordPress本体を7.0.2に更新（根本原因を解消）
- 再展開されたバックドア一式を削除（証跡: `~/incident_evidence_20260719_part4〜7.tar.gz`）
- 検出手法を強化：ファイル名パターンだけでなく、`eval(base64_decode`の全文検索と、既知の不正ペイロードのファイルサイズ一致検索を追加实施

**教訓**：プラグイン更新だけでは不十分。**WordPressコア本体の更新も必ず同時に確認・実施すること**。今後の復旧対応では`wp core check-update`を初動チェックリストに追加する。

- [ ] 24〜48時間、royal878.jpの再発有無を監視
- [ ] Wordfenceファイアウォールの手動最適化（学習モード完了を待たず、緊急対応として即時実施を推奨）

## 追記（2026-07-19）：Wordfenceスキャンで残存バックドア発見、検出手法を刷新

Wordfenceの初回マルウェアスキャンで、AIOSプラグイン内(`simba-tfa`ライブラリ)とtwentytwentyテーマ内に偽装された残存バックドアを発見。調査の結果、**7/18 18:28の時点で新規に作成されたPHPファイルはなく**（.htaccessの一括更新のみ）、実際は**当初(4月〜7月上旬)の侵害時に仕込まれたまま、これまでの検出手法（ファイル名パターン・既知サイズ）に一致せず見逃していたもの**と判明。新たな攻撃ではなく、当初の被害範囲がさらに広かったことを意味する。

- 発見された最古の痕跡：**4/6**（`secure/cgi-bin/index.php`、それまでの最古記録4/12を更新）
- 検出手法を「ファイル名/サイズの既知パターン」から「`goto`難読化・`eval+base64_decode`構造の全文検索」に刷新し、img/secure/wp-content配下の残り4個を発見・除去
- 証跡：`~/incident_evidence_20260719_part8.tar.gz`
- 構造的スキャンで全体を再確認し、残存ゼロを確認。3サイトとも正常稼働

**教訓**：ファイル名・サイズによる検出は攻撃者がパターンを変えると漏れる。`goto`難読化や`eval(base64_decode(`のような**コード構造そのもの**を検索する方法の方が確実。今後の同種対応では最初からこの構造検索を使うべき。

## 追記（2026-07-19）：skybaseで謎の表示崩れ調査 + uploads内バックドア発見

### skybase管理画面・フロントでの謎テキスト表示
`skybase.marudellc.com`の管理画面・フロント両方の冒頭に`<FilesMatch>...Deny from all</FilesMatch>`という不可解なテキストが表示される症状が発生。AIOS/Wordfence/全プラグイン/wp-config.php/コア/DB全体を切り分けたが原因コードの特定には至らず、標準テーマへの一時切り替えテストで**テーマ「rediver/rediver-child」が原因である**ことのみ確定。原因箇所はこの大規模カスタムテーマ内のどこかに埋もれており未特定。対症療法として`wp-content/mu-plugins/strip-leaked-htaccess-text.php`を設置し、出力バッファで該当テキストを自動除去する回避策を適用（表示は解消、根本原因は未解明のまま）。

副産物として、テーマのソースコードに以下を発見（今回の侵害とは別の、テーマ提供元由来の問題）：
- `update_checker()`内にGitHubアクセストークンがハードコード
- `Widget.php`の`download_widget_backup()`に`$_GET['file']`未検証の任意ファイル読み取り脆弱性

### uploads内バックドア発見
Wordfenceのスキャンで`skybase.marudellc.com/wp-content/uploads/2026/07/DnZZCBTa.php`を検出（コメント難読化されたeval(base64_decode(...))、設置日5/6）。`wp-content/uploads`はWordPressが実行可能なPHPを置く場所ではないため、この場所にPHPファイルがあること自体が強いシグナル。削除・証跡保存（`~/incident_evidence_20260719_part9.tar.gz`）。なお同ディレクトリの`aios/firewall-rules/settings.php`はAIOSプラグイン自身が生成する正規ファイルで問題なし。

**教訓**：`wp-content/uploads`配下も定期的に`*.php`ファイルの有無をチェックすべき（画像やドキュメントしか置かれないはずの場所）。

## 追記（2026-07-22）：marudellc.com検索結果スパム表示をきっかけに調査 → royal878.jpで常駐型自己回復マルウェアを発見・緊急オフライン化

Google検索結果でmarudellc.comのサイトリンクにECスパム商品（Panasonic/SIXPAD等）が混入して表示される症状の相談を受け調査。

### marudellc.com本体
- ライブHTML・DB・コアいずれもスパムコンテンツなし。検索結果の混入は過去のハック時にGoogleへインデックスされた残骸と推定（現在進行形の注入ではない）
- ただしドメインルート直下（public_html外、Web非公開領域）に2025年5月設置の古いバックドア2個（`ugefkhag.php`/`quipdvgw.php`、ファイルアップロード型シェル＋PHP一括感染ツール、パーミッション0で隠蔽）を発見・除去。証跡：`~/incident_evidence_20260722_marudellc_root.tar.gz`
- 結論：サイト側の問題ではなく、Google Search Console側で該当URLの削除リクエスト・再クロール依頼が必要

### royal878.jp：7/19対応後もバックドアが現存、さらに稼働中の自己回復プロセスを発見
7/19に「残存ゼロ確認」としていたにもかかわらず、再調査で以下が現存：
- 構造検索該当ファイル15個、偽装「wp」ディレクトリ13個、`wp-conffg.php`（130KB、7/19未明のタイムスタンプ＝前回対応の翌日に触られている）
- `.htaccess`に偽装ファイル名だけPHP実行を許可する不正ルールが健在（14箇所以上のサブディレクトリに同種の`.htaccess`）
- コア`index.php`が難読化バックドアに再置換

**さらに重大な発見**：SSHで`ps -ef`を確認したところ、`php -f wp-includes/<ランダム名>.php`という常駐型プロセスが稼働中。強制終了・ファイル削除しても数分でランダムな別名（vijuoi.php→elwfxd.php→vgxyni.php等）で再出現。手作業のファイル単位削除では追いつかない**自己回復型のマルウェア**と判断。

**対応**：
1. `~/royal878.jp/public_html`を`public_html.infected_20260722`へ退避し、PHPを一切含まない静的メンテナンスページ（503応答）に差し替えてサイトを緊急オフライン化
2. オフライン化後、60秒以上プロセスの再出現なしを確認（トリガーがHTTPリクエスト経由である可能性を支持）
3. 隔離コピー内で残りのバックドア（`cgi-bin`/`img`/`inquiry`/`script`/`secure`配下や`really-simple-ssl`プラグイン内など）と対応する不正`.htaccess`を追加削除（証跡：`~/incident_evidence_20260722_royal878.tar.gz`, `_part2`, `_part3`）
4. `wp core download --version=7.0.2 --force`でコア一式をピュアな状態に上書き
5. 最終確認：`verify-checksums`成功、構造検索・偽装wpディレクトリ・`Allow from all`許可ルールともに残存ゼロ、30秒監視でも改ざん・プロセス再出現なしを確認

**現状**：royal878.jpは引き続きオフライン（メンテナンスページ表示中）。コア・wp-content内の既知バックドアは一掃済みだが、常駐プロセスを実際に起動していたトリガー（テーマ`noel_tcd072`またはプラグイン内の未特定フック）は特定できていないため、テーマ/プラグインの全面再インストール検証が完了するまで公開再開は保留中。

**教訓**：「構造検索でファイル残存ゼロ」を確認しても、**プロセス一覧（`ps -ef`）を見ない限り、稼働中の常駐マルウェアは検知できない**。今後の同種対応では、ファイルスキャンに加えて`ps -ef | grep "php -f"`のような不審プロセスの確認を標準手順に追加すべき。また、7/19時点の「24〜48時間監視」だけでは不十分だったことから、月次チェック（[[project_monthly_malware_check]]）とは別に、このサイトは当面より高頻度の確認が必要。

- [ ] royal878.jpのテーマ（noel_tcd072）・プラグイン（really-simple-ssl等）を公式配布元から再取得し、既存ファイルと比較検証
- [ ] 常駐プロセスの起動トリガー（wp-cron登録フック／テーマfunctions.php／プラグインフック）を特定
- [ ] 検証完了後、`public_html.infected_20260722`を破棄し正式復旧・再公開
- [ ] marudellc.comの旧スパムページをGoogle Search Consoleで削除リクエスト・再クロール依頼

## 教訓

- 新規サイト公開時は、Wordfence + AIOS導入を初期セットアップの標準手順に組み込む（後回しにすると今回のように無防備な期間が生まれる）
- 侵入検知の初動を早めるため、Xserverの「アクセス解析」ログを定期的に確認する運用を検討
- ファイルの構造検索だけでなく、**`ps -ef`での常駐プロセス確認**を侵害調査の標準手順に含める（2026-07-22royal878.jp再調査で判明）
