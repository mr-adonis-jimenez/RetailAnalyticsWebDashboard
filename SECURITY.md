# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Retail Web Analytics Dashboard seriously. If you discover a security vulnerability, please follow these steps:

### Where to Report

**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please report security vulnerabilities through one of the following channels:

1. **GitHub Security Advisories** (Preferred)
   - Navigate to the [Security tab](https://github.com/mr-adonis-jimenez/retail-web-analytics-dashboard/security)
   - Click "Report a vulnerability"
   - Fill out the advisory form

2. **Direct Email**
   - Send an email to: security@yourdomain.com
   - Subject: "[SECURITY] Vulnerability Report - Retail Analytics Dashboard"

### What to Include

Please provide as much information as possible:

- **Description**: Clear description of the vulnerability
- **Type**: What type of vulnerability (XSS, SQLi, CSRF, etc.)
- **Location**: Affected files, functions, or endpoints
- **Impact**: What can an attacker do with this vulnerability?
- **Reproduction**: Step-by-step instructions to reproduce
- **Proof of Concept**: Code, screenshots, or videos demonstrating the issue
- **Suggested Fix**: If you have ideas on how to fix it
- **Affected Versions**: Which versions are impacted
- **Environment**: OS, Python version, browser (if applicable)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Every 7 days until resolved
- **Fix Timeline**: 
  - **Critical**: 1-7 days
  - **High**: 7-30 days
  - **Medium**: 30-90 days
  - **Low**: 90+ days

### What to Expect

1. **Acknowledgment**: We'll confirm receipt of your report
2. **Assessment**: We'll evaluate the severity and impact
3. **Communication**: We'll keep you updated on progress
4. **Fix Development**: We'll develop and test a patch
5. **Disclosure**: We'll coordinate public disclosure with you
6. **Credit**: You'll be credited in our security advisories (if desired)

## Security Best Practices

### For Users

1. **Keep Updated**: Always use the latest version
2. **Secure Configuration**:
   - Use strong, unique passwords
   - Enable HTTPS in production
   - Set proper CORS policies
   - Use environment variables for secrets
3. **Database Security**:
   - Use strong PostgreSQL passwords
   - Restrict database access
   - Enable SSL for database connections
4. **Authentication**:
   - Use JWT tokens with short expiration
   - Implement rate limiting
   - Enable 2FA if available

### For Developers

1. **Dependency Management**:
   ```bash
   # Regularly update dependencies
   pip install --upgrade -r requirements.txt
   
   # Check for vulnerabilities
   pip-audit
   safety check
   ```

2. **Code Review**:
   - Review all PRs for security issues
   - Use static analysis tools (Bandit, Semgrep)
   - Follow OWASP Top 10 guidelines

3. **Secrets Management**:
   - Never commit secrets to Git
   - Use `.env` files (excluded from Git)
   - Rotate credentials regularly
   - Use secure secret storage (AWS Secrets Manager, HashiCorp Vault)

4. **Input Validation**:
   - Validate all user inputs
   - Use parameterized queries for SQL
   - Sanitize HTML output
   - Implement CSRF tokens

5. **Authentication & Authorization**:
   - Implement proper session management
   - Use secure password hashing (bcrypt, argon2)
   - Implement rate limiting on auth endpoints
   - Follow principle of least privilege

## Known Security Considerations

### Production Deployment

1. **Environment Variables**: Never use default or example values in production
2. **Debug Mode**: Ensure `DEBUG=False` in production
3. **Secret Key**: Use cryptographically random secret keys
4. **Database**: Use connection pooling and prepared statements
5. **HTTPS**: Always use TLS/SSL in production
6. **Headers**: Configure security headers (HSTS, CSP, X-Frame-Options)

### Third-Party Dependencies

We regularly scan our dependencies for known vulnerabilities using:
- Dependabot
- Snyk
- Safety
- pip-audit

## Security Features

### Current Implementation

- ✅ JWT-based authentication
- ✅ Password hashing with bcrypt
- ✅ CORS protection
- ✅ Rate limiting
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ XSS protection (template escaping)
- ✅ CSRF protection
- ✅ Secure session management

### Planned Security Enhancements

- 🔄 Two-factor authentication (2FA)
- 🔄 API key management
- 🔄 Audit logging
- 🔄 IP whitelisting
- 🔄 Advanced rate limiting per user
- 🔄 Security headers configuration

## Vulnerability Disclosure Policy

### Public Disclosure

We follow responsible disclosure:

1. **Coordination**: We coordinate with the reporter
2. **Fix Development**: We develop and test a fix
3. **Security Advisory**: We publish a GitHub Security Advisory
4. **Patch Release**: We release a patched version
5. **Public Announcement**: We make a public announcement
6. **CVE Assignment**: We request a CVE if applicable

### Timeline

- **Standard**: 90 days from initial report
- **Critical**: Expedited timeline (7-14 days)
- **With Active Exploitation**: Immediate (1-3 days)

## Security Updates

Subscribe to security updates:

1. Watch this repository
2. Enable GitHub Security Advisories notifications
3. Follow our [security advisories](https://github.com/mr-adonis-jimenez/retail-web-analytics-dashboard/security/advisories)

## Hall of Fame

We recognize security researchers who responsibly disclose vulnerabilities:

<!-- Security researchers will be listed here -->

*No vulnerabilities reported yet.*

## Contact

For security-related questions or concerns:

- **Email**: security@yourdomain.com
- **PGP Key**: Available upon request
- **Response Time**: Within 48 hours

## Legal

### Safe Harbor

We support safe harbor for security researchers who:

- Make a good faith effort to avoid privacy violations
- Minimize disruption to our services
- Provide reasonable time for us to respond
- Do not exploit vulnerabilities beyond proof of concept

### Out of Scope

- Denial of Service attacks
- Social engineering attacks
- Physical attacks
- Attacks against our infrastructure providers

---

**Last Updated**: January 25, 2026

Thank you for helping keep Retail Web Analytics Dashboard secure! 🔒
