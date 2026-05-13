import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HrHospitalDoctorHistory(models.Model):
    _name = 'hr_hospital.doctor.history'
    _description = """Patient doctor assignment history tracking which records
    doctor changes for each patient over time, including assignment
    dates and active status validation."""

    _order = 'display_name'

    display_name = fields.Char(
        string='History',
        compute='_compute_display_name',
        store=True
    )

    patient_id = fields.Many2one(
        comodel_name='hr_hospital.patient',
        string='Patient',
        required=True,
        ondelete='restrict'
    )

    doctor_id = fields.Many2one(
        comodel_name='hr_hospital.doctor',
        string='Doctor',
        domain=[('is_intern', '=', False)],
        required=True,
        ondelete='restrict'
    )

    doctor_assignment_date = fields.Date(
        string='Doctor Assignment Date',
        required=True,
        default=fields.Date.today
    )

    doctor_change_date = fields.Date(string='Doctor Change Date')

    active = fields.Boolean(default=True)

    @api.depends('patient_id', 'doctor_id', 'doctor_id.category_id', 'doctor_assignment_date')
    def _compute_display_name(self):
        for history in self:
            patient = history.patient_id.name or ''
            doctor = history.doctor_id.name or ''
            category = history.doctor_id.category_id.name or ''
            date = fields.Date.to_string(history.doctor_assignment_date) if history.doctor_assignment_date else ''

            history.display_name = f"{patient} - {doctor} ({category}) {date}"

    @api.onchange('doctor_assignment_date', 'doctor_change_date')
    def _onchange_doctors_dates(self):
        if self.doctor_assignment_date and self.doctor_change_date:
            if self.doctor_change_date < self.doctor_assignment_date:
                return {
                    'warning': {
                        'title': 'Attention',
                        'message': 'Doctor change date cannot be earlier than the assignment date.',
                        'type': 'notification'
                    }
                }
        return None

    @api.constrains('doctor_id')
    def _check_is_doctor_intern(self):
        for history in self:
            if history.doctor_id and history.doctor_id.is_intern:
                raise ValidationError('You cannot choose an intern as a personal doctor!')

    @api.constrains('doctor_assignment_date', 'doctor_change_date')
    def _check_doctor_dates(self):
        for history in self:
            if history.doctor_assignment_date and history.doctor_change_date:
                if history.doctor_change_date < history.doctor_assignment_date:
                    raise ValidationError('Doctor change date cannot be earlier than the assignment date.')
