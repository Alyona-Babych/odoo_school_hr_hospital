from odoo import fields
from odoo.exceptions import UserError

from ..constants.appointment_constant import appointment_status
from .common import TestCommon


class TestAppointmentActions(TestCommon):

    def test_01_action_set_done_state(self):

        with self.assertRaises(UserError):
            self.appointment_doctor.with_user(self.user_doctor).action_set_done_state()

        self.appointment_doctor.with_user(self.user_doctor).write(
            {'actual_datetime': fields.Datetime().now()}
        )
        self.appointment_doctor.with_user(self.user_doctor).action_set_done_state()
        self.assertEqual(self.appointment_doctor.state, appointment_status.DONE[0])

    def test_02_action_set_cancelled_state(self):
        self.appointment_doctor.with_user(self.user_doctor).write(
            {
                'actual_datetime': fields.Datetime().now(),
                'state': appointment_status.DONE[0]
            }
        )
        with self.assertRaises(UserError):
            self.appointment_doctor.with_user(self.user_doctor).action_set_cancelled_state()

        self.appointment_intern.with_user(self.user_intern).action_set_cancelled_state()
        self.assertEqual(self.appointment_intern.state, appointment_status.CANCELLED[0])
