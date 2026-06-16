from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


class User(AbstractUser):
    """
    Custom User model to allow for future flexibility and demonstrate
    real-world best practices.
    """

    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

    def __repr__(self):
        return f"<User: {self.username}>"


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator

# ... (Previous imports)


class Skill(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, db_index=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Skill: {self.name}>"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Technology(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, db_index=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Technology: {self.name}>"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class SkillProficiency(models.Model):
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE, related_name="skill_proficiencies")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)

    class Meta:
        unique_together = ("profile", "skill")

    def __str__(self):
        return f"{self.profile.user.username} - {self.skill.name}: {self.level}"


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

    def __repr__(self):
        return f"<Profile: {self.user.username}>"

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
    slug = models.SlugField(unique=True, max_length=220, db_index=True)
    summary = models.CharField(max_length=255)
    description = models.TextField()
    technologies = models.ManyToManyField(Technology, blank=True, related_name="projects")
    demo_url = models.URLField(blank=True)
    source_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"<Project: {self.title[:50]}>"

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

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"<Post: {self.title[:50]}>"


class PostMetric(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="metrics")
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Metrics for {self.post.title}"

    def __repr__(self):
        return f"<PostMetric: {self.post.title[:50]} ({self.views}v, {self.likes}l)>"


class PostLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_post_like"),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"

    def __repr__(self):
        return f"<PostLike: {self.user.username} -> {self.post.title[:30]}>"


class ViewEvent(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="view_events")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"ViewEvent: {self.post.title} @ {self.created_at}"

    def __repr__(self):
        return f"<ViewEvent: {self.post.title[:30]} @ {self.created_at.date()}>"


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

    def __repr__(self):
        return f"<TransactionLog: {self.transaction_id} ({self.status}, ${self.amount})>"


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
    action = models.CharField(max_length=20, choices=Action.choices, db_index=True)

    # Generic relationship
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=64)
    content_object = GenericForeignKey("content_type", "object_id")

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action}:{self.content_type}:{self.object_id}"

    def __repr__(self):
        return f"<AuditLog: {self.action} {self.content_type.model}#{self.object_id}>"


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
    job_type = models.CharField(max_length=40, choices=JobType.choices, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED, db_index=True)
    payload = models.JSONField(default=dict, blank=True)
    result = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.job_type}:{self.status}:{self.pk}"

    def __repr__(self):
        return f"<BackgroundJob: {self.job_type} [{self.status}]>"


class Comment(TimestampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="comments", null=True, blank=True)
    content = models.TextField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post or self.project}"

    def __repr__(self):
        return f"<Comment: by {self.author.username}>"


class Notification(TimestampedModel):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"

    def __repr__(self):
        return f"<Notification: {self.title[:50]} {'✓' if self.is_read else '○'}>"



