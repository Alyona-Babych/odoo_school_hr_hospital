from odoo import fields
from odoo.exceptions import AccessError

from ..constants.appointment_constant import appointment_status
from .common import TestCommon


class TestHrHospitalSecurity(TestCommon):

    def test_01_appointment_intern_access_rights(self):

        appointment_intern = self.appointment_intern.with_user(self.user_intern).read()
        self.assertEqual(len(appointment_intern), 1)

        self.appointment_intern.with_user(self.user_intern).write({
            'state': appointment_status.CANCELLED[0]
        })
        self.assertEqual(self.appointment_intern.state, appointment_status.CANCELLED[0])

        with self.assertRaises(AccessError):
            self.env['hr_hospital.appointment'].with_user(self.user_intern).create(
                {
                    'doctor_id': self.intern.id,
                    'mentor_id': self.doctor.id,
                    'patient_id': self.patient.id,
                    'scheduled_datetime': fields.Datetime().now()
                }
            )

        with self.assertRaises(AccessError):
            self.appointment_intern.with_user(self.user_intern).unlink()

    def test_02_appointment_intern_record_rules(self):

        intern_appointments = self.env['hr_hospital.appointment'].with_user(self.user_intern).search([('id', '=', self.appointment_intern.id)])
        self.assertIn(self.appointment_intern, intern_appointments)

        doctor_appointments = self.env['hr_hospital.appointment'].with_user(self.user_intern).search([
            ('id', '=', self.appointment_doctor.id)
        ])
        self.assertEqual(len(doctor_appointments), 0)

    def test_03_appointment_doctor_access_rights(self):

        appointment_doctor = self.appointment_doctor.with_user(self.user_doctor).read()
        self.assertEqual(len(appointment_doctor), 1)

        self.appointment_doctor.with_user(self.user_doctor).write({
            'state': appointment_status.CANCELLED[0]
        })
        self.assertEqual(self.appointment_doctor.state, appointment_status.CANCELLED[0])

        with self.assertRaises(AccessError):
            self.env['hr_hospital.appointment'].with_user(self.user_doctor).create(
                {
                    'doctor_id': self.intern.id,
                    'patient_id': self.patient.id,
                    'scheduled_datetime': fields.Datetime().today()
                }
            )

        with self.assertRaises(AccessError):
            self.appointment_doctor.with_user(self.user_doctor).unlink()

    def test_04_appointment_doctor_record_rules(self):

        doctor_appointments = self.env['hr_hospital.appointment'].with_user(self.user_doctor).search([('id', '=', self.appointment_doctor.id)])
        self.assertIn(self.appointment_doctor, doctor_appointments)

        intern_appointments = self.env['hr_hospital.appointment'].with_user(self.user_doctor).search([
            ('id', '=', self.appointment_intern.id)
        ])
        self.assertIn(self.appointment_intern, intern_appointments)

        other_doctor_appointment = self.env['hr_hospital.appointment'].with_user(self.user_doctor).search([(
            'id', 'not in', (self.appointment_doctor.id, self.appointment_intern.id)
        )])
        self.assertEqual(len(other_doctor_appointment), 0)

    def test_05_appointment_manager_access_rights(self):

        appointments = self.env['hr_hospital.appointment'].with_user(self.user_manager).search([])
        self.assertTrue(appointments)
        state_appointments = appointments.read(['state'])
        self.assertEqual(all('state' in state for state in state_appointments), True)

        self.appointment_intern.with_user(self.user_manager).write({
            'state': appointment_status.CANCELLED[0]
        })
        self.assertEqual(self.appointment_intern.state, appointment_status.CANCELLED[0])

        new_appointment = self.env['hr_hospital.appointment'].with_user(self.user_manager).create(
            {
                'doctor_id': self.intern.id,
                'mentor_id': self.doctor.id,
                'patient_id': self.patient.id,
                'scheduled_datetime': fields.Datetime().today()
            }
        )
        self.assertTrue(new_appointment)
        self.assertEqual(new_appointment.create_uid, self.user_manager)

        with self.assertRaises(AccessError):
            self.appointment_intern.with_user(self.user_manager).unlink()
