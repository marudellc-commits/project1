# SKYBASE神戸 移行棚卸し表

> [migration-runbook.md](migration-runbook.md) Phase 0-2 に対応する棚卸し表。
> データソース: `backups/skybase-shin-nagata.jp/`（2026-07-28取得の旧本番フルバックアップ、DB＋ファイル）をローカルで解析して作成。
> 参照用のみ。**この棚卸し表自体もDB/ファイルの中身を新環境に直接持ち込む根拠にはしない**（原則1・2は runbook 参照）。

---

## 1. 投稿一覧（ブログ）

| 項目 | 件数 |
|---|---|
| 公開済み投稿（post/publish） | 103 |
| 下書き（post/draft） | 5 |
| 自動下書き（post/auto-draft） | 2 |
| カテゴリ数 | 10 |

- [x] カテゴリ名・投稿の割り当て詳細確認済み（8カテゴリ使用: BLOG/EVENT/NEWS/SCHOOL/プログラミング/国家資格/未分類/空撮＆動画編集）
- [x] パーマリンク構造: `/%year%/%monthnum%/%day%/%postname%/`（`wp_options.permalink_structure`より確認済み）→ 新環境で設定済み

### Phase 4実施記録（2026-07-29）

7/28バックアップDBを解析し、Python製スクリプトでWXR 1.2形式のXMLを直接生成（投稿108件＋関連添付195件、注入コードスキャンでゼロ件確認）。新サーバーにwp-cliが導入済みだったため、SSH経由で`wp plugin install wordpress-importer --activate`→`wp import`を実行し自動インポート。

- [x] 投稿103件・下書き5件・カテゴリ8件・添付195件、インベントリと一致確認済み（新規インストール直後の初期投稿「Hello world!」は削除済み）
- [x] 添付ファイルの再ダウンロードなし（Phase 3で配置済みのファイルをそのまま参照、`wp import`のデフォルト動作＝`--fetch_attachments`なしなので旧ドメインへは一切アクセスしていない）
- [x] ドメイン自体は変更なし（`skybase-shin-nagata.jp`のまま）のため、本文中URLのsearch-replaceは不要
- [x] Diver独自ショートコード等がRE:DIVERで正しく表示されるか確認済み。旧Diverの囲い枠クラス（`sc_frame`/`highlight-box`/`price-box`/`cta-box`/`conclusion-box`/`route-box`/`emphasis-box`/`flow-item`等）を使う記事が108件中7件あり、RE:DIVER側にスタイル定義がなく崩れていたため、旧テーマCSS(`wp-content/themes/diver/css/auxiliary*.css`)から該当クラスの定義94ルールを抽出し、新サイトの「追加CSS」(`wp_update_custom_css_post`)に追加して復元
- [x] 残りの添付ファイル（ブログ以外＝固定ページ・LP等で使われていた分、元DB544件中未登録の349件）もWXR経由でメディアライブラリに追加登録。Phase 5以降の固定ページ構築時に旧画像をメディアライブラリから選べる状態にした（親記事は存在しないため「未添付」扱い）
- [x] **Phase 4完了**

---

## 2. 固定ページ一覧（30件: publish 25 / private 4 / draft 1）

### Phase 5開始前のスラッグ衝突チェック（2026-07-29）

固定ページ作成前に30スラッグ全件を新サーバー上で事前チェックしたところ、3件が衝突していたため解消済み。

| スラッグ | 衝突元 | 対応 |
|---|---|---|
| `front` | diver-blocksプラグインが自動生成した初期デモページ（ID 3787、今日日付、`dbp/section`ブロックのグラデーション見本。旧サイトのデータではない） | ページごと削除 |
| `school` | 添付ファイル(画像)ID 59、タイトルが偶然「school」でスラッグ化されていた | 添付ファイルのスラッグを`school-img`に変更 |
| `work` | 添付ファイル(画像)ID 63、タイトルが偶然「work」でスラッグ化されていた | 添付ファイルのスラッグを`work-img`に変更 |

**教訓**: WordPressは固定ページのスラッグを、添付ファイル（メディア）のスラッグとも重複させられない仕様。画像タイトルが日本語でなく英単語（"school"等）だと特に起きやすい。他の29スラッグは衝突なしを確認済み。

| ID | タイトル | スラッグ | 親ID | 状態 |
|---|---|---|---|---|
| 2 | サンプルページ | sample-page | 0 | publish（要否確認・削除候補） |
| 3 | プライバシーポリシー | privacy-policy | 0 | publish |
| 29 | ABOUT | about | 0 | publish |
| 36 | FRONT | front | 0 | **private**（トップページ本体と推定） |
| 69 | SERVICE｜スカイベース神戸のドローンサービス | service | 0 | publish |
| 75 | 下書き用 | (空) | 0 | draft（削除候補） |
| 139 | レンタルコート｜サーキットコース | rental-coats | 69 | **private** |
| 143 | WORK｜撮影・点検 | work | 69 | publish |
| 152 | CONTACT | contact | 0 | publish |
| 202 | SCHOOL｜民間資格 | minkan | 827 | **private** |
| 222 | Video | video | 143 | publish |
| 280 | ACCESS | access | 0 | publish |
| 287 | NEWS | news | 0 | publish |
| 371 | お問い合わせ完了 | contact-finish | 0 | publish |
| 374 | お問い合わせ確認 | contact-kakunin | 0 | publish |
| 386 | SCHOOL｜プログラミング教室 | programming | 827 | publish |
| 684 | ドローン無料体験説明会送信完了ページ | drone_thanks | 0 | publish |
| 703 | プログラミング無料体験会送信完了ページ | programing_thanks | 0 | publish |
| 740 | SCHOOL｜国家資格・アドバンスコース | national-qualifications | 827 | publish |
| 827 | SCHOOL｜トップ | school | 0 | publish |
| 844 | Sales & Rental｜機体販売・レンタル | sales-rental | 69 | **private** |
| 851 | 屋外練習会・空撮講習 | training | 69 | publish |
| 1057 | ドローン国家資格 無料説明会申込フォーム｜LP | school-lp-form | 0 | publish |
| 1070 | ドローン無料説明会送信完了ページ｜LP | lp_thanks | 0 | publish |
| 1158 | ドローン工作教室体験会送信完了ページ | kousakukyousitsu | 0 | publish |
| 1655 | 助成金で格安取得｜subsidy | subsidy | 0 | publish |
| 2325 | SCHOOL｜空撮＆動画編集講座 | shooting-editing | 827 | publish |
| 2831 | SCHOOL｜農業ドローン講習 | dji-agras-t-25 | 827 | publish |
| 3355 | SCHOOL｜外壁診断講習 | wall-inspection | 827 | publish |
| 3668 | ドローン国家資格 更新講習 | training | 0 | publish |

⚠️ **スラッグ重複に注意**: `training` が2件存在（ID851は`/69/`配下、ID3668はルート直下）。実際のURLは親子関係で決まるため即問題ではないが、新環境で再構築する際に**どちらを`/training/`に割り当てるか要確認**。

- [ ] private扱いの5ページ（FRONT/レンタルコート/民間資格/Sales&Rental）が実際にどこから参照されているか確認
- [ ] sample-page・下書き用ページは新環境に持ち込むか判断（不要なら破棄）
- [x] **サンクスページ6件（`contact-finish`/`contact-kakunin`/`drone_thanks`/`programing_thanks`/`lp_thanks`/`kousakukyousitsu`）は新環境では作成しない方針に決定（2026-07-31）**。フォームを4種類に統合したため、旧の個別サンクスページ構成は複雑すぎると判断。本当に必要になった時点で作成する
- [x] **`rental-coats`/`video`/`sales-rental`/`minkan`/`work`の5ページも新環境では作成しない方針に決定（2026-07-31）**。現状運用していないため。必要になった際は`backups/skybase-shin-nagata.jp/`から内容を拾う

---

## 3. LP一覧（カスタム投稿タイプ `lp`、16件: publish 14 / private 2）

registered by diver theme (`custom_post.php`)、**rewriteスラッグ指定なし＝URLは `/lp/{slug}/`**（固定ページの同名スラッグとは衝突しない。例: page `school` = `/school/`、lp `school` = `/lp/school/`）

| ID | タイトル | スラッグ | 状態 |
|---|---|---|---|
| 942 | 国家資格を取るならSKYBASE神戸 | school | publish |
| 1341 | 国家資格を取るならSKYBASE神戸 | national-qualifications | publish |
| 1435 | Contact | contact | publish |
| 1538 | 冬の一等国家資格キャンペーン | winter-campaign | publish |
| 1589 | Contact｜一等国家資格LP冬キャンペーン | contact-2 | publish |
| 1753 | 二等国家資格キャンペーン | second-campaign | **private** |
| 1797 | Contact｜二等国家資格キャンペーン2026LP | contact-second-campaign | publish |
| 1990 | 5月限定 空撮・映像編集キャンペーン | gw-special-campaigns | publish |
| 2047 | Contact｜二等国家資格2025GW | gw2025 | **private** |
| 2292 | 夏の二等国家資格キャンペーン2026 | summer-2026 | publish |
| 2315 | Contact｜夏の二等国家資格キャンペーン | contact-summer2026 | publish |
| 2859 | 冬の特別キャンペーン20,000円OFF | winter2025 | publish |
| 2945 | Contact｜冬の特別キャンペーン | contact-winter2025 | publish |
| 3048 | 【Skybase KOBE】国家資格取得 | national-qualification | publish |
| 3106 | Contact｜通常LP問い合わせ | contact2026 | publish |
| 3250 | 2026二等国家資格キャンペーン | second-campaign2026 | publish |

- [ ] 終了済みキャンペーンLP（winter-campaign / gw-special-campaigns / summer-2026 / winter2025 等、期間限定物）は**新環境に移行するか終了扱いにするか**クライアントに確認
- [ ] 現行稼働中のLPだけに絞って runbook Phase 6 の対象を確定

---

## 4. フォーム一覧（Contact Form 7、12件）

| ID | フォーム名 | 状態 |
|---|---|---|
| 151 | contact01 | 使用中 |
| 535 | mousikomi_form | 使用中 |
| 669 | mousikomi_form_drone | 使用中 |
| 1067 | 不使用_mousikomi_form_lp | **不使用**（削除候補） |
| 1155 | 不使用_mousikomi_natsuyasumi | **不使用**（削除候補） |
| 1588 | 不使用_mousikomi_form_lp_2024winter-campaign | **不使用**（削除候補） |
| 1796 | mousikomi_form_lp_second-campaign2026 | 使用中 |
| 2046 | 不使用_2025mousikomi_form_lp_gw | **不使用**（削除候補） |
| 2318 | 2026mousikomi_form_lp_summer | 使用中 |
| 2939 | 2025mousikomi_form_lp_winter | 使用中（LP存続判断に連動） |
| 3111 | mousikomi_form_2026lp | 使用中 |
| 3482 | Wall Inspection Training Entry | 使用中 |

→ 12件中4件が命名からして**明示的に「不使用」**。runbook Phase 7の「重複統合・本数確定」はこの4件を除外するところから着手できる。

- [ ] 各フォームの**宛先メール・項目・reCAPTCHA有無**は旧本番管理画面（CF7編集画面）で個別確認
- [ ] `wpcf7-redirect`プラグインが有効 → フォーム送信後のリダイレクト先設定も個別確認（新環境でリダイレクト先URLも作り直しが必要）
- [ ] 保留タスク「GGE問い合わせフォーム追加」「無料相談フォームのLINE切替」の反映先をどのフォームにするか確定

### Phase 7実施内容（2026-07-31・最終決定）

実際の件名を精査した結果、内部名だけでは用途が分からなかったため精査（[lp-extract/cf7-forms-detail.txt](../lp-extract/cf7-forms-detail.txt)に全8件の詳細を書き出し済み）。旧8件（使用中）→**新4件に統合**する方針で確定・実施中。

| 新フォーム | 統合元（旧） | 状態 |
|---|---|---|
| ① 一般問い合わせフォーム | contact01 | ✅ 作成済み |
| ② 申込フォーム（統合） | mousikomi_form_drone／second-campaign2026／summer2026／winter2025／2026lp（国家資格LP） の5件を集約 | ⬜ LP作成と並行して対応中 |
| ③ プログラミング体験申込フォーム | mousikomi_form | ✅ 作成済み |
| ④ 外壁診断申込フォーム（法人向け） | Wall Inspection Training Entry | ⬜ 未着手 |

- **②の統合方式**: フォーム自体は1本化し、各LPの申込ボタンのリンクに`?src=summer2026`等の目印を付与。フォーム送信時にhiddenフィールドで記録し、通知メール・保存データに流入元LPが自動で残る仕組み（Wall Inspection旧フォームの`hidden: source`と同種の手法）
- **winter2025**: 該当LPが終了済みのため、フォームごと**廃止**確定
- [ ] `?src=`パラメータ名とCF7のhiddenフィールド名が一致しているか（`default:get:src`等）、実際の送信テストで動作確認

---

## 5. 必要プラグイン一覧（現状アクティブ18件）

| プラグイン | 新環境での扱い（案） |
|---|---|
| all-in-one-wp-migration | 不要（移行方式が根本的に異なるため） |
| all-in-one-wp-security-and-firewall | ⭕️ 新規インストール（標準セキュリティ構成） |
| classic-editor | 要否確認（RE:DIVERはブロックエディタ前提のため縮小候補） |
| classic-widgets | 要否確認 |
| contact-form-7 | ⭕️ 新規インストール |
| duplicate-post | 要否確認（あれば便利程度） |
| flamingo | ⭕️（CF7の問い合わせ保存用、継続利用なら） |
| google-site-kit | ⭕️ 新規接続（[前回調査](#6-外部連携タグ現状)のGA4/Search Console再設定） |
| google-sitemap-generator | 要検討（他の高機能サイトマッププラグインへの置き換えも可） |
| maintenance | 移行作業中のみ一時利用、本番では不要 |
| nextend-smart-slider3-pro | 要確認（ライセンス・スライダー内容の再現要否） |
| public-post-preview | 要否確認 |
| pubsubhubbub | 要否確認（ブログ更新のPuSH通知、なくても実害小） |
| safe-svg | 要否確認（SVGアップロードを許可するなら要） |
| simple-local-avatars | 要否確認 |
| wordfence | ⭕️ 新規インストール（標準セキュリティ構成） |
| wp-super-cache | ⭕️ 新規インストール（キャッシュ） |
| wpcf7-redirect | フォーム本数確定後に要否判断 |

- [ ] 「本当に要るものだけ」に絞る最終判断はクライアント（マルデ社内）と確認
- [ ] RE:DIVER移行に伴い、diverテーマ独自機能（LP/common投稿タイプ等）の代替をブロックエディタでどう再現するか要検討

---

## 6. 外部連携タグ（現状）

※ 会話内で別途詳細調査済み（[会話内の一覧参照](#)）。要点のみ再掲。

| タグ | ID | 備考 |
|---|---|---|
| Google Tag Manager | GTM-T35P9VKP | テーマのAnalyticsコード欄に手動貼付け |
| GA4（Site Kit経由） | G-EC45H7CMPN | Site Kit接続済み・useSnippet有効。**GTMと二重計測の可能性あり、新環境では一本化を検討** |
| Search Console（Site Kit） | プロパティ = `https://skybase-shin-nagata.jp/` | 新環境移行後は**新規プロパティ登録＋サイトマップ再送信**が必要（runbook Phase 10） |
| Google Ads / AdSense | 未設定 | - |
| Facebook Pixel等その他 | 実装なし | - |

- [x] **方針確定・実施完了（2026-07-31）**: GTM-T35P9VKPは**他社所有のコンテナ**でマルデ側では中身の管理は不可だが、**その他社側の計測のため設置自体は継続が必要**と判明。→ **Site Kit（マルデ管理下）と旧GTM（他社管理下）を併存**させる方針に確定
- [x] Site Kitプラグインを新サーバーに導入・Googleアカウント連携完了。GA4は旧サイトと**同一プロパティ**（`G-EC45H7CMPN`）に接続、Search Consoleは`sc-domain:skybase-shin-nagata.jp`（ドメインプロパティ、DNS検証を流用）で接続確認済み
- [x] GTM-T35P9VKPは、RE:DIVERに手動貼り付け欄がないため`wp-content/mu-plugins/gtm-partner.php`（`wp_head`/`wp_body_open`フック）で設置。出力を`curl`で確認済み

---

## 7. リダイレクト設定

旧本番`.htaccess`を確認 → **カスタム301等の個別リダイレクトは設定なし**（AIOWPSのセキュリティルール＋画像ホットリンク対策＋標準WPリライトのみ）。`Redirection`系プラグインも非導入。

- [ ] → runbook Phase 9-4の通り、スラッグ不変なら大量リダイレクトは不要。統廃合するLP/フォームのURLのみ個別301を用意すればよい

---

## 8. robots.txt / XMLサイトマップ

- 物理`robots.txt`ファイルは**存在しない**（WordPressの仮想robots.txtがデフォルト設定で出力されている状態と推定）
- サイトマップは`google-sitemap-generator`プラグインが生成（URLは旧本番の管理画面で要確認）

- [ ] 新環境でのXMLサイトマップURLを確定し、Phase 10でSearch Console再送信

---

## 9. marudellc側（参照ステージング）で完成しているデザイン範囲

[README.md](../README.md)より（2026-05-28時点）:

| セクション | 状態 |
|---|---|
| セクション1（ヒーロー） | 実装済み |
| セクション2（Why Choose Us） | 実装済み |
| セクション3（スクール） | 実装済み |
| セクション4（講師紹介） | **未実装**（既存スライド流用予定） |
| セクション5（サービス） | 実装済み |
| セクション6（ターゲット別CTA） | 実装済み |
| セクション7（NEWS） | **未実装** |
| 固定ページ（SCHOOL/SERVICE/SUBSIDY/ABOUT/ACCESS） | 未着手 |
| GGE問い合わせフォーム項目追加 | 未着手 |
| 講師写真3名分 | 受領待ち（README更新時点） |

→ runbook Phase 5で「見本」として使う対象はこの範囲。**未実装分（セクション4・7、固定ページ全般）は新環境側で先に完成させる必要がある**か、旧本番の対応セクションを参考にするか要判断。

---

## 9-1. Phase 5途中でのSEO引き継ぎ確認（2026-07-31）

新サーバーで固定ページ22件が作成された時点で、旧本番とのスラッグ照合とSEO設定の引き継ぎを実施。

### スラッグ照合結果

- [x] `privacy-policy` `about` `front` `service` `contact` `access` `news` `programming` `national-qualifications` `school` `subsidy` `shooting-editing` `dji-agras-t-25` `wall-inspection` は一致確認済み
- [ ] `training`スラッグの中身が入れ替わっている：旧サイトの`training`スラッグ衝突（本表2章参照）を、新サーバーでは「ドローン国家資格 講習」=`training`、「屋外練習会・空撮講習」=`training-2`（下書き）で解消していた。**意図通りか要確認**
- [ ] 下書き「Sample」（ID4227、スラッグなし）が旧サイトに該当なし。消し忘れの可能性
- [ ] 新設スラッグ`for-education`/`drone-service`/`inspection`/`pesticide-spraying`は旧サイトに存在しない（旧SERVICEページの分割と思われる）。**旧URLが検索にインデックスされていた場合、Phase 9でリダイレクト設計が必要**
- [ ] 旧サイトにあり新サーバー未作成: `rental-coats` `video` `contact-finish` `contact-kakunin` `drone_thanks` `programing_thanks` `sales-rental` `lp_thanks` `kousakukyousitsu` `minkan` `work`（残作業として認識していれば問題なし）

### SEO設定の引き継ぎ

旧サイトはテーマ独自のSEO欄（`diver_single_metadescription`等、個別ページ）と`diver_seosetting`系（サイト全体）を使用。RE:DIVER側は`diver_single_seo`（個別）・`diver_seo`（全体）という別名の仕組みに変わっているが、意味的に対応。

- [x] `About`ページ（ID4130）の個別メタディスクリプションを転記済み
- [x] サイト全体のフォールバック用SEO説明文を`diver_seo`オプションに設定済み（区切り文字`|`も旧設定に合わせた）
- [x] カテゴリ/タグ/検索結果等のindex/follow設定（`diver_meta_robots`）は旧サイトも未カスタマイズ（コードデフォルトのまま）だったため、新サーバーもデフォルトのままで対応不要と確認
- [x] **現行稼働中2LP（`national-qualification`ID4177/`summer-2026`ID4269）のメタディスクリプションを新規作成・設定済み（2026-07-31）**。「5月限定」の使い回し文言は残っておらず空欄だったため、実際のページ内容（合格率90%・卒業後サポート／夏キャンペーン料金253,000円→223,000円）に基づいて新規に執筆
- [ ] 他8件（LP関連の個別メタディスクリプション）は該当LPが未作成のため対象外。作成時に必要なら参考情報として提供可能
- [ ] Google Site Kitが新サーバー未導入。旧Diverテーマと異なりRE:DIVERはhead/bodyへの手動コード貼り付け欄がなく、**Site Kit連携が前提の設計**。GTM/GA4の実装にはSite Kit導入＋Google側でのOAuth連携（要ブラウザ操作）が必要

---

## 10. DNS / メール現況

### 10-1. DNSレコード（`dig`で公開情報を確認済み、2026-07-29）

| レコード | 値 |
|---|---|
| A（ルート） | `183.90.235.24` |
| A（www） | `183.90.235.24`（CNAMEではなくAで直接同一IP） |
| AAAA | なし（IPv6未対応） |
| NS | `ns1.xbiz.ne.jp` / `ns2.xbiz.ne.jp` / `ns3.xbiz.ne.jp`（runbookの「現状XServer Business」記載と一致） |
| MX | `0 skybase-shin-nagata.jp`（自ホスト。優先度0の1本のみ、外部メールサービスなし） |
| SPF（TXT） | `v=spf1 +a:sv163.xbiz.ne.jp +a:skybase-shin-nagata.jp +mx include:spf.sender.xserver.jp ~all` |
| DKIM | セレクタ **`default`** で存在確認（`default._domainkey.skybase-shin-nagata.jp`、RSA鍵あり） |
| DMARC | **未設定**（`_dmarc`レコードなし）→ 新環境構築時に追加を推奨 |
| サイト所有権確認（TXT） | `google-site-verification=UyX7O9jgwV_O80d2XHpTql7f9gDe9K_yWjWKg4B_brE`（**DNS TXT方式**で検証済み。メタタグ／HTMLファイル方式ではない） |
| autoconfig/autodiscover | 未設定（メールクライアント自動設定は非対応、手動設定前提） |

- [x] DNSレコード一式を記録（上記）
- [ ] 新環境のSPFレコードを作り直す（`sv163.xbiz.ne.jp`のような旧ホスト名を残さない。新サーバーのホスト名＋`include:spf.sender.xserver.jp`に更新）
- [ ] DKIMは新サーバーで新規に鍵生成される想定 → セレクタ名が変わる可能性があるため、切替後に新レコード値を確認してDNSに反映
- [ ] **DMARCを新規追加**（現状ゼロなので、移行を機に`p=none`から段階導入するのが安全）
- [ ] Google Site Verification用のTXTレコードは**ドメイン単位（Search Consoleのドメインプロパティ）の可能性が高い** → 新環境でSearch Console再登録時、同じ検証が引き継がれるか確認（DNS方式なのでサーバー移行の影響を受けにくいはずだが要確認）

### 10-2. メールアカウント一覧

| アドレス | 使用容量 |
|---|---|
| drone@skybase-shin-nagata.jp | 2,831.69 / 5,000 MB |

サーバーパネルで確認済み。**アカウントは1個のみ**。runbook Phase 1の「同じメールアドレス・同じパスワードで新サーバーに再作成」対象はこの1件。

- [x] 独自メールアカウント一覧を確認（上記1件）
- [x] 過去メール移行方針confirm済み（2026-07-29）：**移行する**方針で決定
  - [x] 新サーバーに`drone@skybase-shin-nagata.jp`を**新規パスワードで**作成済み（2026-07-29）
  - [ ] メールソフトに新旧両アカウントをIMAPで登録し、**DNS切替前に**旧→新へフォルダごとドラッグ＆ドロップでコピー（runbook Phase 1参照）
  - [ ] 新パスワードは安全な場所（パスワードマネージャー等）に控える。**このリポジトリには書かない**
- [ ] 現在このアドレスを利用している端末（メールソフト）を洗い出し、切替後にパスワード更新が必要な旨を伝える

### 10-3. 切替準備

- [ ] 切替予定日の24〜48時間前に、A・MXレコードのTTLを300秒程度へ引き下げ

---

## 11. Phase 8 最終検証の進捗（2026-07-31）

新サーバーの固定ページ・LP・投稿、公開済み全128件のURLを対象に自動チェックを実施。

- [x] **リンク切れ全128件チェック→ゼロ件**（`curl`でHTTPステータス確認、全件200）
- [x] **注入コード最終スキャン→ゼロ件**（全128ページのレンダリング後HTMLを対象に`eval(atob`/`base64_decode`/`document.write(unescape`を走査）
- [x] **noindexが有効なまま**であることを確認（`blog_public`オプション=0＝検索エンジン非表示設定中）
- [x] 計測タグ（Site Kit/GTM）設置確認済み（本表6章参照）
- [x] 全ページの画像・アイキャッチ表示（目視確認済み・2026-07-31）
- [x] 表示崩れ（PC/タブレット/スマホ、目視確認済み・2026-07-31）
- [x] 全フォーム実送信テスト（実施済み・2026-07-31）
- [x] 404・検索・カテゴリアーカイブ動作（確認済み・2026-07-31）
- [x] エラーログに致命的エラーなし・表示速度（確認済み・2026-07-31）
- [x] `wp-content/mu-plugins/TEMP-longer-nonce-life.php`を削除済み（2026-07-31）。nonce有効期限はデフォルト24時間に復帰確認済み

---

## 12. Phase 9 本番切替の進捗（2026-07-31）

- [x] 新サーバーの直前フルバックアップ取得（DB+ファイル、`backups/skybase-shin-nagata.jp-newserver/`にローカル保存）
- [x] noindex解除（`blog_public`=1に変更、robots.txtで通常クロール許可状態を確認）。**WordPress標準のXMLサイトマップ（`/wp-sitemap.xml`）が自動生成されていることも確認**
- [x] Basic認証: 未設定のため対応不要
- [x] XServer Domainパネルで「ドメイン適用先サービス」をBusiness→Xserverに変更実施（2026-07-31）
- [x] **NS反映確認（2026-07-31）**: `dig`でNSが`ns1〜5.xserver.jp`、Aレコードが新サーバーIP（`85.131.221.5`）に切り替わったことを確認。実ドメイン`http://skybase-shin-nagata.jp/`への直接アクセスでも200・正しいタイトルを確認し、**本番切替成功**
- [x] Wordfence/AIOSの追加セキュリティ設定を実施（レート制限・ログインURL変更・ファイル保護等、NS反映前に完了）
- [x] **無料独自SSLを発行・動作確認済み（2026-07-31）**: サーバーパネルでON操作、`curl`で証明書検証OK・HTTP/2応答を確認。パネル上「NS相違」表示は残っていたが実際の動作には影響なしと判断
- [x] WordPressの`siteurl`/`home`オプションを`https://`に変更済み
- [x] **DB内`http://skybase-shin-nagata.jp`の残存を`https://`へ一括置換（417箇所、2026-07-31）**。スマホでの画像非表示（混在コンテンツブロック）症状の原因と特定し解消。残存ゼロを確認
- [x] サーバーパネルで「HTTPS転送」「www転送（www→なしへ統一）」を設定
- [ ] 反映後72時間、新旧両方のメールボックスを確認
- [ ] 複数回線・複数拠点(事務所含む)で表示・https・メール送受信の最終確認（拠点によってはDNS浸透が遅れている場合あり）
- [x] http→httpsの自動リダイレクト設定はONにしたが反映待ち（www→wwwなしのリダイレクトは動作確認済み・301）
- [ ] **重要な発見（2026-07-31）：NS切替でDNSゾーンが新規作成され、Google所有権確認用TXTレコードが消失**していることが判明。SPF/DKIMは新サーバー用に自動再生成されて正常だが、Google確認用TXT(`google-site-verification=UyX7O9jgwV_O80d2XHpTql7f9gDe9K_yWjWKg4B_brE`)は自動生成対象外のため、手動で再追加が必要
- [x] sitemap.xmlの提供元がWordPress標準からWordfence生成のものに変わっている（`/sitemap.xml`、robots.txtに記載）が、200で正常動作を確認。対応不要

---

## 更新履歴

- 2026-07-29: 初版作成。DBダンプ（2026-07-28取得分）の解析結果をもとに1〜9を作成。DNS/メール（10）は未調査。
- 2026-07-29: `dig`による公開DNS照会でA/NS/MX/SPF/DKIM/DMARC/サイト所有権確認TXTを記録（10-1）。
- 2026-07-29: サーバーパネルでメールアカウント一覧を確認（10-2）。アカウントは`drone@skybase-shin-nagata.jp`の1件のみ、使用容量2,831.69/5,000MB。Phase 0-4完了、DNS/メール項目は過去メール移行要否の確認のみ残タスク。
- 2026-07-29: 過去メール移行要否の回答が来た（**移行する**方針）。Phase 0完了、Phase 1（新クリーンサーバー準備）に着手。サーバー契約済み・ドメイン設定追加済み（反映待ち）。SSLはNS切替後に発行する方針で確定。
