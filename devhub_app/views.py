from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.db import IntegrityError, transaction
from django.db.models import F, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, UpdateView
from rest_framework import permissions, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .audit import record_audit_event
from .forms import PostForm, ProfileForm, ProjectForm, SignUpForm, TransactionLogForm
from .jobs import enqueue_audit_export_job
from .mixins import QueryValidationMixin
from .models import AuditLog, BackgroundJob, Comment, Notification, Post, PostLike, PostMetric, Project, TransactionLog
from .permissions import IsOwnerObjectPermission
from .serializers import (
    AuditLogSerializer,
    BackgroundJobSerializer,
    CommentSerializer,
    NotificationSerializer,
    PostSerializer,
    PostWriteSerializer,
    ProfileSerializer,
    ProjectSerializer,
    ProjectWriteSerializer,
    TransactionLogSerializer,
)
from .services import get_or_bootstrap_demo_user
from .throttling import ApiBurstThrottle, ApiWriteThrottle, check_ip_rate_limit


def _current_user(request):
    if request.user.is_authenticated:
        return request.user
    return get_or_bootstrap_demo_user()


def _shared_page_context(request):
    user = _current_user(request)
    profile = user.profile
    projects = Project.objects.filter(owner=user).prefetch_related("technologies")
    posts = Post.objects.filter(author=user)
    transactions = TransactionLog.objects.filter(user=user)

    # Cache the count if we are going to use it multiple times
    project_count = projects.count()
    if profile.active_projects != project_count:
        profile.active_projects = project_count
        profile.save(update_fields=["active_projects", "updated_at"])

    featured_project = projects.filter(is_featured=True).first() or projects.first()
    total_post_views = posts.aggregate(total=Sum("metrics__views"))["total"] or 0
    return {
        "workspace_user": user,
        "profile": profile,
        "featured_project": featured_project,
        "projects": projects,
        "transactions": transactions,
        "posts": posts,
        "total_post_views": total_post_views,
        "is_demo_workspace": not request.user.is_authenticated,
    }


def _paginate_response(request, queryset, serializer_class):
    paginator = PageNumberPagination()
    paginator.page_size = 10
    paginator.page_size_query_param = "page_size"
    paginator.max_page_size = 100
    page = paginator.paginate_queryset(queryset, request)
    serializer = serializer_class(page, many=True)
    return paginator.get_paginated_response(serializer.data)


def health_check(request):
    """
    Health check endpoint for production monitoring.
    Checks database connectivity.
    """
    try:
        from django.db import connections

        conn = connections["default"]
        conn.cursor()
    except Exception as e:
        return JsonResponse({"status": "unhealthy", "error": str(e)}, status=503)

    return JsonResponse({"status": "healthy", "version": "1.0.0"})


def landing_page(request):
    return render(request, "devhub_app/landing.html", _shared_page_context(request))


@login_required
def feed_page(request):
    return render(request, "devhub_app/feed.html", _shared_page_context(request))


@login_required
def dashboard_page(request):
    return render(request, "devhub_app/dashboard.html", _shared_page_context(request))


@login_required
def audit_page(request):
    context = _shared_page_context(request)
    logs = AuditLog.objects.filter(actor=request.user).select_related("content_type", "actor")
    jobs = BackgroundJob.objects.filter(requested_by=request.user, job_type=BackgroundJob.JobType.AUDIT_EXPORT)[:10]
    action = request.GET.get("action")
    target_type = request.GET.get("target_type")
    if action in {choice for choice, _ in AuditLog.Action.choices}:
        logs = logs.filter(action=action)
    if target_type:
        logs = logs.filter(content_type__model=target_type)
    context["audit_export_jobs"] = jobs
    context["audit_logs"] = logs[:50]
    return render(request, "devhub_app/audit_logs.html", context)


@login_required
def profile_page(request):
    context = _shared_page_context(request)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("devhub_app:profile")
    else:
        form = ProfileForm(instance=request.user.profile)
    context["form"] = form
    return render(request, "devhub_app/profile.html", context)


@login_required
def project_detail_page(request, slug):
    context = _shared_page_context(request)
    context["project"] = get_object_or_404(
        Project.objects.prefetch_related("technologies"), owner=request.user, slug=slug
    )
    return render(request, "devhub_app/project_detail.html", context)


@login_required
def transactions_page(request):
    context = _shared_page_context(request)
    if request.method == "POST":
        form = TransactionLogForm(request.POST)
        if form.is_valid():
            try:
                transaction = form.save(commit=False)
                transaction.user = request.user
                transaction.save()
                messages.success(request, "Transaction saved.")
                return redirect("devhub_app:transactions")
            except IntegrityError:
                form.add_error("transaction_id", "A transaction with this ID already exists.")
    else:
        form = TransactionLogForm()
    context["form"] = form
    return render(request, "devhub_app/transactions.html", context)


@transaction.atomic
def signup_page(request):
    if request.user.is_authenticated:
        return redirect("devhub_app:dashboard")
    if request.method == "POST" and not check_ip_rate_limit(request, "signup", limit=5, window_seconds=300):
        messages.error(request, "Too many signup attempts. Try again later.")
        response = render(request, "registration/signup.html", {"form": SignUpForm()}, status=429)
        return response
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data["email"]
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.save(update_fields=["email", "first_name", "last_name"])
            login(request, user)
            messages.success(request, "Account created.")
            return redirect("devhub_app:dashboard")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


class RateLimitedLoginView(LoginView):
    template_name = "registration/login.html"

    def post(self, request, *args, **kwargs):
        if not check_ip_rate_limit(request, "login", limit=10, window_seconds=300):
            messages.error(request, "Too many login attempts. Try again later.")
            return render(request, self.template_name, {"form": self.get_form()}, status=429)
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)


class DevHubPasswordResetView(PasswordResetView):
    template_name = "registration/password_reset_form.html"
    email_template_name = "registration/password_reset_email.txt"
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")

    def form_valid(self, form):
        messages.success(self.request, "If the account exists, a reset link has been sent.")
        return super().form_valid(form)


class DevHubPasswordResetDoneView(PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"


class DevHubPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")


class DevHubPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"


@login_required
def post_like_htmx(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like = PostLike.objects.filter(user=request.user, post=post).first()
    if like:
        like.delete()
        PostMetric.objects.filter(post=post).update(likes=F("likes") - 1)
    else:
        PostLike.objects.create(user=request.user, post=post)
        PostMetric.objects.filter(post=post).update(likes=F("likes") + 1)
    post.refresh_from_db()
    return render(
        request,
        "devhub_app/partials/post_likes.html",
        {"post": post},
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def analytics_summary(request):
    """
    Returns analytics data for the user's posts over the last 30 days.
    """
    user = request.user
    posts = Post.objects.filter(author=user)

    # Mocking time-series data based on actual post views for visualization
    # In a real app, this would query a dedicated Analytics/Metric model
    labels = []
    data = []
    now = timezone.now()

    for i in range(7, -1, -1):
        day = now - timedelta(days=i)
        labels.append(day.strftime("%b %d"))
        # Deterministic pseudo-random data based on total post views
        total_views = posts.aggregate(total=Sum("metrics__views"))["total"] or 0
        data.append(int((total_views / 10) * (1 + (i % 3) * 0.2)))

    return Response(
        {
            "labels": labels,
            "datasets": [
                {
                    "label": "Views",
                    "data": data,
                }
            ],
        }
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def profile_skills_analytics(request):
    """
    Returns radar chart data for user skills based on projects and profile.
    """
    user = request.user
    profile = user.profile
    skills = profile.skill_names

    # Base skills from profile get a value of 80
    # Technologies from projects add 5 points each
    data = []
    labels = skills[:6]  # Limit to 6 for best radar look

    for skill in labels:
        score = 60
        # Check how many projects use this skill (case insensitive)
        count = Project.objects.filter(owner=user, technologies__name__icontains=skill).count()
        score += min(count * 10, 40)
        data.append(score)

    return Response({"labels": labels, "data": data})


class OwnerQuerySetMixin(LoginRequiredMixin):
    def get_queryset(self):
        return super().get_queryset().filter(**{self.owner_field: self.request.user})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "devhub_app/post_form.html"
    success_url = reverse_lazy("devhub_app:feed")

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        PostMetric.objects.get_or_create(post=post)
        record_audit_event(actor=self.request.user, action=AuditLog.Action.CREATE, target=post)
        messages.success(self.request, "Post created.")
        return redirect(self.success_url)


class PostUpdateView(OwnerQuerySetMixin, UpdateView):
    model = Post
    owner_field = "author"
    form_class = PostForm
    template_name = "devhub_app/post_form.html"
    success_url = reverse_lazy("devhub_app:feed")

    def form_valid(self, form):
        original = self.get_object()
        response = super().form_valid(form)
        record_audit_event(
            actor=self.request.user,
            action=AuditLog.Action.UPDATE,
            target=self.object,
            metadata={"title_before": original.title, "title_after": self.object.title},
        )
        messages.success(self.request, "Post updated.")
        return response

    def get_success_url(self):
        return str(self.success_url)


class PostDeleteView(OwnerQuerySetMixin, DeleteView):
    model = Post
    owner_field = "author"
    template_name = "devhub_app/confirm_delete.html"
    success_url = reverse_lazy("devhub_app:feed")

    def form_valid(self, form):
        record_audit_event(actor=self.request.user, action=AuditLog.Action.DELETE, target=self.object)
        messages.success(self.request, "Post deleted.")
        return super().form_valid(form)


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "devhub_app/project_form.html"

    def form_valid(self, form):
        project = form.save(commit=False)
        project.owner = self.request.user
        project.save()
        project.set_technology_names(form.cleaned_data.get("tech_stack_text", "").split(","))
        record_audit_event(actor=self.request.user, action=AuditLog.Action.CREATE, target=project)
        messages.success(self.request, "Project created.")
        return redirect("devhub_app:project-detail", slug=project.slug)


class ProjectUpdateView(OwnerQuerySetMixin, UpdateView):
    model = Project
    owner_field = "owner"
    form_class = ProjectForm
    template_name = "devhub_app/project_form.html"

    def form_valid(self, form):
        original = self.get_object()
        response = super().form_valid(form)
        record_audit_event(
            actor=self.request.user,
            action=AuditLog.Action.UPDATE,
            target=self.object,
            metadata={"title_before": original.title, "title_after": self.object.title},
        )
        messages.success(self.request, "Project updated.")
        return response

    def get_success_url(self):
        return reverse_lazy("devhub_app:project-detail", kwargs={"slug": self.object.slug})


class ProjectDeleteView(OwnerQuerySetMixin, DeleteView):
    model = Project
    owner_field = "owner"
    template_name = "devhub_app/confirm_delete.html"
    success_url = reverse_lazy("devhub_app:dashboard")

    def form_valid(self, form):
        record_audit_event(actor=self.request.user, action=AuditLog.Action.DELETE, target=self.object)
        messages.success(self.request, "Project deleted.")
        return super().form_valid(form)


class PostViewSet(QueryValidationMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerObjectPermission]
    throttle_classes = [ApiBurstThrottle, ApiWriteThrottle]
    throttle_scope = "api_write"

    def get_queryset(self):
        queryset = Post.objects.select_related("author").filter(author=self.request.user)
        query = self.request.query_params.get("q")
        ordering = self.request.query_params.get("ordering")
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(content__icontains=query))
        allowed_ordering = {
            "created_at",
            "-created_at",
            "metrics__views",
            "-metrics__views",
            "metrics__likes",
            "-metrics__likes",
            "title",
            "-title",
        }
        self.validate_choice_param("ordering", ordering, allowed_ordering)
        if ordering in allowed_ordering:
            queryset = queryset.order_by(ordering)
        return queryset

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return PostWriteSerializer
        return PostSerializer

    def get_throttles(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [throttle() for throttle in self.throttle_classes]
        return []

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        PostMetric.objects.get_or_create(post=post)
        record_audit_event(
            actor=self.request.user, action=AuditLog.Action.CREATE, target=post, metadata={"source": "api"}
        )

    def perform_update(self, serializer):
        post = serializer.save()
        record_audit_event(
            actor=self.request.user, action=AuditLog.Action.UPDATE, target=post, metadata={"source": "api"}
        )

    def perform_destroy(self, instance):
        record_audit_event(
            actor=self.request.user, action=AuditLog.Action.DELETE, target=instance, metadata={"source": "api"}
        )
        instance.delete()


class ProjectViewSet(QueryValidationMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerObjectPermission]
    throttle_classes = [ApiBurstThrottle, ApiWriteThrottle]
    throttle_scope = "api_write"

    def get_queryset(self):
        queryset = Project.objects.filter(owner=self.request.user).prefetch_related("technologies")
        query = self.request.query_params.get("q")
        technology = self.request.query_params.get("technology")
        featured = self.request.query_params.get("featured")
        ordering = self.request.query_params.get("ordering")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(summary__icontains=query) | Q(description__icontains=query)
            )
        if technology:
            queryset = queryset.filter(technologies__slug=technology)
        self.validate_choice_param("featured", featured, {"true", "false"}, "Use 'true' or 'false'.")
        if featured in {"true", "false"}:
            queryset = queryset.filter(is_featured=featured == "true")
        allowed_ordering = {"created_at", "-created_at", "title", "-title"}
        self.validate_choice_param("ordering", ordering, allowed_ordering)
        if ordering in allowed_ordering:
            queryset = queryset.order_by(ordering)
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return ProjectWriteSerializer
        return ProjectSerializer

    def get_throttles(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [throttle() for throttle in self.throttle_classes]
        return []

    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)
        record_audit_event(
            actor=self.request.user, action=AuditLog.Action.CREATE, target=project, metadata={"source": "api"}
        )

    def perform_update(self, serializer):
        project = serializer.save()
        record_audit_event(
            actor=self.request.user, action=AuditLog.Action.UPDATE, target=project, metadata={"source": "api"}
        )

    def perform_destroy(self, instance):
        record_audit_event(
            actor=self.request.user, action=AuditLog.Action.DELETE, target=instance, metadata={"source": "api"}
        )
        instance.delete()


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def audit_log_list(request):
    logs = AuditLog.objects.filter(actor=request.user).select_related("content_type", "actor")
    action = request.query_params.get("action")
    target_type = request.query_params.get("target_type")
    ordering = request.query_params.get("ordering")
    allowed_actions = {choice for choice, _ in AuditLog.Action.choices}
    if action and action not in allowed_actions:
        raise ValidationError({"action": [f"Unsupported action '{action}'."]})
    if action in allowed_actions:
        logs = logs.filter(action=action)
    if target_type:
        logs = logs.filter(content_type__model=target_type)
    allowed_ordering = {"created_at", "-created_at", "content_type__model", "-content_type__model"}
    if ordering and ordering not in allowed_ordering:
        raise ValidationError({"ordering": [f"Unsupported ordering '{ordering}'."]})
    if ordering in allowed_ordering:
        logs = logs.order_by(ordering)
    return _paginate_response(request, logs, AuditLogSerializer)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def audit_export_request(request):
    filters = {
        "action": request.data.get("action") or request.query_params.get("action") or "",
        "target_type": request.data.get("target_type") or request.query_params.get("target_type") or "",
    }
    if filters["action"] and filters["action"] not in {choice for choice, _ in AuditLog.Action.choices}:
        raise ValidationError({"action": [f"Unsupported action '{filters['action']}'."]})
    job = enqueue_audit_export_job(user=request.user, filters=filters)
    record_audit_event(
        actor=request.user,
        action=AuditLog.Action.CREATE,
        target=job,
        metadata={"source": "api", "kind": "audit_export_request"},
    )
    return Response({"ok": True, "job": BackgroundJobSerializer(job).data}, status=202)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def background_job_list(request):
    jobs = BackgroundJob.objects.filter(requested_by=request.user)
    job_type = request.query_params.get("job_type")
    status = request.query_params.get("status")
    if job_type in {choice for choice, _ in BackgroundJob.JobType.choices}:
        jobs = jobs.filter(job_type=job_type)
    if status in {choice for choice, _ in BackgroundJob.Status.choices}:
        jobs = jobs.filter(status=status)
    return _paginate_response(request, jobs, BackgroundJobSerializer)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def background_job_detail(request, job_id):
    job = get_object_or_404(BackgroundJob, pk=job_id, requested_by=request.user)
    return Response({"ok": True, "job": BackgroundJobSerializer(job).data})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def background_job_download(request, job_id):
    job = get_object_or_404(
        BackgroundJob,
        pk=job_id,
        requested_by=request.user,
        status=BackgroundJob.Status.SUCCEEDED,
    )
    content = (job.result or {}).get("content", "")
    filename = (job.result or {}).get("filename", f"job-{job.pk}.txt")
    content_type = (job.result or {}).get("content_type", "text/plain")
    response = HttpResponse(content, content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def dashboard_summary(request):
    context = _shared_page_context(request)
    profile = context["profile"]
    return Response(
        {
            "points": profile.points,
            "active_projects": context["projects"].count(),
            "reputation": profile.reputation,
            "total_post_views": context["total_post_views"],
        }
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def profile_detail(request):
    profile = request.user.profile
    profile.active_projects = Project.objects.filter(owner=request.user).count()
    profile.save(update_fields=["active_projects", "updated_at"])
    return Response(ProfileSerializer(profile).data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def featured_project(request):
    project = (
        Project.objects.filter(owner=request.user, is_featured=True).prefetch_related("technologies").first()
        or Project.objects.filter(owner=request.user).prefetch_related("technologies").first()
    )
    if not project:
        return Response({"detail": "No projects found."}, status=404)
    return Response(ProjectSerializer(project).data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def transaction_list(request):
    transactions = TransactionLog.objects.filter(user=request.user)
    status = request.query_params.get("status")
    ordering = request.query_params.get("ordering")
    allowed_statuses = {choice for choice, _ in TransactionLog.Status.choices}
    if status and status not in allowed_statuses:
        raise ValidationError({"status": [f"Unsupported status '{status}'."]})
    if status in allowed_statuses:
        transactions = transactions.filter(status=status)
    allowed_ordering = {"created_at", "-created_at", "amount", "-amount"}
    if ordering and ordering not in allowed_ordering:
        raise ValidationError({"ordering": [f"Unsupported ordering '{ordering}'."]})
    if ordering in allowed_ordering:
        transactions = transactions.order_by(ordering)
    return _paginate_response(request, transactions, TransactionLogSerializer)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerObjectPermission]
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)
        record_audit_event(
            actor=self.request.user, action=AuditLog.Action.CREATE, target=comment, metadata={"source": "api"}
        )

    def perform_update(self, serializer):
        comment = serializer.save()
        record_audit_event(
            actor=self.request.user, action=AuditLog.Action.UPDATE, target=comment, metadata={"source": "api"}
        )

    def perform_destroy(self, instance):
        record_audit_event(
            actor=self.request.user, action=AuditLog.Action.DELETE, target=instance, metadata={"source": "api"}
        )
        instance.delete()


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        queryset = Notification.objects.filter(recipient=self.request.user)
        return queryset

    @action(detail=True, methods=["post"], url_path="read")
    def mark_as_read(self, request, pk=None):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.is_read = True
        notification.save(update_fields=["is_read", "updated_at"])
        return Response({"ok": True})
