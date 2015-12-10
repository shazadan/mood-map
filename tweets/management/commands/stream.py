from django.core.management.base import BaseCommand, CommandError
from tweets.tasks import stream

#The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "My twitter stream command"

    # A command must define handle()
    def handle(self, *args, **options):
        stream()
