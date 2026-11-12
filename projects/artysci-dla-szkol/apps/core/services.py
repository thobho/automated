"""Health and readiness checks. Views only turn these results into HTTP responses."""

import logging

from django.db import DEFAULT_DB_ALIAS, DatabaseError, connections
from django.db.migrations.executor import MigrationExecutor

logger = logging.getLogger(__name__)

OK = "ok"
ERROR = "error"
PENDING = "pending"


def check_database(alias: str = DEFAULT_DB_ALIAS) -> str:
    """Run `SELECT 1` on the database. Returns "ok" or "error"."""
    try:
        with connections[alias].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        logger.exception("Database health check failed")
        return ERROR
    return OK


def check_migrations(alias: str = DEFAULT_DB_ALIAS) -> str:
    """Returns "ok" when every migration is applied, "pending" otherwise, "error" if unknown."""
    try:
        executor = MigrationExecutor(connections[alias])
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    except DatabaseError:
        logger.exception("Migration readiness check failed")
        return ERROR
    return PENDING if plan else OK


def health() -> dict[str, str]:
    """Liveness: the process runs and can reach the database."""
    return {"db": check_database()}


def readiness() -> dict[str, str]:
    """Readiness: the database is reachable and the schema is fully migrated."""
    db = check_database()
    if db != OK:
        return {"db": db, "migrations": ERROR}
    return {"db": db, "migrations": check_migrations()}


def all_ok(result: dict[str, str]) -> bool:
    return all(value == OK for value in result.values())
