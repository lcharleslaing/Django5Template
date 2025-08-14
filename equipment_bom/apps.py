from django.apps import AppConfig


class EquipmentBomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'equipment_bom'
    verbose_name = 'Equipment BOM Management'
    
    def ready(self):
        try:
            import equipment_bom.signals  # noqa
        except ImportError:
            pass
