"""
Management command to load sample ministries, agencies, departments, and 50 test employees.
Usage: python manage.py load_sample_data
"""
import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import (
    Ministry, Agency, GovernmentDepartment, CadreCategory,
    Position, Role, JobRank, EmployeeType, District
)
from employees.models import Employee

User = get_user_model()

MINISTRIES = [
    ('Ministry of ICT and National Guidance', 'MOICT', 'Responsible for ICT policy, e-Government, and national guidance.'),
    ('Ministry of Finance, Planning and Economic Development', 'MOFPED', 'Responsible for financial management and economic planning.'),
    ('Ministry of Health', 'MOH', 'Responsible for health policy, health services delivery and regulation.'),
    ('Ministry of Education and Sports', 'MOES', 'Responsible for education policy, curriculum, and sports development.'),
    ('Ministry of Public Service', 'MOPS', 'Responsible for human resource management in the public service.'),
    ('Ministry of Defence and Veteran Affairs', 'MODVA', 'Responsible for national defence and veteran affairs.'),
    ('Ministry of Justice and Constitutional Affairs', 'MOJCA', 'Responsible for legal affairs and constitutional matters.'),
    ('Ministry of Agriculture, Animal Industry and Fisheries', 'MAAIF', 'Responsible for agriculture, animal industry and fisheries policy.'),
]

AGENCIES = [
    ('National Information Technology Authority - Uganda', 'NITA-U', 'ICT regulatory and advisory body for government.'),
    ('Uganda Communications Commission', 'UCC', 'Regulator for the communications sector in Uganda.'),
    ('Uganda Revenue Authority', 'URA', 'Government agency that collects taxes and customs revenue.'),
    ('National Social Security Fund', 'NSSF', 'Provident fund for workers in the private sector.'),
    ('Uganda National Bureau of Statistics', 'UBOS', 'Government statistical agency.'),
    ('Uganda Registration Services Bureau', 'URSB', 'Responsible for registration of companies, businesses, and intellectual property.'),
]

DEPARTMENTS = [
    ('Directorate of ICT', 'DICT', 'Oversees ICT services within government.'),
    ('Directorate of Ethics and Integrity', 'DEI', 'Promotes ethics and integrity in public service.'),
    ('Directorate of Public Prosecutions', 'DPP', 'Prosecution of criminal cases on behalf of the state.'),
    ('National Planning Authority', 'NPA', 'Government think tank for national development planning.'),
    ('Public Procurement and Disposal of Public Assets Authority', 'PPDA', 'Oversees public procurement.'),
    ('Uganda Human Rights Commission', 'UHRC', 'Promotes and protects human rights in Uganda.'),
]

FIRST_NAMES_M = [
    'James', 'Robert', 'David', 'Samuel', 'Joseph', 'Moses', 'Peter', 'John',
    'Andrew', 'Michael', 'Emmanuel', 'Patrick', 'Richard', 'Francis', 'George',
    'Brian', 'Daniel', 'Henry', 'Stephen', 'Paul', 'Martin', 'Ronald', 'Ivan',
    'Timothy', 'Charles',
]
FIRST_NAMES_F = [
    'Sarah', 'Grace', 'Esther', 'Mercy', 'Florence', 'Agnes', 'Rebecca', 'Irene',
    'Dorothy', 'Rose', 'Patricia', 'Brenda', 'Catherine', 'Jane', 'Mary',
    'Lydia', 'Harriet', 'Gladys', 'Joan', 'Diana', 'Alice', 'Judith', 'Annet',
    'Ruth', 'Sylvia',
]
LAST_NAMES = [
    'Okello', 'Nambi', 'Kato', 'Mugisha', 'Namutebi', 'Ssempala', 'Ouma',
    'Achieng', 'Tumusiime', 'Nankya', 'Kyambadde', 'Muwanga', 'Atim',
    'Byaruhanga', 'Nabirye', 'Mukasa', 'Laker', 'Ochieng', 'Akello',
    'Birungi', 'Kamya', 'Kironde', 'Musoke', 'Kagwa', 'Nakitto',
    'Wasswa', 'Babirye', 'Lubwama', 'Ssebunya', 'Kibuuka', 'Nsubuga',
    'Wamala', 'Ddungu', 'Kaddu', 'Mubiru', 'Katende', 'Sserunjogi',
    'Nakimera', 'Wandera', 'Masaba',
]


class Command(BaseCommand):
    help = 'Load sample ministries, agencies, departments and 50 test employees'

    def handle(self, *args, **options):
        self.load_entities()
        self.load_employees()
        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))

    def load_entities(self):
        for name, code, desc in MINISTRIES:
            Ministry.objects.get_or_create(code=code, defaults={
                'name': name, 'description': desc, 'is_active': True,
            })
        self.stdout.write(f'  Loaded {len(MINISTRIES)} ministries')

        for name, code, desc in AGENCIES:
            Agency.objects.get_or_create(code=code, defaults={
                'name': name, 'description': desc, 'is_active': True,
            })
        self.stdout.write(f'  Loaded {len(AGENCIES)} agencies')

        for name, code, desc in DEPARTMENTS:
            GovernmentDepartment.objects.get_or_create(code=code, defaults={
                'name': name, 'description': desc, 'is_active': True,
            })
        self.stdout.write(f'  Loaded {len(DEPARTMENTS)} departments')

    def load_employees(self):
        categories = list(CadreCategory.objects.filter(is_active=True))
        positions = list(Position.objects.filter(is_active=True))
        job_ranks = list(JobRank.objects.filter(is_active=True))
        emp_types = list(EmployeeType.objects.filter(is_active=True))
        ministries = list(Ministry.objects.filter(is_active=True))
        agencies = list(Agency.objects.filter(is_active=True))
        departments = list(GovernmentDepartment.objects.filter(is_active=True))
        districts = list(District.objects.filter(is_active=True))

        if not categories or not positions or not job_ranks or not emp_types:
            self.stdout.write(self.style.WARNING(
                'Missing reference data. Run load_initial_data first.'
            ))
            return

        genders = ['M', 'F']
        titles_m = ['Mr', 'Dr', 'Prof']
        titles_f = ['Mrs', 'Ms', 'Dr', 'Prof']
        entity_types = ['ministry', 'agency', 'department', 'local_govt']
        marital_choices = ['single', 'married', 'divorced', 'widowed']
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

        created = 0
        target = 50
        emp_counter = Employee.objects.count()

        for i in range(target):
            gender = random.choice(genders)
            if gender == 'M':
                first_name = random.choice(FIRST_NAMES_M)
                title = random.choice(titles_m)
            else:
                first_name = random.choice(FIRST_NAMES_F)
                title = random.choice(titles_f)
            last_name = random.choice(LAST_NAMES)

            email = f"{first_name.lower()}.{last_name.lower()}{i+1}@moict.go.ug"
            username = f"{first_name.lower()}{last_name.lower()}{i+1}"

            if User.objects.filter(email=email).exists():
                continue

            user = User.objects.create_user(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                password='TestPass@2024',
                is_employee=True,
            )

            emp_counter += 1
            emp_number = f"ICT-{emp_counter:05d}"

            entity_type = random.choice(entity_types)
            ministry = None
            agency = None
            department = None
            district = None

            if entity_type == 'ministry' and ministries:
                ministry = random.choice(ministries)
            elif entity_type == 'agency' and agencies:
                agency = random.choice(agencies)
            elif entity_type == 'department' and departments:
                department = random.choice(departments)
            elif entity_type == 'local_govt' and districts:
                district = random.choice(districts)

            cadre = random.choice(categories)
            cadre_positions = [p for p in positions if p.cadre_category_id == cadre.id]
            position = random.choice(cadre_positions) if cadre_positions else random.choice(positions)

            dob = date(
                random.randint(1970, 2000),
                random.randint(1, 12),
                random.randint(1, 28)
            )
            joined_ministry = date(
                random.randint(2010, 2024),
                random.randint(1, 12),
                random.randint(1, 28)
            )
            joined_position = joined_ministry + timedelta(days=random.randint(0, 1000))
            if joined_position > date.today():
                joined_position = date.today() - timedelta(days=random.randint(30, 365))

            emp = Employee(
                user=user,
                employee_number=emp_number,
                title=title,
                date_of_birth=dob,
                gender=gender,
                nationality='Ugandan',
                national_id=f"CM{random.randint(10000000000, 99999999999)}",
                phone_primary=f"+256{random.randint(700000000, 799999999)}",
                marital_status=random.choice(marital_choices),
                blood_type=random.choice(blood_types),
                district_of_origin=random.choice(districts) if districts else None,
                district_of_residence=random.choice(districts) if districts else None,
                physical_address=f"Plot {random.randint(1,200)}, {random.choice(['Kampala Rd', 'Entebbe Rd', 'Jinja Rd', 'Bombo Rd', 'Luwum St'])}",
                next_of_kin_name=f"{random.choice(FIRST_NAMES_M + FIRST_NAMES_F)} {random.choice(LAST_NAMES)}",
                next_of_kin_phone=f"+256{random.randint(700000000, 799999999)}",
                next_of_kin_relationship=random.choice(['Spouse', 'Parent', 'Sibling', 'Child']),
                emergency_contact_name=f"{random.choice(FIRST_NAMES_M + FIRST_NAMES_F)} {random.choice(LAST_NAMES)}",
                emergency_contact_phone=f"+256{random.randint(700000000, 799999999)}",
                emergency_contact_relationship=random.choice(['Spouse', 'Parent', 'Friend']),
                employee_type=random.choice(emp_types),
                entity_type=entity_type,
                ministry=ministry,
                agency=agency,
                government_department=department,
                district=district,
                cadre_category=cadre,
                position=position,
                job_rank=random.choice(job_ranks),
                work_location=random.choice([
                    'Kampala', 'Entebbe', 'Jinja', 'Mbarara', 'Gulu',
                    'Fort Portal', 'Soroti', 'Lira', 'Masaka', 'Mbale'
                ]),
                date_joined_position=joined_position,
                date_joined_ministry=joined_ministry,
                is_active=True,
            )
            emp.save()
            created += 1

        self.stdout.write(f'  Created {created} sample employees')
