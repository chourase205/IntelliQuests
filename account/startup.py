import logging

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db import OperationalError
from django.db import ProgrammingError
from django.db import connections
from django.db.models.signals import post_migrate


logger = logging.getLogger(__name__)
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
_startup_hook_registered = False


def _auth_table_exists(using="default"):
    connection = connections[using]

    try:
        return get_user_model()._meta.db_table in connection.introspection.table_names()
    except (OperationalError, ProgrammingError):
        return False


def ensure_default_admin(sender=None, using="default", **kwargs):
    User = get_user_model()

    if not _auth_table_exists(using=using):
        return

    if User.objects.using(using).filter(is_superuser=True).exists():
        return

    try:
        User.objects.db_manager(using).create_superuser(
            username=DEFAULT_ADMIN_USERNAME,
            email="",
            password=DEFAULT_ADMIN_PASSWORD,
        )
        logger.info("Created default admin user '%s'.", DEFAULT_ADMIN_USERNAME)
    except IntegrityError:
        # Another process may have created the same user during startup.
        logger.info("Default admin user already exists; skipping creation.")


def register_startup_hooks():
    global _startup_hook_registered

    if _startup_hook_registered:
        return

    post_migrate.connect(
        ensure_default_admin,
        dispatch_uid="account.ensure_default_admin",
    )
    _startup_hook_registered = True
