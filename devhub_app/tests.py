from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import AuditLog, BackgroundJob, Notification, Post, PostMetric, Project, Skill, Technology, TransactionLog
from .services import bootstrap_demo_user

User = get_user_model()


class BaseTestCase(TestCase):
    def setUp(self):
        bootstrap_demo_user()
        self.user = User.objects.create_user(
            username="alice",
            password="password123A!",
            first_name="Alice",
            last_name="Stone",
            email="alice@example.com",
        )

    def login(self):
        self.client.login(username="alice", password="password123A!")


class PageRenderTests(BaseTestCase):
    def test_signup_page_renders(self):
        response = self.client.get(reverse("devhub_app:signup"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("devhub_app:dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_pages_render(self):
        self.login()
        project = Project.objects.create(
            owner=self.user,
            title="Private Workspace",
            summary="Summary",
            description="Description",
        )
        project.set_technology_names(["Django"])
        post = Post.objects.create(author=self.user, title="Hello", content="Private post")
        PostMetric.objects.create(post=post, views=1, likes=0)
        TransactionLog.objects.create(user=self.user, transaction_id="ALICE-1", amount=25, status=TransactionLog.Status.PENDING)
        for name in ["devhub_app:feed", "devhub_app:dashboard", "devhub_app:profile", "devhub_app:transactions"]:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)
        detail = self.client.get(reverse("devhub_app:project-detail", kwargs={"slug": project.slug}))
        self.assertEqual(detail.status_code, 200)

    def test_health_check_returns_200(self):
        response = self.client.get(reverse("devhub_app:health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")


class PostCRUDTests(BaseTestCase):
    def test_post_crud_is_user_owned(self):
        self.login()
        create_response = self.client.post(reverse("devhub_app:post-create"), {"title": "Owned", "content": "Owned content"})
        self.assertEqual(create_response.status_code, 302)
        post = Post.objects.get(title="Owned")
        self.assertEqual(post.author, self.user)

        other = User.objects.create_user(username="other", password="Password123!")
        foreign_post = Post.objects.create(author=other, title="Foreign", content="Forbidden")
        PostMetric.objects.create(post=foreign_post, views=1, likes=0)
        forbidden = self.client.get(reverse("devhub_app:post-edit", kwargs={"pk": foreign_post.pk}))
        self.assertEqual(forbidden.status_code, 404)


class APITests(BaseTestCase):
    def test_api_returns_paginated_filtered_current_user_objects(self):
        self.login()
        post1 = Post.objects.create(author=self.user, title="Mine", content="Visible content")
        PostMetric.objects.create(post=post1, views=10, likes=0)
        post2 = Post.objects.create(author=self.user, title="Another", content="Other content")
        PostMetric.objects.create(post=post2, views=99, likes=0)
        demo_user = User.objects.get(username="demo")
        post3 = Post.objects.create(author=demo_user, title="Demo hidden", content="Hidden")
        PostMetric.objects.create(post=post3, views=1, likes=0)
        response = self.client.get(reverse("posts-list"), {"q": "Visible", "ordering": "-metrics__views"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("results", payload)
        titles = [row["title"] for row in payload["results"]]
        self.assertIn("Mine", titles)
        self.assertNotIn("Demo hidden", titles)

    def test_api_validation_errors_have_structured_contract(self):
        self.login()
        response = self.client.get(reverse("projects-list"), {"featured": "maybe"})
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertFalse(payload["ok"])
        self.assertIn("error", payload)
        self.assertIn("details", payload["error"])
        self.assertIn("featured", payload["error"]["details"])

    def test_write_api_validation_rejects_bad_payloads(self):
        self.login()
        response = self.client.post(
            reverse("projects-list"),
            data={
                "title": "No",
                "summary": "short",
                "description": "too short",
                "tech_stack": ["Django"],
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertFalse(payload["ok"])
        self.assertIn("summary", payload["error"]["details"])

    def test_project_api_filtering_and_transaction_pagination(self):
        self.login()
        project = Project.objects.create(owner=self.user, title="Payments", summary="S", description="D", is_featured=True)
        project.set_technology_names(["Redis"])
        TransactionLog.objects.create(user=self.user, transaction_id="ALICE-3", amount=10, status=TransactionLog.Status.PENDING)
        TransactionLog.objects.create(user=self.user, transaction_id="ALICE-4", amount=20, status=TransactionLog.Status.COMPLETED)
        project_response = self.client.get(reverse("projects-list"), {"technology": "redis", "featured": "true"})
        self.assertEqual(project_response.status_code, 200)
        project_payload = project_response.json()
        self.assertEqual(project_payload["count"], 1)
        self.assertEqual(project_payload["results"][0]["title"], "Payments")

        transaction_response = self.client.get("/api/v1/devhub/transactions/", {"status": "completed", "page_size": 1})
        self.assertEqual(transaction_response.status_code, 200)
        transaction_payload = transaction_response.json()
        self.assertEqual(transaction_payload["count"], 1)
        self.assertEqual(transaction_payload["results"][0]["transaction_id"], "ALICE-4")


class ModelRelationshipTests(BaseTestCase):
    def test_can_create_project_and_transaction(self):
        self.login()
        project_response = self.client.post(
            reverse("devhub_app:project-create"),
            {
                "title": "Team Portal",
                "summary": "Workspace",
                "description": "Detailed project",
                "tech_stack_text": "Django, PostgreSQL",
                "demo_url": "https://example.com/demo",
                "source_url": "https://example.com/source",
                "is_featured": True,
            },
        )
        self.assertEqual(project_response.status_code, 302)
        transaction_response = self.client.post(
            reverse("devhub_app:transactions"),
            {"transaction_id": "ALICE-2", "amount": "99.99", "status": TransactionLog.Status.COMPLETED},
        )
        self.assertEqual(transaction_response.status_code, 302)
        self.assertTrue(Project.objects.filter(owner=self.user, title="Team Portal").exists())
        self.assertTrue(TransactionLog.objects.filter(user=self.user, transaction_id="ALICE-2").exists())
        self.assertTrue(Technology.objects.filter(name="Django").exists())

    def test_relational_skills_and_technologies_are_persisted(self):
        self.login()
        profile = self.user.profile
        profile.set_skill_names(["Python", "Django"])
        project = Project.objects.create(owner=self.user, title="API Hub", summary="s", description="d")
        project.set_technology_names(["PostgreSQL", "Docker"])
        self.assertEqual(set(profile.skill_names), {"Python", "Django"})
        self.assertEqual(set(project.technology_names), {"PostgreSQL", "Docker"})
        self.assertEqual(Skill.objects.count(), 4)


class AuditLogTests(BaseTestCase):
    def test_audit_logs_are_created_for_html_and_api_writes(self):
        self.login()
        self.client.post(reverse("devhub_app:post-create"), {"title": "Audit Post", "content": "Audit content body"})
        html_log = AuditLog.objects.filter(action=AuditLog.Action.CREATE).first()
        self.assertIsNotNone(html_log)
        self.assertEqual(html_log.actor, self.user)

        response = self.client.post(
            reverse("projects-list"),
            data={
                "title": "Audit Project",
                "summary": "A sufficiently long summary",
                "description": "A sufficiently long description for audit logging.",
                "demo_url": "https://example.com/demo",
                "tech_stack": ["Django", "Redis"],
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        api_log = AuditLog.objects.filter(action=AuditLog.Action.CREATE, metadata__source="api").first()
        self.assertIsNotNone(api_log)

    def test_audit_page_and_api_are_protected_and_scoped(self):
        page_response = self.client.get(reverse("devhub_app:audit"))
        self.assertEqual(page_response.status_code, 302)

        self.login()
        post = Post.objects.create(author=self.user, title="Post", content="Content")
        AuditLog.objects.create(
            actor=self.user,
            action=AuditLog.Action.CREATE,
            content_object=post,
            metadata={"source": "manual"},
        )
        other = User.objects.create_user(username="other2", password="Password123!")
        project = Project.objects.create(owner=other, title="Project", summary="s", description="d")
        AuditLog.objects.create(
            actor=other,
            action=AuditLog.Action.DELETE,
            content_object=project,
            metadata={"source": "manual"},
        )
        page_response = self.client.get(reverse("devhub_app:audit"))
        self.assertEqual(page_response.status_code, 200)
        self.assertContains(page_response, "Action")
        self.assertNotContains(page_response, ">Project<")

        api_response = self.client.get("/api/v1/devhub/audit/", {"action": "create"})
        self.assertEqual(api_response.status_code, 200)
        payload = api_response.json()
        self.assertEqual(payload["count"], 1)


class RateLimitTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        from django.core.cache import cache
        cache.clear()

    @override_settings(
        DEVHUB_API_WRITE_RATE="1/minute",
        DEVHUB_API_BURST_RATE="100/minute",
    )
    def test_api_write_rate_limit_is_enforced(self):
        self.login()
        first = self.client.post(
            reverse("posts-list"),
            data={"title": "Rate Limit Post", "content": "This is enough content to pass validation."},
            content_type="application/json",
        )
        self.assertEqual(first.status_code, 201)
        second = self.client.post(
            reverse("posts-list"),
            data={"title": "Rate Limit Again", "content": "This is enough content to pass validation."},
            content_type="application/json",
        )
        self.assertEqual(second.status_code, 429)
        payload = second.json()
        self.assertFalse(payload["ok"])

    def test_login_rate_limit_is_enforced(self):
        for _ in range(10):
            response = self.client.post(reverse("login"), {"username": "alice", "password": "wrong"})
            self.assertIn(response.status_code, {200, 302})
        blocked = self.client.post(reverse("login"), {"username": "alice", "password": "wrong"})
        self.assertEqual(blocked.status_code, 429)


class AuthFlowTests(BaseTestCase):
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_flow_sends_email(self):
        response = self.client.post(reverse("password_reset"), {"email": "alice@example.com"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("password reset", mail.outbox[0].subject.lower())


class BackgroundJobTests(BaseTestCase):
    def test_audit_export_job_can_be_queued_processed_and_downloaded(self):
        self.login()
        post = Post.objects.create(author=self.user, title="Audit Post", content="Content")
        AuditLog.objects.create(
            actor=self.user,
            action=AuditLog.Action.CREATE,
            content_object=post,
            metadata={"source": "manual"},
        )
        response = self.client.post("/api/v1/devhub/audit/export/", {"action": "create"})
        self.assertEqual(response.status_code, 202)
        job_id = response.json()["job"]["id"]
        job = BackgroundJob.objects.get(pk=job_id)
        self.assertEqual(job.status, BackgroundJob.Status.SUCCEEDED)

        listing = self.client.get("/api/v1/devhub/jobs/")
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.json()["count"], 1)

        download = self.client.get(f"/api/v1/devhub/jobs/{job.id}/download/")
        self.assertEqual(download.status_code, 200)
        self.assertIn("text/csv", download["Content-Type"])


class NotificationTests(BaseTestCase):
    def test_notification_mark_as_read_action(self):
        self.login()
        notification = Notification.objects.create(
            recipient=self.user,
            title="Build complete",
            message="Your export has finished.",
            is_read=False,
        )

        unread_list = self.client.get(reverse("notifications-list"))
        self.assertEqual(unread_list.status_code, 200)
        self.assertEqual(unread_list.json()["count"], 1)
        self.assertFalse(unread_list.json()["results"][0]["is_read"])

        response = self.client.post(reverse("notifications-mark-as-read", kwargs={"pk": notification.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])

        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
