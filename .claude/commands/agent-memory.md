# /agent-memory — 重要情報の記憶保存

会話中の重要な情報を `00_context/memories/` に保存するスキル。「覚えておいて」で発動。

## 実行手順

1. **保存すべき情報を抽出**
   - 意思決定とその理由
   - クライアントの特記事項・好み・NG
   - 価格設定・契約条件の方針
   - 業務上のルール・マイルール
   - ツール・プロセスの変更

2. **カテゴリに分類して適切なファイルに保存**

| カテゴリ | 保存先ファイル |
|---------|-------------|
| クライアント情報 | `00_context/memories/clients.md` |
| 価格・契約方針 | `00_context/memories/pricing-policy.md` |
| 業務ルール | `00_context/memories/workflow-rules.md` |
| 意思決定の記録 | `00_context/memories/decisions.md` |
| 好み・スタイル | `00_context/memories/preferences.md` |

3. **追記形式で保存**
   ```
   ## YYYY-MM-DD
   **カテゴリ**: 
   **内容**: 
   **背景・理由**: 
   ```

4. **保存完了をユーザーに報告**
   - 保存したファイルのパスと内容の要約を提示

## 注意事項
- 個人情報・機密情報を保存する場合はその旨をユーザーに確認
- `clients.md` はGitHubにpushしない（.gitignoreで管理）
