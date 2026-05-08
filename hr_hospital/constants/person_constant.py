from collections import namedtuple

Gender = namedtuple(
    'Gender',
    (
        'FEMALE',
        'MALE',
        'OTHER',
     )
)

person_gender = Gender(
    ('female', 'Female'),
    ('male', 'Male'),
    ('other', 'Other'),
)


BloodGroup = namedtuple('BloodGroup', ('O', 'A', 'B', 'AB'))

person_blood_group = BloodGroup(
    ('o', 'O (I)'),
    ('a', 'A (II)'),
    ('b', 'B (III)'),
    ('ab', 'AB (IV)')
)

RhFactor = namedtuple(
    'RhFactor',
    (
        'POSITIVE',
        'NEGATIVE'
    )
)

person_rh_factor = RhFactor(
    ('positive', 'Rh+'),
    ('negative', 'Rh-')
)
