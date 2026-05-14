import re
from django.core.management.base import BaseCommand
from main_florife.models import StrongConcord

STRONG_RE = re.compile(r'\([^{}()]+?,\s*(\d+)\)')


class Command(BaseCommand):
    help = 'Extrae los números de Strong desde las definiciones y los guarda en strong_numbers'

    def handle(self, *args, **options):
        total = StrongConcord.objects.count()
        self.stdout.write(f'Procesando {total} registros...')

        updated = 0
        batch_size = 5000
        batch = []

        for sc in StrongConcord.objects.iterator(chunk_size=batch_size):
            if not sc.definition:
                continue
            m = STRONG_RE.search(sc.definition)
            numbers = [int(m[1])] if m else []
            if numbers:
                sc.strong_numbers = numbers
                batch.append(sc)
                updated += 1

            if len(batch) >= batch_size:
                StrongConcord.objects.bulk_update(batch, ['strong_numbers'])
                self.stdout.write(f'  - Procesados {updated}/{total}...')
                batch = []

        if batch:
            StrongConcord.objects.bulk_update(batch, ['strong_numbers'])

        self.stdout.write(self.style.SUCCESS(
            f'¡Éxito! {updated} registros actualizados con números de Strong.'
        ))
