import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HrHospitalDoctorHistory(models.Model):
    """
    Patient doctor assignment history.

    This model tracks the history of doctor assignments for each patient.

    It stores:
    - which doctor was assigned to a patient;
    - when the assignment started;
    - when the doctor was changed;
    - validation rules for correct medical assignment flow.

    Used for:
    - maintaining full patient-doctor history;
    - audit and reporting;
    - ensuring correct chronological assignment of doctors.
    """

    _name = 'hr_hospital.doctor.history'
    _description = """Patient doctor assignment history tracking which records
    doctor changes for each patient over time, including assignment
    dates and active status validation."""

    _order = 'doctor_assignment_date'

    display_name = fields.Char(
        string='History',
        compute='_compute_display_name',
        store=False
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
    @api.depends_context('lang')
    def _compute_display_name(self):
        """
        Compute human-readable display name for history record.

        Format:
            <Patient> - <Doctor> (<Doctor Category>) <Assignment Date>

        :return: None
        """
        for history in self:
            patient = history.patient_id.name or ''
            doctor = history.doctor_id.name or ''
            category = history.doctor_id.category_id.name or ''
            date = fields.Date.to_string(history.doctor_assignment_date) if history.doctor_assignment_date else ''

            history.display_name = f"{patient} - {doctor} ({category}) {date}"

    @api.onchange('doctor_assignment_date', 'doctor_change_date')
    def _onchange_doctors_dates(self):
        """
        Validate doctor assignment dates in UI.

        Shows warning if change date is earlier than assignment date.

        :return: Warning dictionary or None
        :rtype: dict | None
        """
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
        """
        Prevent assignment of intern doctors as personal doctors.

        :raises ValidationError:
            If selected doctor is an intern.
        """
        for history in self:
            if history.doctor_id and history.doctor_id.is_intern:
                raise ValidationError('You cannot choose an intern as a personal doctor!')

    @api.constrains('doctor_assignment_date', 'doctor_change_date')
    def _check_doctor_dates(self):
        """
        Validate chronological consistency of doctor assignment dates.

        Ensures that change date is not earlier than assignment date.

        :raises ValidationError:
            If doctor_change_date < doctor_assignment_date.
        """
        for history in self:
            if history.doctor_assignment_date and history.doctor_change_date:
                if history.doctor_change_date < history.doctor_assignment_date:
                    raise ValidationError('Doctor change date cannot be earlier than the assignment date.')
