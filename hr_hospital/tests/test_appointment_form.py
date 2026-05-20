from odoo import fields
from odoo.tests import Form

from ..constants.appointment_constant import appointment_status
from .common import TestCommon


class TestAppointmentForm(TestCommon):

    def test_01_check_mentor(self):
        test_form = Form(self.appointment_intern)
        mentor = test_form.mentor_id
        self.assertEqual(mentor.id, self.doctor.id)

    def test_02_check_default_state(self):
        test_form = Form(self.appointment_intern)
        state = test_form.state
        self.assertEqual(state, appointment_status.PLANNED[0])

    def test_03_onchange_actual_datetime(self):
        test_form = Form(self.appointment_intern)
        test_form.state = appointment_status.DONE[0]
        self.assertEqual(test_form.actual_datetime, fields.Datetime.now())
