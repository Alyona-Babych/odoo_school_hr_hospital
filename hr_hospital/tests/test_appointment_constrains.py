from odoo import fields
from odoo.exceptions import ValidationError

from ..constants.appointment_constant import appointment_status
from .common import TestCommon


class TestAppointmentConstrains(TestCommon):

    def test_01_constrains_scheduled_datetime_actual_datetime(self):
        self.appointment_doctor.with_user(self.user_doctor).write({'scheduled_datetime': fields.Datetime().now()})
        with self.assertRaises(ValidationError):
            self.appointment_doctor.with_user(self.user_doctor).write({'actual_datetime': fields.Datetime().today()})

    def test_04_constrains_actual_datetime_state(self):
        with self.assertRaises(ValidationError):
            self.appointment_doctor.with_user(self.user_doctor).write({'state': appointment_status.DONE[0]})
