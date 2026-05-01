# Vivere con il Cane

> Piattaforma completa per l'analisi del comportamento del cane con intelligenza artificiale, risorse gratuite, community e strumenti per proprietari di cani.

![Vivere con il Cane](static/images/logo.png)

## 📋 Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [API Endpoints](#-api-endpoints)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

- **AI Behavior Analysis**: Describe your dog's behavior and get personalized advice using AI
- **Free Tools**: 
  - Food Calculator - Calculate proper portions
  - Age Converter - Dog years to human years
  - Language Quiz - Test your knowledge of dog communication
  - Heart Recorder - Monitor your dog's heart rate
- **Learning Hub**: Articles, guides, and resources on dog education, health, nutrition
- **Community**: Forum for dog owners to share experiences and get support
- **Newsletter**: Automated onboarding sequence with welcome and follow-up emails
- **Dashboard**: Personal area to track your dog's profile and analysis history
- **Multi-language**: Italian and English support
- **PWA Ready**: Offline support, installable as mobile app
- **SEO Optimized**: Meta tags, structured data, sitemap
- **Ads Ready**: Google AdSense integration
- **Secure**: Proper authentication, password reset, email verification

## 📁 Project Structure

```
vivere-con-il-cane/
├── .github/                    # GitHub Actions and issue templates
├── .kilo/                      # Kilo CLI configuration (commands, agents, skills)
├── blog/                       # Main app: home, about, blog posts
├── canine_tools/               # Free tools: calculators, quizzes, heart recorder
├── community/                  # Forum and discussion features
├── config/                     # Django settings, URLs, WSGI
├── dog_profile/                # User dog profiles and analytics
├── knowledge/                  # Learning hub: articles, problems, solutions
├── marketing/                  # Newsletter, landing page, follow-up emails
├── requirements.txt            # Python dependencies
├── manage.py                   # Django management script
├── static/                     # Static files: CSS, JS, images
├── templates/                  # HTML templates
└── media/                      # User uploaded files (not in repo)
```

### Key Applications

| App | Description |
|-----|-------------|
| **blog** | Home page, about, blog posts, AI analysis |
| **canine_tools** | Free interactive tools for dog owners |
| **community** | Forum for discussions and support |
| **dog_profile** | Manage your dog's information and health |
| **knowledge** | Educational content: articles, problems, solutions |
| **marketing** | Newsletter system, landing page, email automation |

## ⚙️ Installation

### Prerequisites

- Python 3.8+
- pip
- Git
- (Optional) Docker for containerized deployment

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/ballales1984-wq/vivere-con-il-cane.git
   cd vivere-con-il-cane
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Unix/MacOS:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

   Minimum required variables:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ```

5. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load initial data (optional)**
   ```bash
   python manage.py loaddata knowledge/fixtures/knowledge_data.json
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

   Visit http://127.0.0.1:8000

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `True` |
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `EMAIL_BACKEND` | Email backend | `django.core.mail.backends.console.EmailBackend` |
| `GOOGLE_OAUTH_CLIENT_ID` | Google OAuth client ID | `your-client-id` |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Google OAuth client secret | `your-secret` |
| `GOOGLE_OAUTH_REDIRECT_URI` | OAuth redirect URI | `http://localhost:8000/auth/google/callback` |

### Email Configuration

For development, you can use the console backend:
```bash
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

For production, configure SMTP:
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Google APIs

To enable Google OAuth and Health/Fitness APIs:

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable:
   - Google+ API (for sign-in)
   - Fitness API
   - People API
3. Create OAuth 2.0 credentials
4. Set redirect URI to `http://localhost:8000/auth/google/callback`

## 🚀 Usage

### Admin Panel

Access the Django admin at `/admin/` with your superuser credentials.

### Main Features

1. **Home Page**: `/` - AI behavior analysis form
2. **About**: `/it/chi-sono/` - About Alessio and the project
3. **Blog**: `/it/blog/` - Articles and guides
4. **Tools**: `/it/tool/` - Free calculators and quizzes
5. **Knowledge**: `/it/knowledge/` - Educational content
6. **Community**: `/it/community/` - Forum discussions
7. **My Dog**: `/it/cane/` - Your dog's profile and analytics
8. **Newsletter**: `/landing/` - Marketing landing page
9. **Analysis Results**: `/analizza/` - Submit behavior for AI analysis

### Newsletter System

- Subscription: `/it/newsletter/subscribe/` (HTMX form)
- Unsubscription: `/unsubscribe/<token>/`
- Welcome email sent immediately
- Follow-up sequence:
  - Day 2: How to use AI for your dog
  - Day 5: Monitor your dog's health

### AI Analysis

Submit a description of your dog's behavior to get personalized advice based on:
- Breed characteristics
- Age-specific behaviors
- Veterinary knowledge
- Training best practices

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python manage.py test --debug-mode

# Run specific app tests
python manage.py test blog knowledge marketing --debug-mode

# Run with verbose output
python manage.py test blog -v 2
```

### Test Coverage

- Models: Validation, methods, relationships
- Views: Status codes, templates, context
- Forms: Validation, processing
- Utils: Helper functions, AI integration (mocked)

## ☁️ Deployment

### Render.com (Recommended)

1. Fork the repository
2. Create new Web Service on Render
3. Connect your GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python manage.py gunicorn config.wsgi:application`
6. Add environment variables in Render dashboard
7. Enable auto-deploy on push

### Docker

```bash
# Build image
docker build -t vivere-con-il-cane .

# Run container
docker run -p 8000:8000 \
  -e DEBUG=False \
  -e SECRET_KEY=your-secret-key \
  -e ALLOWED_HOSTS=yourdomain.com \
  vivere-con-il-cane
```

### Traditional Server

1. Install Python 3.8+, pip, virtualenv
2. Follow installation steps above
3. Set `DEBUG=False` in production
4. Configure a WSGI server (Gunicorn, uWSGI)
5. Set up reverse proxy (Nginx, Apache)
6. Enable SSL (Let's Encrypt recommended)

## 🔌 API Endpoints

### Public Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | Home page with AI analysis form |
| GET | `/analizza/` | Submit behavior for AI analysis |
| GET | `/landing/` | Marketing landing page |
| GET | `/it/tool/` | Free tools index |
| GET | `/it/knowledge/` | Learning hub index |
| GET | `/it/community/` | Community forum |
| POST | `/it/newsletter/subscribe/` | Newsletter subscription (HTMX) |
| GET | `/unsubscribe/<uuid:token>/` | Unsubscribe from newsletter |

### Protected Endpoints (require authentication)

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/it/cane/` | Dog profile dashboard |
| GET | `/it/accounts/profile/` | User profile |
| GET | `/it/accounts/logout/` | Logout |
| GET | `/it/dashboard/` | User dashboard |

### Admin Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/admin/` | Django admin login |
| GET | `/admin/blog/` | Blog post management |
| GET | `/admin/marketing/` | Newsletter subscribers |
| GET | `/admin/dog_profile/` | Dog profiles |

## 📚 Documentation

### Architecture Decisions

- **Modular Apps**: Separated concerns with Django apps
- **HTMX**: Used for dynamic forms without full page reloads
- **PWA**: Service worker and manifest for offline capability
- **i18n**: Built-in Django internationalization
- **Storage**: Local file storage for development, cloud storage (AWS S3) for production
- **Caching**: Redis recommended for production

### Database Models

Key models include:
- `BlogPost`: Articles and guides
- `KnowledgeProblem`: Behavioral problems with solutions
- `DogAnalysis`: AI analysis results
- `NewsletterSubscriber`: Email marketing list
- `DogProfile`: User's dog information
- `HeartSoundRecording`: Audio recordings for analysis

### Static Files

- CSS: `static/css/style.css` (main stylesheet)
- Images: `static/images/` (logos, photos, illustrations)
- JavaScript: Minimal vanilla JS, HTMX for AJAX

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Write tests for new features
- Keep commits atomic and descriptive
- Update documentation when changing functionality
- Respect the existing code style

### Reporting Issues

Please use the GitHub Issues tracker to report bugs or request features.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- Alessio - Founder and canine behavior expert
- The open-source Django community
- Contributors and testers
- Dog owners everywhere who make this work meaningful

---

**Made with ❤️ for dogs and their humans**

Last updated: May 2026