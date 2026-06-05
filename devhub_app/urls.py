from django.urls import path

from .views import (
    DevHubPasswordResetCompleteView,
    DevHubPasswordResetConfirmView,
    DevHubPasswordResetDoneView,
    DevHubPasswordResetView,
    PostCreateView,
    PostDeleteView,
    PostUpdateView,
    ProjectCreateView,
    ProjectDeleteView,
    ProjectUpdateView,
    RateLimitedLoginView,
    audit_page,
    dashboard_page,
    feed_page,
    health_check,
    landing_page,
    profile_page,
    project_detail_page,
    signup_page,
    transactions_page,
)

app_name = "devhub_app"

urlpatterns = [
    path("", landing_page, name="landing"),
    path("health/", health_check, name="health"),
    path("accounts/login/", RateLimitedLoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/password-reset/", DevHubPasswordResetView.as_view(), name="password_reset"),
    path("accounts/password-reset/done/", DevHubPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("accounts/reset/<uidb64>/<token>/", DevHubPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("accounts/reset/done/", DevHubPasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("signup/", signup_page, name="signup"),
    path("audit/", audit_page, name="audit"),
    path("feed/", feed_page, name="feed"),
    path("dashboard/", dashboard_page, name="dashboard"),
    path("profile/", profile_page, name="profile"),
    path("posts/new/", PostCreateView.as_view(), name="post-create"),
    path("posts/<int:pk>/edit/", PostUpdateView.as_view(), name="post-edit"),
    path("posts/<int:pk>/delete/", PostDeleteView.as_view(), name="post-delete"),
    path("projects/new/", ProjectCreateView.as_view(), name="project-create"),
    path("projects/<slug:slug>/", project_detail_page, name="project-detail"),
    path("projects/<int:pk>/edit/", ProjectUpdateView.as_view(), name="project-edit"),
    path("projects/<int:pk>/delete/", ProjectDeleteView.as_view(), name="project-delete"),
    path("transactions/", transactions_page, name="transactions"),
]
