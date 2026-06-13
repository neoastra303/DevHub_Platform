from rest_framework import serializers

from .models import AuditLog, BackgroundJob, Post, PostMetric, Profile, Project, TransactionLog, Comment, Notification


class PostMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMetric
        fields = ("views", "likes")


class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)
    metrics = PostMetricSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ("id", "title", "content", "metrics", "author_name", "created_at")


class PostWriteSerializer(serializers.ModelSerializer):
    def validate_title(self, value):
        cleaned = value.strip()
        if len(cleaned) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return cleaned

    def validate_content(self, value):
        cleaned = value.strip()
        if len(cleaned) < 10:
            raise serializers.ValidationError("Content must be at least 10 characters long.")
        return cleaned

    class Meta:
        model = Post
        fields = ("id", "title", "content")


class ProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    skills = serializers.ListField(child=serializers.CharField(), source="skill_names", read_only=True)

    class Meta:
        model = Profile
        fields = (
            "username",
            "full_name",
            "headline",
            "bio",
            "avatar_seed",
            "reputation",
            "points",
            "active_projects",
            "skills",
        )


class ProjectSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)
    tech_stack = serializers.ListField(child=serializers.CharField(), source="technology_names", read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "title",
            "slug",
            "summary",
            "description",
            "tech_stack",
            "demo_url",
            "source_url",
            "is_featured",
            "owner_name",
        )


class ProjectWriteSerializer(serializers.ModelSerializer):
    tech_stack = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)

    def validate_title(self, value):
        cleaned = value.strip()
        if len(cleaned) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return cleaned

    def validate_summary(self, value):
        cleaned = value.strip()
        if len(cleaned) < 10:
            raise serializers.ValidationError("Summary must be at least 10 characters long.")
        return cleaned

    def validate_description(self, value):
        cleaned = value.strip()
        if len(cleaned) < 20:
            raise serializers.ValidationError("Description must be at least 20 characters long.")
        return cleaned

    def validate(self, attrs):
        demo_url = attrs.get("demo_url")
        source_url = attrs.get("source_url")
        if not demo_url and not source_url:
            raise serializers.ValidationError(
                {"non_field_errors": ["Provide at least one of demo_url or source_url."]}
            )
        return attrs

    class Meta:
        model = Project
        fields = ("id", "title", "summary", "description", "demo_url", "source_url", "is_featured", "tech_stack")

    def create(self, validated_data):
        tech_stack = validated_data.pop("tech_stack", [])
        project = super().create(validated_data)
        project.set_technology_names(tech_stack)
        return project

    def update(self, instance, validated_data):
        tech_stack = validated_data.pop("tech_stack", None)
        project = super().update(instance, validated_data)
        if tech_stack is not None:
            project.set_technology_names(tech_stack)
        return project


class TransactionLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = TransactionLog
        fields = ("transaction_id", "user_name", "amount", "status", "status_label", "created_at")


class AuditLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)
    target_type = serializers.SerializerMethodField()
    target_id = serializers.CharField(source="object_id", read_only=True)

    def get_target_type(self, obj):
        return obj.content_type.model

    class Meta:
        model = AuditLog
        fields = ("id", "action", "target_type", "target_id", "actor_username", "metadata", "created_at")


class BackgroundJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackgroundJob
        fields = ("id", "job_type", "status", "payload", "result", "error_message", "created_at", "updated_at")


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "author_name", "post", "project", "content", "created_at")
        read_only_fields = ("id", "created_at", "author_name")


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "title", "message", "is_read", "link", "created_at")
        read_only_fields = ("id", "created_at")
