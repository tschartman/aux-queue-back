from django.apps import AppConfig


class FollowersConfig(AppConfig):
    name = 'followers'

    def ready(self):
        import followers.signals