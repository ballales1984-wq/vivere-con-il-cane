# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Full test suite with pytest (144 tests)
- Comprehensive documentation (README, CONTRIBUTING, API docs)
- Progressive Web App (PWA) support with offline capability
- HTMX integration for dynamic forms without JavaScript
- Multi-language support (Italian and English)
- Community forum with reputation and badge system
- Knowledge base with problem auto-detection
- AI-powered behavior analysis using Groq API
- Newsletter automation with follow-up sequence
- Dog profile management with health tracking
- PDF dossier generation

### Changed
- Migrated from OpenAI to Groq API exclusively for AI endpoints (commit 801c829)
- Standardized all AI endpoints to use GROQ_API_KEY (commit 5432e7b)
- Improved security headers and static file collection (commit 8062a9c)
- Fixed sitemap namespace and i18n issues (commit 686d9f9)

### Fixed
- Session cookie domain for mobile login consistency (commit bc9ac95)
- RateLimitMiddleware naming (commit 859ba79)
- Render deployment reliability (commit c9d8ca6)
- Database session handling and migration issues
- Duplicate HttpResponse import and null byte issue (commit 68853bc)

### Security
- Added django-ratelimit integration for API protection
- Configured CSRF trusted origins for production domains
- Implemented proper SECRET_KEY environment variable handling

### Infrastructure
- Added Docker support with Dockerfile and docker-compose.yml
- Configured for Render.com deployment (render.yaml)
- Added Redis caching support
- Health check endpoints and process management (Procfile, ecosystem.config.js)

---

## [0.1.0] - 2026-05-07 (Initial Release)

### Added
- Initial public release of Vivere con il Cane
- Complete Django project structure with modular apps
- Blog with AI article generation
- Canine tools (food calculator, age converter, quiz, heart recorder)
- Community forum with discussions, posts, likes, votes
- Dog profile management with analytics
- Knowledge base with behavioral problems and solutions
- Marketing system with newsletter subscription and automation
- Admin dashboard for content management
- All fixtures and initial data
- Basic documentation

---

## Version History Notes

**Note:** Earlier versions were in development and not formally tagged. The project
entered its stable phase with version 0.1.0. All commits from the repository's
inception are included in the initial release.

---

*This changelog was generated from git commit history and project documentation.*
