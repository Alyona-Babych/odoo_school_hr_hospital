from odoo import fields
from odoo.tests.common import TransactionCase

from ..constants.doctor_constant import doctor_qualification_category


class TestCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        doctor_categories = cls.env['hr_hospital.doctor.category'].create([
            {
                'name': 'test_intern',
                'qualification_category': doctor_qualification_category.INTERN[0]
            },
            {
                'name': 'test_specialist',
                'qualification_category': doctor_qualification_category.SPECIALIST[0]
            }
        ])
        cls.doctor_category_intern, cls.doctor_category_specialist = doctor_categories

        users = cls.env['res.users'].create([
            {
                'name': 'Patient',
                'login': 'patient',
                'password': '123456',
                'group_ids': [(4, cls.env.ref('base.group_user').id), (4, cls.env.ref('hr_hospital.group_patient').id)]
            },
            {
                'name': 'Doctor',
                'login': 'doctor',
                'password': '123456',
                'group_ids': [(4, cls.env.ref('base.group_user').id), (4, cls.env.ref('hr_hospital.group_doctor').id)]
            },
            {
                'name': 'Intern',
                'login': 'intern',
                'password': '123456',
                'group_ids': [(4, cls.env.ref('base.group_user').id), (4, cls.env.ref('hr_hospital.group_intern').id)]
            },
            {
                'name': 'Another Doctor',
                'login': 'another.doctor',
                'password': '123456',
                'group_ids': [(4, cls.env.ref('base.group_user').id), (4, cls.env.ref('hr_hospital.group_doctor').id)]
            },
            {
                'name': 'Another Intern',
                'login': 'another.intern',
                'password': '123456',
                'group_ids': [(4, cls.env.ref('base.group_user').id), (4, cls.env.ref('hr_hospital.group_intern').id)]
            },
            {
                'name': 'Manager',
                'login': 'manager',
                'password': '123456',
                'group_ids': [(4, cls.env.ref('base.group_user').id), (4, cls.env.ref('hr_hospital.group_manager').id)]
            },
        ])
        cls.user_patient, cls.user_doctor, cls.user_intern, cls.user_another_doctor, cls.user_another_intern, cls.user_manager = users

        doctors = cls.env['hr_hospital.doctor'].create([
            {
                'name': 'Doctor',
                'user_id': cls.user_doctor.id,
                'category_id': cls.doctor_category_specialist.id,
                'birth_date': fields.Date().today(),
                'phone': '555-555-555'
            },
            {
                'name': 'Intern',
                'user_id': cls.user_intern.id,
                'category_id': cls.doctor_category_intern.id,
                'birth_date': fields.Date().today(),
                'phone': '111-111-111'
            },
            {
                'name': 'Another Doctor',
                'user_id': cls.user_another_doctor.id,
                'category_id': cls.doctor_category_specialist.id,
                'birth_date': fields.Date().today(),
                'phone': '333-333-333'
            },
            {
                'name': 'Another Intern',
                'user_id': cls.user_another_intern.id,
                'category_id': cls.doctor_category_intern.id,
                'birth_date': fields.Date().today(),
                'phone': '444-444-444'
            }
        ])
        cls.doctor, cls.intern, cls.another_doctor, cls.another_intern = doctors
        cls.intern.write({'mentor_id': cls.doctor.id})
        cls.another_intern.write({'mentor_id': cls.another_doctor.id})

        cls.patient = cls.env['hr_hospital.patient'].create(
            {
                'name': 'Patient',
                'user_id': cls.user_patient.id,
                'birth_date': fields.Date().today(),
                'phone': '222-222-222'
            }
        )

        appointments = cls.env['hr_hospital.appointment'].create([
            {
                'doctor_id': cls.doctor.id,
                'patient_id': cls.patient.id,
                'scheduled_datetime': fields.Datetime().today()
            },
            {
                'doctor_id': cls.intern.id,
                'patient_id': cls.patient.id,
                'scheduled_datetime': fields.Datetime().today()
            },
            {
                'doctor_id': cls.another_doctor.id,
                'patient_id': cls.patient.id,
                'scheduled_datetime': fields.Datetime().today()
            },
            {
                'doctor_id': cls.another_intern.id,
                'patient_id': cls.patient.id,
                'scheduled_datetime': fields.Datetime().today()
            }
        ])
        cls.appointment_doctor, cls.appointment_intern = appointments[0], appointments[1]
