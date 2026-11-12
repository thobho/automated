"""The custom User must exist before any other project migration (Django requirement)."""

import pytest
from django.conf import settings
from django.db.migrations.loader import MigrationLoader

PROJECT_APPS = {app.rsplit(".", 1)[-1] for app in settings.LOCAL_APPS}


@pytest.fixture(scope="module")
def loader():
    # connection=None: read migration files only, never touch the database.
    return MigrationLoader(None, ignore_no_migrations=True)


def test_accounts_initial_migration_creates_user(loader):
    migration = loader.get_migration("accounts", "0001_initial")
    created = [op.name for op in migration.operations if op.__class__.__name__ == "CreateModel"]
    assert created == ["User"]


def test_accounts_initial_depends_on_no_other_project_app(loader):
    migration = loader.get_migration("accounts", "0001_initial")
    project_deps = {app for app, _ in migration.dependencies if app in PROJECT_APPS}
    assert project_deps == set()


def test_every_other_project_migration_comes_after_user(loader):
    graph = loader.graph
    for app_label, name in graph.leaf_nodes():
        if app_label in PROJECT_APPS and app_label != "accounts":
            ancestors = graph.forwards_plan((app_label, name))
            assert ("accounts", "0001_initial") in ancestors, (app_label, name)
