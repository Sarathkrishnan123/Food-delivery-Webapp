from django.apps import AppConfig


class FoodappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foodapp'

    def ready(self):
        import foodapp.signals  
