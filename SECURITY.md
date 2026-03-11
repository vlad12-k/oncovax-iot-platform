# Security Policy

## Supported Versions
This is a portfolio project. Security fixes are applied on the `main` branch.

| Version | Supported |
|--------|-----------|
| main   | ✅        |

## Reporting a Vulnerability
If you believe you have found a security vulnerability, please use one of the following:

1) **Preferred:** Open a GitHub Security Advisory (private disclosure) if available.
2) If private reporting is not enabled, open an issue **without sensitive details** and label it `security`.
3) Do **not** include secrets (tokens, passwords, connection strings) in issues, logs, screenshots, or pull requests.

### Response expectations
- Initial acknowledgement: **within 7 days**
- Status update: **within 14 days**, or sooner if the issue is confirmed

## No-Secrets Policy (Important)
- Never commit API keys, tokens, passwords, or connection strings.
- Use local `.env` files for development and keep them out of git.
- Only commit `.env.example` with placeholder values.

## Security-by-default goals
- Least privilege access (RBAC) for API/UI.
- Encrypted transport where practical (TLS).
- Audit logging for critical actions (alert acknowledgements, configuration changes).
- Dependency and code scanning enabled via GitHub features (Dependabot, CodeQL).
