# 🐕 Vivere con il Cane - Database Troubleshooting Guide

## Problem: Database Credentials Not Found on Mobile

### Root Cause
When accessing the application from a mobile device, the SQLite database file may not be accessible or may not exist, and the application doesn't have proper default credentials configured.

### Solution

#### 1. Initialize the Database (Run Once)

The application requires database initialization to create tables and set up default users. Run this command:

```bash
cd /vivere-con-il-cane
python manage.py migrate --noinput
python manage.py loaddata knowledge/fixtures/knowledge_data.json --ignorenonexistent
python manage.py loaddata blog/fixtures/blog_data.json --ignorenonexistent
```

#### 2. Create Admin User (If Not Exists)

```bash
cd /vivere-con-il-cane
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Create admin user
if not User.objects.filter(email='admin@vivereconilcane.com').exists():
    admin = User.objects.create_user(
        username='admin@vivereconilcane.com',
        email='admin@vivereconilcane.com',
        password='Admin123!'
    )
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print('Admin created: admin@vivereconilcane.com / Admin123!')
else:
    print('Admin exists')
"
```

#### 3. Verify Database File Exists

```bash
cd /vivere-con-il-cane
ls -la db.sqlite3
```

Expected output: Database file should exist

#### 4. Test Authentication

```bash
cd /vivere-con-il-cane
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import authenticate

# Test credentials
credentials = [
    ('admin@vivereconilcane.com', 'Admin123!', 'Admin'),
    ('test@vivereconilcane.com', 'Test123!', 'Test User'),
    ('ballales1984@gmail.com', 'Ballales123!', 'Ballales')
]

for username, password, name in credentials:
    user = authenticate(username=username, password=password)
    if user:
        print(f'[OK] {name}: {username}')
    else:
        print(f'[FAIL] {name}: {username}')
"
```

### Default Credentials

| User Type | Email | Password | Access Level |
|-----------|-------|----------|--------------|
| Admin | `admin@vivereconilcane.com` | `Admin123!` | Full admin access |
| Test User | `test@vivereconilcane.com` | `Test123!` | Standard user |
| Existing User | `ballales1984@gmail.com` | `Ballales123!` | Standard user |

### Manual Database Reset

If the database is corrupted, you can reset it:

```bash
cd /vivere-con-il-cane

# Remove old database
rm db.sqlite3

# Recreate with migrations
python manage.py migrate --noinput

# Load fixtures
python manage.py loaddata knowledge/fixtures/knowledge_data.json --ignorenonexistent
python manage.py loaddata blog/fixtures/blog_data.json --ignorenonexistent

# Create admin user
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
admin = User.objects.create_superuser(
    username='admin@vivereconilcane.com',
    email='admin@vivereconilcane.com',
    password='Admin123!'
)
print('Admin user created')
"
```

### Configuration Checks

#### Check .env File

Ensure `.env` file contains:

```bash
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
```

#### Check settings.py

Verify database configuration in `config/settings.py`:

```python
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, conn_health_checks=True)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
```

### Mobile-Specific Considerations

1. **File Persistence**: SQLite database file must be on persistent storage, not in temp directories
2. **File Permissions**: Ensure the web server process can read/write the database file
3. **Deployment**: When deploying to platforms like Heroku or Render, use PostgreSQL instead of SQLite
4. **Session Consistency**: Mobile browsers may have different session handling; ensure cookies are configured correctly

### Common Errors and Fixes

| Error | Cause | Solution |
|-------|-------|----------|
| `no such table` | Migrations not run | Run `python manage.py migrate` |
| `unable to open database file` | Wrong permissions or path | Check file permissions and path |
| `OperationalError` | Database locked | Restart application server |
| `Authentication failed` | Wrong password or user exists | Reset password or recreate user |
| `404 on mobile` | URL configuration issue | Check ALLOWED_HOSTS and CSRF settings |

### Production Deployment

For production, consider using PostgreSQL:

```bash
# Update .env
DATABASE_URL=postgresql://user:password@localhost/dbname

# Run migrations
python manage.py migrate --noinput
```

### Database Backup

```bash
# Backup SQLite database
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d)

# Restore database
cp db.sqlite3.backup.20260506 db.sqlite3
```

### Support

If issues persist:
1. Check Django logs: `python manage.py check --deploy`
2. Verify migrations: `python manage.py showmigrations`
3. Test database connection: `python manage.py dbshell`
4. Review settings: `python manage.py diffsettings`