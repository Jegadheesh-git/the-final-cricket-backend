from django.core.management.base import BaseCommand
from coredata.models import Nationality

COUNTRIES = [
    ("India","IND"),
    ("Australia","AUS"),
    ("England","ENG"),
    ("Newzealand","NZ")
]

class Command(BaseCommand):
    help = "seed nationality data"

    def handle(self, *args, **kwargs):
        for name, code in COUNTRIES:
            Nationality.objects.get_or_create(
                code = code,
                defaults={"name":name}
            )

        self.stdout.write(self.style.SUCCESS("Nationalities seeded"))