from django.apps import AppConfig


class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'

    def ready(self):
        import account.signals
        from account.startup import ensure_default_admin, register_startup_hooks

        register_startup_hooks()
        ensure_default_admin()
