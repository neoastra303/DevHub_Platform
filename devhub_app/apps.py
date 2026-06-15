from django.apps import AppConfig


class DevhubAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "devhub_app"

    def ready(self):
        import devhub_app.signals  # noqa: F401
