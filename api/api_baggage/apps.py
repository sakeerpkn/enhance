import random
import string

from django.apps import AppConfig


def generate_username(size=10, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_qr():
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(6))


class ApiBaggageConfig(AppConfig):
    name = 'api.api_baggage'

    def ready(self):
        from api.api_baggage.models import PhysicalLocation
        PhysicalLocation.objects.update_or_create(name='Floor1', defaults={'name': 'Floor1'})
