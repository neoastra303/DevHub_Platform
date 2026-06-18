from django.core.management.base import BaseCommand

from devhub_app.services import get_or_bootstrap_demo_user


class Command(BaseCommand):
    help = "Seed the demo user and sample data for first-run exploration."

    def handle(self, *args, **options):
        user = get_or_bootstrap_demo_user()
        self.stdout.write(self.style.SUCCESS(f"Demo user ready: {user.username}"))
