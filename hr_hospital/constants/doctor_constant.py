from collections import namedtuple


DoctorSpecialization = namedtuple(
    'DoctorSpecialization',
    (
        'THERAPIST',
        'PEDIATRICIAN',
        'CARDIOLOGIST',
        'NEUROLOGIST',
        'ENDOCRINOLOGIST',
        'GASTROENTEROLOGIST',
    )
)

doctor_specialization = DoctorSpecialization(
    ('therapist', 'Therapist'),
    ('pediatrician', 'Pediatrician'),
    ('cardiologist', 'Cardiologist'),
    ('neurologist', 'Neurologist'),
    ('endocrinologist',  'Endocrinologist'),
    ('gastroenterologist', 'Gastroenterologist'),
)


DoctorQualificationCategory = namedtuple(
    'DoctorCategory',
    (
        'INTERN',
        'SPECIALIST',
        'FIRST',
        'SECOND',
        'HIGHEST'
    )
)

doctor_qualification_category = DoctorQualificationCategory(
    ('intern', 'Intern'),
    ('specialist', 'Specialist'),
    ('first', 'first Category'),
    ('second', 'Second Category'),
    ('highest', 'Highest Category')
)