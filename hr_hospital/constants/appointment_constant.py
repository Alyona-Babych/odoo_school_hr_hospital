from collections import namedtuple

AppointmentStatus = namedtuple(
    'AppointmentStatus',
    (
        'PLANNED',
        'DONE',
        'CANCELLED',
    )
)

appointment_status = AppointmentStatus(
    ('planned', 'Planned'),
    ('done', 'Done'),
    ('cancelled', 'Cancelled'),
)
