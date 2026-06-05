import json

from django.db import migrations, models
from django.utils.text import slugify


def migrate_json_taxonomy_to_relations(apps, schema_editor):
    Profile = apps.get_model("devhub_app", "Profile")
    Project = apps.get_model("devhub_app", "Project")
    Skill = apps.get_model("devhub_app", "Skill")
    Technology = apps.get_model("devhub_app", "Technology")

    def table_exists(table_name):
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name = %s",
                [table_name],
            )
            return cursor.fetchone() is not None

    def table_columns(table_name):
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            return {row[1] for row in cursor.fetchall()}

    def load_json_list(raw_value):
        if raw_value in (None, ""):
            return []
        if isinstance(raw_value, list):
            return raw_value
        try:
            parsed = json.loads(raw_value)
        except (TypeError, json.JSONDecodeError):
            return []
        return parsed if isinstance(parsed, list) else []

    profile_exists = table_exists("devhub_app_profile")
    project_exists = table_exists("devhub_app_project")
    profile_columns = table_columns("devhub_app_profile") if profile_exists else set()
    project_columns = table_columns("devhub_app_project") if project_exists else set()
    profile_source = "skills" if "skills" in profile_columns else "legacy_skills" if "legacy_skills" in profile_columns else None
    project_source = (
        "tech_stack" if "tech_stack" in project_columns else "legacy_tech_stack" if "legacy_tech_stack" in project_columns else None
    )

    profile_rows = []
    if profile_exists:
        with schema_editor.connection.cursor() as cursor:
            if profile_source:
                cursor.execute(f"SELECT id, {profile_source} FROM devhub_app_profile")  # nosec B608
                profile_rows = cursor.fetchall()

            else:
                cursor.execute("SELECT id FROM devhub_app_profile")
                profile_rows = [(row[0], None) for row in cursor.fetchall()]

    for profile_id, raw_names in profile_rows:
        names = load_json_list(raw_names)
        skill_ids = []
        for name in names:
            cleaned = (name or "").strip()
            if not cleaned:
                continue
            skill, _ = Skill.objects.get_or_create(name=cleaned, defaults={"slug": slugify(cleaned)})
            skill_ids.append(skill.id)
        if skill_ids:
            Profile.objects.get(pk=profile_id).skills.set(skill_ids)

    project_rows = []
    if project_exists:
        with schema_editor.connection.cursor() as cursor:
            if project_source:
                cursor.execute(f"SELECT id, {project_source} FROM devhub_app_project")  # nosec B608
                project_rows = cursor.fetchall()

            else:
                cursor.execute("SELECT id FROM devhub_app_project")
                project_rows = [(row[0], None) for row in cursor.fetchall()]

    for project_id, raw_names in project_rows:
        names = load_json_list(raw_names)
        technology_ids = []
        for name in names:
            cleaned = (name or "").strip()
            if not cleaned:
                continue
            technology, _ = Technology.objects.get_or_create(name=cleaned, defaults={"slug": slugify(cleaned)})
            technology_ids.append(technology.id)
        if technology_ids:
            Project.objects.get(pk=project_id).technologies.set(technology_ids)


def drop_legacy_json_columns(apps, schema_editor):
    def table_exists(table_name):
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name = %s",
                [table_name],
            )
            return cursor.fetchone() is not None

    def table_columns(table_name):
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            return {row[1] for row in cursor.fetchall()}

    if table_exists("devhub_app_profile"):
        for column in ("legacy_skills", "skills"):
            if column in table_columns("devhub_app_profile"):
                schema_editor.execute(f'ALTER TABLE "devhub_app_profile" DROP COLUMN "{column}"')
                break

    if table_exists("devhub_app_project"):
        for column in ("legacy_tech_stack", "tech_stack"):
            if column in table_columns("devhub_app_project"):
                schema_editor.execute(f'ALTER TABLE "devhub_app_project" DROP COLUMN "{column}"')
                break


class Migration(migrations.Migration):
    dependencies = [
        ("devhub_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Skill",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, unique=True)),
                ("slug", models.SlugField(max_length=90, unique=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Technology",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, unique=True)),
                ("slug", models.SlugField(max_length=90, unique=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RenameField(
                    model_name="profile",
                    old_name="skills",
                    new_name="legacy_skills",
                ),
            ],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RenameField(
                    model_name="project",
                    old_name="tech_stack",
                    new_name="legacy_tech_stack",
                ),
            ],
        ),
        migrations.AddField(
            model_name="profile",
            name="skills",
            field=models.ManyToManyField(blank=True, related_name="profiles", to="devhub_app.skill"),
        ),
        migrations.AddField(
            model_name="project",
            name="technologies",
            field=models.ManyToManyField(blank=True, related_name="projects", to="devhub_app.technology"),
        ),
        migrations.RunPython(migrate_json_taxonomy_to_relations, migrations.RunPython.noop),
        migrations.RunPython(drop_legacy_json_columns, migrations.RunPython.noop),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="profile",
                    name="legacy_skills",
                ),
            ],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="project",
                    name="legacy_tech_stack",
                ),
            ],
        ),
    ]
