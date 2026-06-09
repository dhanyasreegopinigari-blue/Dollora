import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.management import call_command

from store.models import Category, Product


class Command(BaseCommand):
    help = "Load legacy catalog data and create/reset the legacy admin account."

    def handle(self, *args, **options):
        fixture = settings.BASE_DIR / "data.json"
        if not fixture.exists():
            self.stderr.write(self.style.ERROR(f"Fixture not found: {fixture}"))
            return

        if Product.objects.exists() or Category.objects.exists():
            self.stdout.write(self.style.WARNING("Legacy catalog data already exists. Skipping fixture load."))
        else:
            call_command("loaddata", str(fixture))

        # Backfill automatic discount badges for all products (old and new).
        for product in Product.objects.all():
            product.save(update_fields=["discount_percent"])

        User = get_user_model()
        admin_username = os.getenv("LEGACY_ADMIN_USERNAME", "admin")
        admin_password = os.getenv("LEGACY_ADMIN_PASSWORD", "Admin@12345")
        admin_email = os.getenv("LEGACY_ADMIN_EMAIL", "admin@dollora.local")

        admin_user, created = User.objects.get_or_create(
            username=admin_username,
            defaults={
                "email": admin_email,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        admin_user.email = admin_email or admin_user.email
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.set_password(admin_password)
        admin_user.save()

        self.stdout.write(
            self.style.SUCCESS(
                "Legacy data loaded successfully. "
                f"Admin login ready: {admin_username} / {admin_password}"
            )
        )
