from django.apps import AppConfig


class PetrescueAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'petrescue_app'

    def ready(self):
        import petrescue_app.signals  # noqa
