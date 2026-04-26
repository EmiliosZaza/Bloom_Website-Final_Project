from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        # Load signals so UserProfile is auto-created on user registration
        import accounts.models