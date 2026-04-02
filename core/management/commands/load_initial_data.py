from django.core.management.base import BaseCommand
from core.models import EmployeeType, CadreCategory, Position, Role, JobRank, SystemSettings


class Command(BaseCommand):
    help = 'Load initial reference data for the system'

    def handle(self, *args, **options):
        # Employee Types
        emp_types = ['Permanent', 'Contract', 'Casual', 'Secondment', 'Intern']
        for name in emp_types:
            EmployeeType.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS('Employee types loaded.'))

        # Cadre Categories
        cadres = [
            ('IT Officer', 'Information Technology Officers'),
            ('Communications Officer', 'Communications and PR Officers'),
            ('Software Engineer', 'Software Engineering Cadre'),
            ('Network Engineer', 'Network and Infrastructure Engineers'),
            ('Data Analyst', 'Data and Business Intelligence Analysts'),
            ('Cybersecurity Officer', 'Information Security Officers'),
            ('Database Administrator', 'Database Management Cadre'),
            ('Systems Administrator', 'Systems and Infrastructure Administrators'),
            ('ICT Support Officer', 'ICT Helpdesk and Support Staff'),
            ('Project Manager', 'ICT Project Management Cadre'),
            ('Policy Officer', 'ICT Policy and Regulation Officers'),
            ('Digital Transformation Officer', 'Digital Transformation Specialists'),
        ]
        for name, desc in cadres:
            cat, _ = CadreCategory.objects.get_or_create(name=name, defaults={'description': desc})

        self.stdout.write(self.style.SUCCESS('Cadre categories loaded.'))

        # Default system settings
        SystemSettings.get_settings()
        self.stdout.write(self.style.SUCCESS('System settings initialized.'))

        # Job Ranks
        ranks = [
            ('Principal IT Officer', 'PITO', 5),
            ('Senior IT Officer', 'SITO', 4),
            ('IT Officer I', 'ITO1', 3),
            ('IT Officer II', 'ITO2', 2),
            ('Assistant IT Officer', 'AITO', 1),
            ('Principal Communications Officer', 'PCO', 5),
            ('Senior Communications Officer', 'SCO', 4),
            ('Communications Officer I', 'CO1', 3),
            ('Communications Officer II', 'CO2', 2),
        ]
        for name, code, level in ranks:
            JobRank.objects.get_or_create(name=name, code=code, defaults={'level': level, 'entity_type': 'all'})

        self.stdout.write(self.style.SUCCESS('Job ranks loaded.'))
        self.stdout.write(self.style.SUCCESS('All initial data loaded successfully!'))
