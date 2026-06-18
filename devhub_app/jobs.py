import csv
import io

from celery import shared_task
from django.utils import timezone

from .models import AuditLog, BackgroundJob, Notification


@shared_task(bind=True)
def process_background_job_task(self, job_id):
    try:
        job = BackgroundJob.objects.get(pk=job_id)
    except BackgroundJob.DoesNotExist:
        return f"Job {job_id} not found"

    result = process_background_job(job)

    # Notify user when job finishes
    Notification.objects.create(
        recipient=job.requested_by,
        title=f"Job {job.get_job_type_display()} Complete",
        message=f"Your background job has finished with status: {job.get_status_display()}",
        link="/audit/" if job.job_type == BackgroundJob.JobType.AUDIT_EXPORT else ""
    )

    return result


def enqueue_audit_export_job(*, user, filters=None):
    job = BackgroundJob.objects.create(
        requested_by=user,
        job_type=BackgroundJob.JobType.AUDIT_EXPORT,
        payload={"filters": filters or {}, "requested_at": timezone.now().isoformat()},
    )
    process_background_job_task.delay(job.id)
    return job


def process_background_job(job):
    if job.status != BackgroundJob.Status.QUEUED:
        return job

    job.status = BackgroundJob.Status.RUNNING
    job.error_message = ""
    job.save(update_fields=["status", "error_message", "updated_at"])

    try:
        if job.job_type == BackgroundJob.JobType.AUDIT_EXPORT:
            _process_audit_export(job)
        else:
            raise ValueError(f"Unsupported job type '{job.job_type}'")
        job.status = BackgroundJob.Status.SUCCEEDED
        job.save(update_fields=["status", "result", "updated_at"])
    except Exception as exc:
        job.status = BackgroundJob.Status.FAILED
        job.error_message = str(exc)
        job.save(update_fields=["status", "error_message", "updated_at"])
        raise

    return job


def _process_audit_export(job):
    filters = (job.payload or {}).get("filters", {})
    logs = AuditLog.objects.filter(actor=job.requested_by).select_related("content_type")
    action = filters.get("action")
    target_type = filters.get("target_type")
    if action:
        logs = logs.filter(action=action)
    if target_type:
        logs = logs.filter(content_type__model=target_type)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "action", "target_type", "target_id", "created_at", "metadata"])
    for log in logs.order_by("-created_at"):
        writer.writerow([
            log.id, log.action, log.content_type.model,
            log.object_id, log.created_at.isoformat(), log.metadata,
        ])

    job.result = {
        "content_type": "text/csv",
        "filename": f"audit-export-{job.pk}.csv",
        "content": buffer.getvalue(),
        "row_count": logs.count(),
    }
