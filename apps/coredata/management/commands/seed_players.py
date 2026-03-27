import csv
import os
from django.core.management.base import BaseCommand
from coredata.models import Player, Nationality


class Command(BaseCommand):
    help = "Seed players from CSV (skip duplicates, skip empty CI)"

    def handle(self, *args, **kwargs):
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "../data/players.csv"
        )
        file_path = os.path.abspath(file_path)

        created_count = 0
        skipped_existing = 0
        skipped_no_ci = 0
        skipped_invalid = 0

        # --- Pre-load nationality lookup: code -> Nationality instance ---
        nationality_map = {n.code: n for n in Nationality.objects.all()}

        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                ci_id = (row.get("ci_player_id") or "").strip()

                # Skip if no CI ID
                if not ci_id:
                    skipped_no_ci += 1
                    continue

                # Skip if already exists
                if Player.objects.filter(ci_player_id=ci_id).exists():
                    skipped_existing += 1
                    continue

                # ---- Nationality: resolve from nationality_code ----
                nat_code = (row.get("nationality_code") or "").strip()
                nationality = nationality_map.get(nat_code)
                if not nationality:
                    self.stdout.write(self.style.ERROR(
                        f"❌ Invalid/missing nationality code: '{nat_code}' for ci_id={ci_id}"
                    ))
                    skipped_invalid += 1
                    continue

                # ---- Normalize + validate choice fields ----
                gender_raw = (row.get("gender") or "").strip().upper()
                gender = gender_raw if gender_raw in ("MALE", "FEMALE", "OTHER") else "MALE"

                role_raw = (row.get("role") or "").strip().upper()
                valid_roles = {"BATTER", "BOWLER", "ALL_ROUNDER", "WICKET_KEEPER"}
                role = role_raw if role_raw in valid_roles else None

                batting_hand_raw = (row.get("batting_hand") or "").strip().upper()
                batting_hand = batting_hand_raw if batting_hand_raw in ("LEFT", "RIGHT") else None

                bowling_hand_raw = (row.get("bowling_hand") or "").strip().upper()
                bowling_hand = bowling_hand_raw if bowling_hand_raw in ("LEFT", "RIGHT") else None

                bowling_type_raw = (row.get("bowling_type") or "").strip().upper()
                valid_bowling_types = {"PACE", "MEDIUM", "SPIN"}
                bowling_type = bowling_type_raw if bowling_type_raw in valid_bowling_types else None

                # ---- Optional fields ----
                dob_raw = (row.get("date_of_birth") or "").strip()
                date_of_birth = dob_raw if dob_raw else None

                def to_int_or_none(val):
                    try:
                        return int(float(val)) if val and str(val).strip() else None
                    except (ValueError, TypeError):
                        return None

                # ---- Create Player ----
                Player.objects.create(
                    ci_player_id=ci_id,
                    first_name=row.get("first_name", "").strip(),
                    middle_name=row.get("middle_name", "").strip(),
                    last_name=row.get("last_name", "").strip(),
                    nick_name=row.get("nick_name", "").strip(),
                    nationality=nationality,
                    date_of_birth=date_of_birth,
                    gender=gender,
                    height_cm=to_int_or_none(row.get("height_cm")),
                    weight_kg=to_int_or_none(row.get("weight_kg")),
                    role=role,
                    batting_hand=batting_hand,
                    bowling_hand=bowling_hand,
                    bowling_type=bowling_type,
                    bowling_style=row.get("bowling_style", "").strip(),
                    # SYSTEM data
                    owner_type="SYSTEM",
                    owner_id=None,
                    is_locked=True,
                )

                created_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Created: {ci_id} - {row.get('first_name')} {row.get('last_name')}"
                ))

        # ---- Summary ----
        self.stdout.write(self.style.SUCCESS(
            f"""
================ RESULT =================
Created              : {created_count}
Skipped (exists)     : {skipped_existing}
Skipped (no CI)      : {skipped_no_ci}
Skipped (invalid)    : {skipped_invalid}
========================================
"""
        ))