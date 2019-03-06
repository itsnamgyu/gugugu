import os

from django.core.management.base import BaseCommand
from django.conf import settings
from gugugu.models import TalkRegistration


class Command(BaseCommand):
    help = 'Export sg-talk registrations as csv.'

    def handle(self, *args, **kwargs):
        path = os.path.join(settings.BASE_DIR, 'registrations.csv')
        print('Saving data to {}... '.format(path), end='')
        TalkRegistration.export_as_csv(path)
        print('done!')
