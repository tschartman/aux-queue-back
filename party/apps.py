from django.apps import AppConfig


class PartyConfig(AppConfig):
    name = 'party'

    def ready(self):
        import party.signals