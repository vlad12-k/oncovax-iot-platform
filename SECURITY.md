# Security Policy

## Supported Scope

This repository currently represents an MVP and hosted prototype baseline for the OncoVax IoT Monitoring Platform.

Security support currently applies to:

- the public source repository
- the FastAPI service baseline
- the lightweight operational dashboard
- Docker-based local development configuration
- MongoDB Atlas integration baseline
- DigitalOcean hosted application baseline

This project is not yet a fully production-hardened platform. Security controls should therefore be interpreted as baseline prototype practices rather than complete enterprise-grade protections.

## Reporting a Vulnerability

If you discover a security issue in this repository or its hosted baseline, please report it responsibly.

Please include:

- a clear description of the issue
- the affected component or file
- reproduction steps where possible
- the potential impact
- any suggested mitigation if known

Please do **not** disclose sensitive vulnerabilities publicly before the issue has been reviewed.

## Current Security Baseline

The current project includes the following security-oriented practices:

- no intended storage of secrets in source control
- use of environment variables for sensitive runtime configuration
- schema-based validation of incoming telemetry messages
- separation of time-series and audit-oriented data responsibilities
- Docker-based service isolation in development
- MongoDB Atlas-managed hosted audit data baseline
- DigitalOcean hosted runtime baseline
- dependency and code scanning support through GitHub tooling
- threat-model placeholder documentation for future expansion

## Current Limitations

The current baseline still has important security limitations, including:

- no user authentication or role-based access control yet
- no protected operator login flow
- limited secret-management maturity
- no formal production reverse-proxy and TLS hardening baseline documented yet
- no full audit of all public network exposure paths
- limited application-layer authorization controls
- prototype-grade hosted deployment rather than hardened production deployment

## Sensitive Data Handling

This repository should not be used to store:

- production passwords
- real API keys
- cloud secrets
- database credentials
- patient data
- laboratory-sensitive regulated operational data

Any hosted deployment should use environment-based configuration and avoid committing secrets to the repository.

## Hosted Environment Notes

For the current hosted baseline:

- MongoDB Atlas is used as a managed audit data backend
- DigitalOcean is used as a hosted runtime baseline
- security groups, firewall rules, least-privilege database access, and HTTPS hardening should be strengthened further before any production use

## Dependency and Code Quality Tooling

The repository includes a baseline quality and security posture through:

- GitHub Actions
- CodeQL
- Dependabot

These controls help support early detection of code and dependency issues, but they do not replace formal security review.

## Future Security Improvements

Planned future improvements include:

- authentication and session management
- role-based access control
- stronger secret-management patterns
- reverse proxy and HTTPS hardening
- tighter database permissions
- improved deployment security controls
- stronger observability and incident-response support
