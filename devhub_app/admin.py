from django.contrib import admin

from .models import AuditLog, Post, Profile, Project, Skill, Technology, TransactionLog


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "headline", "reputation", "points", "active_projects")
    search_fields = ("user__username", "user__first_name", "user__last_name", "headline")
    filter_horizontal = ("skills",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "stack_summary", "is_featured", "created_at")
    list_filter = ("is_featured", "created_at")
    search_fields = ("title", "owner__username", "summary")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("technologies",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title", "content", "author__username")


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "user", "amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("transaction_id", "user__username")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "content_type", "object_id", "actor", "created_at")
    list_filter = ("action", "content_type", "created_at")
    search_fields = ("object_id", "actor__username")
