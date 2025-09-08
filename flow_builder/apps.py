from django.apps import AppConfig


class FlowBuilderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'flow_builder'

    def ready(self):
        import flow_builder.signals  # Import to connect signals