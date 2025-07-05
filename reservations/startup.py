from django.core.management import call_command
from django.contrib.auth.models import User
from .models import UserProfile

def run_startup_tasks():
    try:
        call_command('migrate')
    except Exception as e:
        print(f"Migracije nisu uspele: {e}")

    try:
        for user in User.objects.all():
            UserProfile.objects.get_or_create(user=user)
    except Exception as e:
        print(f"Greška prilikom dodavanja UserProfile: {e}")
