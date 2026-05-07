# Support

We're here to help! This guide outlines how to get support for the Vivere con il Cane project.

## Quick Links

- 📚 [Documentation](README.md) - Complete project documentation
- 🐛 [Report a Bug](https://github.com/ballales1984-wq/vivere-con-il-cane/issues/new?template=bug_report.md)
- 💡 [Request a Feature](https://github.com/ballales1984-wq/vivere-con-il-cane/issues/new?template=feature_request.md)
- ❓ [Ask a Question](https://github.com/ballales1984-wq/vivere-con-il-cane/issues/new?template=question.md)
- 📖 [Knowledge Base](/it/knowledge/) - Articles about dog behavior, health, and training
- 🛠️ [Free Tools](/it/tool/) - Calculators, quizzes, and utilities

## Getting Help

### 1. Search Existing Resources

Before opening a new issue, please search:
- **Existing GitHub Issues** - Your question may already be answered
- **Knowledge Base** - Comprehensive guides on dog behavior and health
- **README** - Installation, configuration, and usage instructions
- **Contributing Guide** - Development setup and testing

### 2. Community Forum

For community support and discussions with other dog owners:
- Visit our [Community Forum](/it/community/)
- Browse existing discussions
- Create a new topic to ask questions

### 3. GitHub Issues

Use GitHub Issues for:

- **Bug Reports** - Something isn't working as expected
- **Feature Requests** - Suggest new functionality
- **Questions** - Development or deployment questions

Please use the appropriate issue template when creating a new issue.

### 4. Documentation

Project documentation is organized as follows:

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Project overview, installation, usage |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Development guidelines |
| [CHANGELOG.md](CHANGELOG.md) | Version history and changes |
| [SECURITY.md](SECURITY.md) | Security policy and reporting |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community guidelines |
| [TEST_REPORT.md](TEST_REPORT.md) | Latest test results |
| [DATABASE_TROUBLESHOOTING.md](DATABASE_TROUBLESHOOTING.md) | Database setup help |
| [GOOGLE_OAUTH_COMPLETE_GUIDE.md](GOOGLE_OAUTH_COMPLETE_GUIDE.md) | OAuth configuration |

## Response Time

We aim to respond to issues within **48-72 hours** during weekdays. For urgent matters, please label the issue as `priority: high`.

## Self-Hosted Deployment Support

If you're self-hosting the application:

1. Check [DATABASE_TROUBLESHOOTING.md](DATABASE_TROUBLESHOOTING.md) for database issues
2. Review environment variables in `.env.example`
3. Ensure all migrations are applied: `python manage.py migrate`
4. Load fixtures: `python manage.py loaddata knowledge/fixtures/knowledge_data.json`
5. Check the server logs for error messages

## Cloud Deployment (Render.com)

For deployments on Render:
- Set all required environment variables in the Render dashboard
- Verify the database is provisioned and `DATABASE_URL` is set
- Ensure Redis is configured for caching
- Check build logs for any dependency issues

## Professional Support

For commercial support, custom development, or consulting:

- Contact: [INSERT CONTACT EMAIL OR FORM]
- Services: Custom features, deployment assistance, training, integration

## Feedback

We value your feedback! Let us know how we can improve the project:

- Open an issue with the `enhancement` label
- Participate in discussions
- Submit a pull request with improvements

---

**Thank you for using Vivere con il Cane!**
