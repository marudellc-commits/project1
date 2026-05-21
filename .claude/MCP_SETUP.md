# MCP連携セットアップ手順

このファイルはローカルのClaude Code環境でMCP接続を有効にするための手順書です。

---

## 1. Google Calendar

### 手順
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新規プロジェクトを作成（または既存を選択）
3. 「APIとサービス」→「ライブラリ」→ **Google Calendar API** を有効化
4. 「認証情報」→「認証情報を作成」→「OAuth 2.0クライアントID」
   - アプリの種類: **デスクトップアプリ**
   - 名前: `claude-calendar`
5. JSONをダウンロードし、`~/.claude/google-oauth-credentials.json` に配置
6. `~/.claude/claude_desktop_config.json` に以下を追記：

```json
{
  "mcpServers": {
    "google-calendar": {
      "command": "npx",
      "args": ["-y", "@cocal/google-calendar-mcp"],
      "env": {
        "GOOGLE_OAUTH_CREDENTIALS": "/Users/あなたのユーザー名/.claude/google-oauth-credentials.json"
      }
    }
  }
}
```

7. Claude Codeを再起動して接続テスト：「今日の予定を教えて」

---

## 2. Google Sheets

### 手順
1. [Google Cloud Console](https://console.cloud.google.com/) で同プロジェクトを選択
2. 「APIとサービス」→「ライブラリ」→ **Google Sheets API** を有効化
3. 「認証情報」→「サービスアカウント」を作成
   - サービスアカウント名: `claude-sheets`
   - ロール: **編集者**
4. サービスアカウントのキー（JSON）をダウンロード → `~/.claude/google-service-account.json`
5. **使用するスプレッドシートをサービスアカウントのメールアドレスと共有する**
6. `~/.claude/claude_desktop_config.json` に以下を追記：

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-gdrive"],
      "env": {
        "GOOGLE_SERVICE_ACCOUNT_KEY": "/Users/あなたのユーザー名/.claude/google-service-account.json"
      }
    }
  }
}
```

---

## 3. GitHub（このリポジトリ）

### 手順
1. GitHub → Settings → Developer settings → **Personal access tokens** → Tokens (classic)
2. 「Generate new token」で作成：
   - スコープ: `repo`, `project`, `read:org`
   - 期限: 90日以上推奨
3. トークンをコピーして環境変数に設定（`.zshrc` または `.bash_profile` に追記）：

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

4. `~/.claude/claude_desktop_config.json` に以下を追記：

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

5. 接続テスト：「GitHubのIssue一覧を見せて」

---

## 設定完了後の確認

すべて設定完了後、以下のコマンドで動作確認：

```
おはよう
```

→ `/daily-schedule` スキルが発動し、Google Calendarの予定 + GitHubのタスクが統合された工程表が生成されます。

---

## トラブルシューティング

| 問題 | 確認事項 |
|------|---------|
| Calendarが取得できない | OAuth認証ファイルのパスを確認・再認証を試みる |
| Sheetsが読めない | サービスアカウントとスプレッドシートの共有設定を確認 |
| GitHubが接続できない | トークンのスコープと有効期限を確認 |
