from django.apps import AppConfig


class StarwarsrestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'starwarsrest'
    
    def ready(self):
        import starwarsrest.signals