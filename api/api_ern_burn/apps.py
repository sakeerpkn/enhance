from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ApiErnBurnConfig(AppConfig):
    name = 'api.api_ern_burn'

    def ready(self):
        import api.api_ern_burn.signals