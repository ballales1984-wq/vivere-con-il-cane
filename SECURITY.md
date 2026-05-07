# Security Policy

## Supported Versions

We currently support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of our project seriously. If you believe you have found a
security vulnerability, please report it to us as described below.

### How to Report a Security Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to [INSERT SECURITY EMAIL OR CONTACT FORM].

You should receive a response within 48 hours. If for some reason you do not,
please follow up via email to ensure we received your original message.

Please include the following information in your report:

- Type of issue (e.g. SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or exact URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### What to Expect

- You will receive an acknowledgement of your report within 48 hours.
- We will confirm the issue and determine its severity.
- We will work to fix the vulnerability as quickly as possible.
- We will keep you informed of the progress towards a fix and full disclosure.
- We will credit you in the security advisory and changelog (unless you prefer to remain anonymous).

### Disclosure Process

1. Report is received and assigned a primary handler.
2. Issue is confirmed and investigated.
3. Fix is developed and tested.
4. Release is prepared and security advisory is drafted.
5. **Coordinated public disclosure** - we publish the advisory and release the fix simultaneously.
6. Credit is given to the reporter (unless anonymity is requested).

### Security Best Practices for Users

If you are deploying this application, please ensure:

1. **Always use environment variables** for sensitive configuration (SECRET_KEY, database credentials, API keys)
2. **Keep dependencies updated** regularly with `pip install --upgrade -r requirements.txt`
3. **Enable HTTPS** in production, never run with `DEBUG=True`
4. **Use strong passwords** for admin accounts and enable 2FA if available
5. **Regularly backup** your database
6. **Limit access** to admin panels via firewall rules or IP whitelisting
7. **Monitor logs** for suspicious activity
8. **Keep secrets out of version control** - ensure `.env` is in `.gitignore`

---

*Last updated: 2026-05-07*
