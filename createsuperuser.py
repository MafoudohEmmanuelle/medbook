import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medbook.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        password=password,
        first_name="Admin",
        last_name="User",
        role="ADMIN"  
    )
    print("✅ Superuser created successfully.")
else:
    print("⚠️ Superuser already exists.")
