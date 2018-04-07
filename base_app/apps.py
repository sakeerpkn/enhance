from django.apps import AppConfig



class BaseAppConfig(AppConfig):
    name = 'base_app'

    def ready(self):
        levels = ['Silver','Gold','Platinum']
        from base_app.models import MembershipLevel
        # for level in levels:
        #     MembershipLevel.objects.update_or_create(name=level, defaults={'name': level})


