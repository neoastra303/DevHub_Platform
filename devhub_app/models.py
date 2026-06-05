from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Skill(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Technology(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Profile(TimestampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    headline = models.CharField(max_length=255)
    bio = models.TextField()
    avatar_seed = models.CharField(max_length=80, default="devhub")
    reputation = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)
    active_projects = models.PositiveIntegerField(default=0)
    skills = models.ManyToManyField(Skill, blank=True, related_name="profiles")

    def __str__(self):
        return f"Profile<{self.user.username}>"

    @property
    def skill_names(self):
        return list(self.skills.values_list("name", flat=True))

    def set_skill_names(self, names):
        skills = []
        for name in names:
            cleaned = name.strip()
            if not cleaned:
                continue
            skill, _ = Skill.objects.get_or_create(name=cleaned, defaults={"slug": slugify(cleaned)})
            skills.append(skill)
        self.skills.set(skills)


class Project(TimestampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    summary = models.CharField(max_length=255)
    description = models.TextField()
    technologies = models.ManyToManyField(Technology, blank=True, related_name="projects")
    demo_url = models.URLField(blank=True)
    source_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_featured", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "project"
            slug = base_slug
            counter = 2
            while Project.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def technology_names(self):
        return list(self.technologies.values_list("name", flat=True))

    @property
    def stack_summary(self):
        return ", ".join(self.technology_names[:3])

    def set_technology_names(self, names):
        technologies = []
        for name in names:
            cleaned = name.strip()
            if not cleaned:
                continue
            technology, _ = Technology.objects.get_or_create(name=cleaned, defaults={"slug": slugify(cleaned)})
            technologies.append(technology)
        self.technologies.set(technologies)


class Post(TimestampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=200)
    content = models.TextField()
    likes_count = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class TransactionLog(TimestampedModel):
    class Status(models.TextChoices):
        COMPLETED = "completed", "Completed"
        PENDING = "pending", "Pending"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions")
    transaction_id = models.CharField(max_length=32, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.transaction_id


class AuditLog(TimestampedModel):
    class Action(models.TextChoices):
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    target_type = models.CharField(max_length=60)
    target_id = models.CharField(max_length=64)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action}:{self.target_type}:{self.target_id}"


class BackgroundJob(TimestampedModel):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    class JobType(models.TextChoices):
        AUDIT_EXPORT = "audit_export", "Audit Export"

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="background_jobs",
    )
    job_type = models.CharField(max_length=40, choices=JobType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    payload = models.JSONField(default=dict, blank=True)
    result = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.job_type}:{self.status}:{self.pk}"


@receiver(post_save, sender=get_user_model())
def create_profile_for_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            headline="Developer",
            bio="This profile was created automatically.",
            avatar_seed=instance.username,
        )
