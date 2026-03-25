"""
Django management command to seed wastage reasons.

Usage: python manage.py seed_wastage_reasons
"""

from django.core.management.base import BaseCommand
from api.models import WastageReason


class Command(BaseCommand):
    help = 'Seeds the database with predefined wastage reasons'

    def handle(self, *args, **options):
        """Execute the command to seed wastage reasons"""

        # Predefined wastage reasons
        WASTAGE_REASONS_DATA = [
            {
                'reason': 'Expired',
                'description': 'Products that have passed their expiration date'
            },
            {
                'reason': 'Damaged',
                'description': 'Products that are physically damaged or broken'
            },
            {
                'reason': 'Spilled',
                'description': 'Products that were accidentally spilled or lost'
            },
            {
                'reason': 'Theft',
                'description': 'Products lost due to theft or unauthorized removal'
            },
            {
                'reason': 'Spoiled',
                'description': 'Products that have spoiled due to improper storage'
            },
            {
                'reason': 'Pest Damage',
                'description': 'Products damaged by insects, rodents, or other pests'
            },
            {
                'reason': 'Burn',
                'description': 'Products burned or overcooked during production'
            },
            {
                'reason': 'Other',
                'description': 'Other wastage reasons not listed above'
            },
        ]

        created_count = 0
        skipped_count = 0

        self.stdout.write(self.style.WARNING('Starting wastage reasons seeding...'))
        self.stdout.write('')

        for reason_data in WASTAGE_REASONS_DATA:
            # Check if reason already exists
            if WastageReason.objects.filter(reason=reason_data['reason']).exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"✓ Skipped: '{reason_data['reason']}' (already exists)"
                    )
                )
                skipped_count += 1
                continue

            # Create the reason
            reason = WastageReason.objects.create(
                reason=reason_data['reason'],
                description=reason_data['description']
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Created: {reason.reason_id} - {reason.reason}"
                )
            )
            created_count += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS(f'Summary:'))
        self.stdout.write(self.style.SUCCESS(f'  Created: {created_count}'))
        self.stdout.write(self.style.WARNING(f'  Skipped: {skipped_count}'))
        self.stdout.write(self.style.SUCCESS(f'  Total:   {created_count + skipped_count}'))
        self.stdout.write(self.style.SUCCESS('='*50))
