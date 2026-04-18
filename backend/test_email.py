import os
import django
from django.core.mail import send_mail
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def test_email():
    print(f"Testing email from: {settings.EMAIL_HOST_USER}")
    print(f"Using host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    try:
        send_mail(
            'Test Email',
            'If you see this, NSR BOOKS email setup is working!',
            settings.DEFAULT_FROM_EMAIL,
            ['karthikdreddy5@gmail.com'],
            fail_silently=False,
        )
        print("SUCCESS: Email sent successfully!")
    except Exception as e:
        print(f"ERROR: Failed to send email: {str(e)}")

if __name__ == "__main__":
    test_email()
