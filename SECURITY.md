# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | Yes       |

## Reporting a Vulnerability

If you discover a security issue, please **do not** open a public GitHub issue with exploit details.

1. Email the maintainer or use GitHub **Private vulnerability reporting** (if enabled).
2. Include steps to reproduce and impact assessment.
3. Allow reasonable time for a fix before public disclosure.

## Security Practices in This Project

- Secrets via environment variables and GitHub Actions secrets (never committed)
- Non-root Docker user
- Security headers on HTTP responses
- Trivy filesystem and image scanning in CI
- CodeQL static analysis
- Dependabot for dependency updates
- `.env` excluded from Git via `.gitignore`

## Production Checklist

- [ ] Set a strong `SECRET_KEY`
- [ ] Set `ENVIRONMENT=production`
- [ ] Use HTTPS (Render/load balancer or Nginx + TLS)
- [ ] Rotate Docker Hub tokens regularly
- [ ] Restrict EC2 security groups to required ports only
