from django.core.management.base import BaseCommand
from coredata.models import Nationality

COUNTRIES = [
    ("Afghanistan", "AFG"),
    ("Albania", "ALB"),
    ("Algeria", "ALG"),
    ("Argentina", "ARG"),
    ("Australia", "AUS"),
    ("Austria", "AUT"),
    ("Bangladesh", "BAN"),
    ("Belgium", "BEL"),
    ("Brazil", "BRA"),
    ("Canada", "CAN"),
    ("Chile", "CHI"),
    ("China", "CHN"),
    ("Colombia", "COL"),
    ("Denmark", "DEN"),
    ("Egypt", "EGY"),
    ("England", "ENG"),
    ("Finland", "FIN"),
    ("France", "FRA"),
    ("Germany", "GER"),
    ("Greece", "GRE"),
    ("Hong Kong", "HKG"),
    ("Hungary", "HUN"),
    ("India", "IND"),
    ("Indonesia", "INA"),
    ("Ireland", "IRE"),
    ("Israel", "ISR"),
    ("Italy", "ITA"),
    ("Japan", "JPN"),
    ("Kenya", "KEN"),
    ("Malaysia", "MAS"),
    ("Mexico", "MEX"),
    ("Morocco", "MAR"),
    ("Nepal", "NEP"),
    ("Netherlands", "NED"),
    ("New Zealand", "NZL"),
    ("Nigeria", "NGR"),
    ("Norway", "NOR"),
    ("Pakistan", "PAK"),
    ("Philippines", "PHI"),
    ("Poland", "POL"),
    ("Portugal", "POR"),
    ("Qatar", "QAT"),
    ("Russia", "RUS"),
    ("Saudi Arabia", "KSA"),
    ("Scotland", "SCO"),
    ("Singapore", "SGP"),
    ("South Africa", "RSA"),
    ("South Korea", "KOR"),
    ("Spain", "ESP"),
    ("Sri Lanka", "SL"),
    ("Sweden", "SWE"),
    ("Switzerland", "SUI"),
    ("Thailand", "THA"),
    ("Turkey", "TUR"),
    ("UAE", "UAE"),
    ("Uganda", "UGA"),
    ("Ukraine", "UKR"),
    ("United States", "USA"),
    ("West Indies", "WI"),
    ("Zimbabwe", "ZIM"),
]

class Command(BaseCommand):
    help = "seed nationality data"

    def handle(self, *args, **kwargs):
        created_count = 0
        updated_count = 0

        for name, code in COUNTRIES:
            obj, created = Nationality.objects.update_or_create(
                code=code,
                defaults={"name": name}
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {name} ({code})"))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"Updated: {name} ({code})"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone ✅ | Created: {created_count}, Updated: {updated_count}"
            )
        )