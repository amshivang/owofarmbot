# Security & Token Safety Policy

## Credential Safety Guidelines

**OwO Auto Bot** requires a Discord User Authorization Token to communicate with Discord's API:
- **Never Share Your Token**: Your authorization token grants full access to your Discord account. Never send your token to anyone or commit it into version control.
- **In-Memory Credential Handling**: The application does not upload or exfiltrate your token to any third-party server. It is stored locally in session memory to connect directly to Discord's official Gateway.
- **Token Invalidation**: If you believe your token has been compromised, change your Discord account password immediately to invalidate all active tokens.

## Responsible Disclosure

If you discover any security issue or vulnerability in the application:
1. Please do **NOT** open a public issue.
2. Email **linkwithshivang@gmail.com** with the subject line `[SECURITY] OwO Auto Bot Vulnerability`.

All reports are reviewed within 48 hours.
