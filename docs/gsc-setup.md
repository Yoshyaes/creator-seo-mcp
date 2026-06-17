# Google Search Console Setup Guide

This guide walks you through getting OAuth credentials so creator-seo-mcp can read your Search Console data.

You only need to do this once. The token is stored locally and refreshes automatically.

> **Note:** Google recently redesigned the OAuth console into "Google Auth Platform." The steps below reflect the new UI. If you see the old "OAuth consent screen" flow, the concepts are the same but the labels differ.

---

## Step 1. Create a Google Cloud project

1. Go to [console.cloud.google.com](https://console.cloud.google.com).
2. Click the project dropdown at the top, then **New Project**.
3. Name it anything (e.g. "two-average-gamers") and click **Create**.

---

## Step 2. Enable the Search Console API

1. In your new project, go to **APIs and Services > Library** (search "APIs and services" in the top search bar).
2. Search for **Google Search Console API**.
3. Click it, then click **Enable**.

---

## Step 3. Configure Google Auth Platform (OAuth consent)

After enabling the API, navigate to **APIs and Services > Google Auth Platform** (or search for it). You'll see a left sidebar with: Overview, Branding, Audience, Clients, Data Access, Verification Center, Settings.

### 3a. Set the Audience (user type)

1. Click **Audience** in the left sidebar.
2. Select **External** (allows any Google account, not just your Workspace org).
3. Save.

### 3b. Set Branding

1. Click **Branding** in the left sidebar.
2. Fill in:
   - **App name:** creator-seo-mcp
   - **User support email:** your email
   - **Developer contact email:** your email
3. Save.

> You will likely see an "unverified app" warning the first time you authorize. This is expected for personal-use apps. Click **Advanced > Go to creator-seo-mcp (unsafe)** to proceed.

---

## Step 4. Create an OAuth Desktop client

1. Click **Clients** in the left sidebar.
2. Click **Create Client** (or **+ Create OAuth client**).
3. Application type: **Desktop app**.
4. Name it "creator-seo-mcp desktop".
5. Click **Create**.
6. On the confirmation screen, click **Download JSON**.
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
| "GOOGLE_CREDENTIALS_PATH env var is not set" | Set the env var to the path of your downloaded JSON file |
| "Access blocked: creator-seo-mcp has not completed the Google verification process" | In the Audience section, add your Google account as a test user |
| Token expired or invalid | Delete `~/.creator-seo-mcp/token.json` and re-authorize |
| "This app isn't verified" warning | Click Advanced, then "Go to creator-seo-mcp (unsafe)" |
| No sites returned | Make sure the Google account you authorized has verified properties in Search Console |
| Can't find "External" option | Look under **Audience** in the Google Auth Platform left sidebar |
