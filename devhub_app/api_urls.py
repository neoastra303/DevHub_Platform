from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CommentViewSet,
    NotificationViewSet,
    PostViewSet,
    ProjectViewSet,
    audit_export_request,
    audit_log_list,
    background_job_detail,
    background_job_download,
    background_job_list,
    dashboard_summary,
    featured_project,
    profile_detail,
    transaction_list,
    analytics_summary,
)

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="posts")
router.register(r"projects", ProjectViewSet, basename="projects")
router.register(r"comments", CommentViewSet, basename="comments")
router.register(r"notifications", NotificationViewSet, basename="notifications")

urlpatterns = [
    path("audit/", audit_log_list, name="api-audit"),
    path("audit/export/", audit_export_request, name="api-audit-export"),
    path("jobs/", background_job_list, name="api-jobs"),
    path("jobs/<int:job_id>/", background_job_detail, name="api-job-detail"),
    path("jobs/<int:job_id>/download/", background_job_download, name="api-job-download"),
    path("dashboard-summary/", dashboard_summary, name="dashboard-summary"),
    path("profile/", profile_detail, name="api-profile"),
    path("featured-project/", featured_project, name="api-featured-project"),
    path("transactions/", transaction_list, name="api-transactions"),
    path("analytics/", analytics_summary, name="api-analytics"),
]

urlpatterns += router.urls
