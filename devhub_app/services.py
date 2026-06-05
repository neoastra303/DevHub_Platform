from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Post, Profile, Project, TransactionLog


def bootstrap_demo_user():
    user_model = get_user_model()

    # Fast check without transaction
    user = user_model.objects.filter(username="demo").first()
    if user and Profile.objects.filter(user=user).exists() and Project.objects.filter(owner=user).exists():
        return user
    with transaction.atomic():
        user, created = user_model.objects.get_or_create(
            username="demo",
            defaults={
                "first_name": "Demo",
                "last_name": "Builder",
                "email": "demo@example.com",
            },
        )
        if created:
            user.set_password("demo-password-123")
            user.save(update_fields=["password"])

        profile, _ = Profile.objects.get_or_create(
            user=user,
            defaults={
                "headline": "Platform Engineer",
                "bio": "Demo account for first-run exploration.",
                "avatar_seed": "Demo",
            },
        )
        profile.set_skill_names(["Django", "REST APIs", "PostgreSQL"])

        if not Project.objects.filter(owner=user).exists():
            project = Project.objects.create(
                owner=user,
                title="Launch Readiness Workspace",
                summary="A demo project that shows the app structure after first boot.",
                description="This seeded project exists only to avoid an empty first-run experience.",
                demo_url="https://example.com/demo",
                source_url="https://example.com/source",
                is_featured=True,
            )
            project.set_technology_names(["Django", "Tailwind", "SQLite"])

        if not Post.objects.filter(author=user).exists():
            Post.objects.create(
                author=user,
                title="Welcome to DevHub",
                content="Create an account to replace this shared demo workspace with your own data.",
                likes_count=5,
                views=42,
            )

        if not TransactionLog.objects.filter(user=user).exists():
            TransactionLog.objects.create(
                user=user,
                transaction_id="DEMO-1001",
                amount=199.00,
                status=TransactionLog.Status.COMPLETED,
            )

    return user
