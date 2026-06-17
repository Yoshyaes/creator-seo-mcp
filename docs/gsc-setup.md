# Google Search Console Setup Guide

This guide walks you through getting OAuth credentials so creator-seo-mcp can read your Search Console data.

You only need to do this once. The token is stored locally and refreshes automatically.

---

## Step 1. Create a Google Cloud project

1. Go to [console.cloud.google.com](https://console.cloud.google.com).
2. Click the project dropdown at the top, then **New Project**.
3. Name it anything (e.g. "creator-seo-mcp") and click **Create**.

---

## Step 2. Enable the Search Console API

1. In your new project, go to **APIs and Services > Library**.
2. Search for "Google Search Console API".
3. Click it, then click **Enable**.

---

## Step 3. Configure the OAuth consent screen

1. Go to **APIs and Services > OAuth consent screen**.
2. Choose **External** (unless you have a Google Workspace org), then click **Create**.
3. Fill in the required fields:
   - App name: "creator-seo-mcp"
   - User support email: your email
   - Developer contact: your email
4. Click **Save and Continue** through the Scopes and Test Users screens (no changes needed).
5. On the Summary screen, click **Back to Dashboard**.
6. Under "Publishing status", click **Publish App** if you want to skip the "unverified app" warning. For personal use, leaving it in Testing is fine. If you leave it in Testing, add your Google account as a test user.

---

## Step 4. Create OAuth credentials

1. Go to **APIs and Services > Credentials**.
2. Click **Create Credentials > OAuth client ID**.
3. Application type: **Desktop app**.
4. Name it "creator-seo-mcp desktop".
5. Click **Create**.
6. Click **Download JSON** on the confirmation dialog.
7. Save the file somewhere safe, e.g. `~/.creator-seo-mcp/credentials.json`.

---

## Step 5. Point the server at your credentials file

Set the environment variable:

```bash
export GOOGLE_CREDENTIALS_PATH="$HOME/.creator-seo-mcp/credentials.json"
```

Or add it to your `.env` file (copy from `.env.example`).

---

## Step 6. Authorize on first run

The first time you call any GSC tool, a browser window will open asking you to sign in and grant access to your Search Console data. After you approve, a token is saved to `~/.creator-seo-mcp/token.json`. Subsequent calls use this token automatically.

If you see an "unverified app" warning, click **Advanced > Go to creator-seo-mcp (unsafe)**. This is expected for personal-use OAuth apps that have not been through Google's verification process.

---

## Verify it worked

Ask the agent to call `list_sites` or `health_check`. You should see your verified Search Console properties in the response.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "GOOGLE_CREDENTIALS_PATH env var is not set" | Set the env var to the path of your downloaded `credentials.json` |
| "Access blocked: creator-seo-mcp has not completed the Google verification process" | Add your Google account as a test user in the OAuth consent screen |
| Token expired or invalid | Delete `~/.creator-seo-mcp/token.json` and re-authorize |
| "This app isn't verified" warning | Click Advanced, then "Go to creator-seo-mcp (unsafe)" |
| No sites returned | Make sure the Google account you authorized has verified properties in Search Console |
