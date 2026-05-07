# Database Troubleshooting Guide

This guide covers common database issues and their solutions for Vivere con il Cane.

## Table of Contents

- [SQLite Issues (Development)](#sqlite-issues-development)
- [PostgreSQL Setup (Production)](#postgresql-setup-production)
- [Render Database Issues](#render-database-issues)
- [Migration Problems](#migration-problems)
- [Permission Issues](#permission-issues)

## SQLite Issues (Development)

### Database file not created

**Problem:** `db.sqlite3` is not being created after running migrations.

**Solution:**
```bash
# Ensure you're in the project root directory
ls -la db.sqlite3

# Run migrations explicitly
python manage.py migrate

# Check database exists
ls -la db.sqlite3
```

### "Database is locked" error

**Problem:** `django.db.utils.OperationalError: database is locked`

**Solution:**
```bash
# Close any Django shell or management commands
# Check for running Python processes
taskkill //F //IM python.exe  # Windows
killall python  # Unix/MacOS

# If using IDE, ensure no database connections are open
# Restart your development server
```

### Permission denied on database file

**Problem:** `PermissionError: [Errno 13] Permission denied`

**Solution:**
```bash
# Fix permissions on database file
chmod 644 db.sqlite3

# On Windows, ensure file is not read-only
attrib -R db.sqlite3
```

## PostgreSQL Setup (Production)

### Connection refused

**Problem:** `psycopg2.OperationalError: connection to server refused`

**Solution:**
1. Ensure PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql
   ```
2. Check `DATABASE_URL` or individual DB settings in `.env`:
   ```
   DB_NAME=vivere_con_cane
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```
3. Verify PostgreSQL accepts local connections in `pg_hba.conf`

### Authentication failed

**Problem:** `FATAL: password authentication failed`

**Solution:**
```bash
# Reset PostgreSQL user password
sudo -u postgres psql
\password postgres
# Enter new password and update .env accordingly
```

### Migrations not applying

**Problem:** Migrations fail on PostgreSQL

**Solution:**
```bash
# Ensure PostgreSQL extensions are enabled
sudo -u postgres psql -d vivere_con_cane -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"

# Run migrations
python manage.py migrate --run-syncdb
```

## Render Database Issues

### DATABASE_URL not working

**Problem:** Render provides `DATABASE_URL` but app fails to connect.

**Solution:**
1. Ensure `dj-database-url` is in requirements.txt:
   ```
   dj-database-url>=1.4.0
   ```
2. Check settings.py uses:
   ```python
   DATABASES = {
       'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
   }
   ```
3. Verify the DATABASE_URL format in Render dashboard is correct

### Migrations fail on Render deploy

**Problem:** Build succeeds but migrations fail.

**Solution:**
1. Add explicit migrate command in build script:
   ```bash
   python manage.py migrate --noinput
   ```
2. Check Render logs for specific error messages
3. Ensure `ALLOWED_HOSTS` includes your Render domain

## Migration Problems

### "No migrations to apply" but models missing

**Problem:** Models exist but no tables in database.

**Solution:**
```bash
# Create migrations for existing models
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Verify tables created
python manage.py dbshell
.tables  # SQLite
\dt  # PostgreSQL
```

### Migration conflicts

**Problem:** Conflicting migrations between branches.

**Solution:**
```bash
# Reset migrations (DEVELOPMENT ONLY - never in production)
python manage.py migrate <app> zero
rm <app>/migrations/0*.py

# Recreate migrations
python manage.py makemigrations <app>
python manage.py migrate
```

### Fixture loading fails

**Problem:** `loaddata` fails with foreign key errors.

**Solution:**
```bash
# Load in correct order (knowledge before blog)
python manage.py loaddata knowledge/fixtures/knowledge_data.json --ignorenonexistent
python manage.py loaddata blog/fixtures/blog_data.json --ignorenonexistent
```

## Permission Issues

### Database file not writable

**Problem:** Cannot write to database file.

**Solution:**
```bash
# For SQLite, ensure file is writable
chmod 664 db.sqlite3
chown $USER db.sqlite3

# For PostgreSQL, verify user has permissions
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE vivere_con_cane TO postgres;"
```

### Media upload permission denied

**Problem:** User uploads fail with permission errors.

**Solution:**
```bash
# Ensure media directory exists and is writable
mkdir -p media
chmod 755 media
chmod -R 775 media/
```

## Quick Recovery Commands

```bash
# Reset database completely (DEVELOPMENT ONLY)
rm db.sqlite3
python manage.py migrate --run-syncdb
python manage.py loaddata knowledge/fixtures/knowledge_data.json --ignorenonexistent

# Check database status
python manage.py dbshell "PRAGMA database_list;"  # SQLite
python manage.py dbshell "\l"  # PostgreSQL
```

## Getting Help

If issues persist:
1. Check the error message in Django logs
2. Verify your `.env` file has correct database configuration
3. Check Render dashboard for database connection details
4. Open an issue on GitHub with the full error message