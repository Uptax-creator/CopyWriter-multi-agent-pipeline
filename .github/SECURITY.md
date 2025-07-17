# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.x.x   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability, please follow these steps:

### 1. **Do Not** Create a Public Issue
Please do not create a public GitHub issue for security vulnerabilities.

### 2. Report Privately
Send an email to: **security@uptax.com**

Include the following information:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if available)

### 3. Response Timeline
- **Acknowledgment**: Within 24 hours
- **Initial Assessment**: Within 72 hours
- **Fix Timeline**: Depends on severity
  - Critical: Within 7 days
  - High: Within 14 days
  - Medium: Within 30 days
  - Low: Next scheduled release

### 4. Disclosure Policy
- We will work with you to understand and resolve the issue
- We will not disclose the vulnerability until a fix is available
- We will credit you in the security advisory (if desired)

## Security Best Practices

### For Contributors
- Never commit secrets, API keys, or passwords
- Use environment variables for sensitive configuration
- Follow secure coding practices
- Run security scans before submitting PRs

### For Users
- Keep your installation up to date
- Use strong, unique credentials
- Enable two-factor authentication where possible
- Monitor logs for suspicious activity
- Use HTTPS in production environments

## Security Features

### Authentication
- Token-based authentication for all ERP integrations
- Configurable token expiration
- Rate limiting to prevent abuse
- Audit logging for all authentication attempts

### Data Protection
- Encryption of sensitive data at rest
- Secure transmission (HTTPS/TLS)
- Input validation and sanitization
- No logging of sensitive information

### Access Control
- Role-based access control (RBAC)
- Principle of least privilege
- Regular access reviews
- Secure default configurations

## Vulnerability Management

### Dependency Scanning
- Automated scanning for known vulnerabilities
- Regular dependency updates
- Security advisories for dependencies

### Code Analysis
- Static code analysis (Bandit)
- Dynamic testing
- Penetration testing (quarterly)
- Code reviews for security concerns

## Incident Response

### In Case of a Security Breach
1. **Immediate Response** (0-1 hour)
   - Isolate affected systems
   - Assess scope of breach
   - Notify security team

2. **Short-term Response** (1-24 hours)
   - Contain the breach
   - Preserve evidence
   - Notify affected users

3. **Long-term Response** (24+ hours)
   - Implement fixes
   - Conduct post-incident review
   - Update security measures

## Security Contacts

- **Primary**: security@uptax.com
- **Emergency**: +55 11 9999-9999
- **PGP Key**: Available on request

## Compliance

This project follows:
- OWASP Top 10 security practices
- ISO 27001 guidelines
- Brazilian LGPD requirements
- Industry best practices for API security

## Security Updates

Security updates are released as patches to supported versions. Subscribe to our security mailing list for notifications:
- Email: security-updates@uptax.com
- GitHub: Watch this repository for security advisories

---

**Remember**: Security is everyone's responsibility. When in doubt, report it.