from django.core.management.base import BaseCommand

from devhub_app.jobs import process_background_job
from devhub_app.models import BackgroundJob


class Command(BaseCommand):
    help = "Process queued background jobs."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=20)

    def handle(self, *args, **options):
        limit = options["limit"]
        jobs = BackgroundJob.objects.filter(status=BackgroundJob.Status.QUEUED)[:limit]
        processed = 0
        for job in jobs:
            process_background_job(job)
            processed += 1
        self.stdout.write(self.style.SUCCESS(f"Processed {processed} jobs"))
