#!/bin/bash
# Database Initialization Script for Vivere con il Cane
# This script ensures the database is properly set up with all migrations
# and creates a default admin user with known credentials

echo "==================================="
echo "Vivere con il Cane - DB Initialization"
echo "==================================="

# Change to project directory
cd /vivere-con-il-cane

# Run migrations
echo ""
echo "1. Running database migrations..."
python manage.py migrate --noinput

# Load initial data
echo ""
echo "2. Loading knowledge data..."
python manage.py loaddata knowledge/fixtures/knowledge_data.json --ignorenonexistent

# Load blog data
echo ""
echo "3. Loading blog data..."
python manage.py loaddata blog/fixtures/blog_data.json --ignorenonexistent

# Create default admin user if not exists
echo ""
echo "4. Creating default admin user..."
python manage.py shell << 'PYEOF'
from django.contrib.auth import get_user_model
User = get_user_model()

# Create admin user with known password
if not User.objects.filter(email='admin@vivereconilcane.com').exists():
    admin_user = User.objects.create_user(
        username='admin@vivereconilcane.com',
        email='admin@vivereconilcane.com',
        password='Admin123!'
    )
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    print("  ✓ Admin user created: admin@vivereconilcane.com / Admin123!")
else:
    print("  ✓ Admin user already exists")

# Create a test user for mobile testing
if not User.objects.filter(email='test@vivereconilcane.com').exists():
    test_user = User.objects.create_user(
        username='test@vivereconilcane.com',
        email='test@vivereconilcane.com',
        password='Test123!'
    )
    test_user.save()
    print("  ✓ Test user created: test@vivereconilcane.com / Test123!")
else:
    print("  ✓ Test user already exists")

# Reset password for existing ballales user
ballales = User.objects.filter(email='ballales1984@gmail.com').first()
if ballales:
    ballales.set_password('Ballales123!')
    ballales.save()
    print("  ✓ Password reset for: ballales1984@gmail.com / Ballales123!")

print("\n  ✓ Database initialization complete!")
PYEOF

echo ""
echo "==================================="
echo "Database setup complete!"
echo "Default credentials:"
echo "  Admin: admin@vivereconilcane.com / Admin123!"
echo "  Test:  test@vivereconilcane.com / Test123!"
echo "  Ballales: ballales1984@gmail.com / Ballales123!"
echo "==================================="