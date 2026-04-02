from django.core.management.base import BaseCommand
from core.models import District


DISTRICTS = {
    'Central': [
        'Buikwe', 'Bukomansimbi', 'Buvuma', 'Gomba', 'Kampala', 'Kayunga',
        'Kiboga', 'Kyankwanzi', 'Luweero', 'Lwengo', 'Lyantonde', 'Masaka',
        'Mityana', 'Mpigi', 'Mubende', 'Mukono', 'Nakaseke', 'Nakasongola',
        'Rakai', 'Sembabule', 'Wakiso', 'Kalungu', 'Butebo',
    ],
    'Eastern': [
        'Amuria', 'Budaka', 'Bududa', 'Bugiri', 'Bugweri', 'Bukedea',
        'Bukwa', 'Bulambuli', 'Busia', 'Butaleja', 'Buyende', 'Iganga',
        'Jinja', 'Kaberamaido', 'Kaliro', 'Kamuli', 'Kapchorwa', 'Katakwi',
        'Kibuku', 'Kumi', 'Kween', 'Luuka', 'Manafwa', 'Mayuge', 'Mbale',
        'Namayingo', 'Namisindwa', 'Namutumba', 'Ngora', 'Pallisa', 'Serere',
        'Sironko', 'Soroti', 'Tororo', 'Mbale City', 'Soroti City',
    ],
    'Northern': [
        'Abim', 'Adjumani', 'Agago', 'Alebtong', 'Amolatar', 'Amudat',
        'Amuru', 'Apac', 'Arua', 'Dokolo', 'Gulu', 'Kaabong', 'Kitgum',
        'Koboko', 'Kole', 'Kotido', 'Kwania', 'Lamwo', 'Lira', 'Madi-Okollo',
        'Maracha', 'Moroto', 'Moyo', 'Nakapiripirit', 'Napak', 'Nebbi',
        'Nwoya', 'Obongi', 'Omoro', 'Otuke', 'Oyam', 'Pader', 'Pakwach',
        'Terego', 'Yumbe', 'Zombo', 'Gulu City', 'Lira City', 'Arua City',
    ],
    'Western': [
        'Buhweju', 'Buliisa', 'Bundibugyo', 'Bushenyi', 'Hoima', 'Ibanda',
        'Isingiro', 'Kabale', 'Kabarole', 'Kagadi', 'Kakumiro', 'Kamwenge',
        'Kanungu', 'Kasese', 'Kibaale', 'Kibale', 'Kiruhura', 'Kiryandongo',
        'Kisoro', 'Kyegegwa', 'Kyenjojo', 'Masindi', 'Mitooma', 'Mbarara',
        'Ntoroko', 'Ntungamo', 'Rubanda', 'Rubirizi', 'Rukiga', 'Rukungiri',
        'Rwampara', 'Sheema', 'Fort Portal City', 'Mbarara City', 'Hoima City',
        'Kabale City',
    ],
}


class Command(BaseCommand):
    help = 'Load all Uganda districts into the database'

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0
        for region, districts in DISTRICTS.items():
            for name in districts:
                _, created = District.objects.get_or_create(
                    name=name,
                    defaults={'region': region, 'is_active': True}
                )
                if created:
                    created_count += 1
                else:
                    skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Districts loaded: {created_count} created, {skipped_count} already existed.'
            )
        )
