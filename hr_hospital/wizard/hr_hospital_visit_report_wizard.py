import logging
from datetime import date

from odoo import Command, fields, models

from ..constants.appointment_constant import appointment_status

_logger = logging.getLogger(__name__)


class HrHospitalVisitReportWizard(models.TransientModel):
    """
    Wizard for generating patient visit reports.

    This wizard allows filtering hospital visits based on:
    - doctors;
    - patients;
    - diseases;
    - visit date range;
    - visit completion status.

    It supports both:
    - completed visits reporting;
    - scheduled + completed mixed reporting.

    The wizard is used for analytical reporting and
    medical workflow monitoring in hospital system.
    """

    _name = 'hr_hospital.visit.report.wizard'
    _description = 'Patient Visit Report Wizard allowing filtering by doctors, patients, date range, disease, and visit status'

    doctor_ids = fields.Many2many(
        comodel_name='hr_hospital.doctor',
        string='Doctors'
    )

    patient_ids = fields.Many2many(
        comodel_name='hr_hospital.patient',
        string='Patients'
    )

    start_date = fields.Date(string='Period Start')

    end_date = fields.Date(string='Period End')

    is_done_appointment = fields.Boolean(string='Completed Visits Only')

    disease_ids = fields.Many2many(
        comodel_name='hr_hospital.disease',
        string='Diseases'
    )

    def default_get(self, fields):
        """
        Pre-fill wizard values based on context.

        If the wizard is opened from:
        - patient view → pre-fills patient_ids;
        - doctor view → pre-fills doctor_ids.

        :param list fields: requested fields
        :return: default values dictionary
        :rtype: dict
        """
        res = super().default_get(fields)

        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])

        if active_model == 'hr_hospital.patient':
            res['patient_ids'] = [Command.set(active_ids)]

        elif active_model == 'hr_hospital.doctor':
            res['doctor_ids'] = [Command.set(active_ids)]

        return res

    def action_generate_report(self):
        """
        Generate visit report based on selected filters.

        Filtering logic:
        - doctors (optional)
        - patients (optional)
        - diseases (optional)
        - date range filtering
        - completed or mixed visits mode

        Returns appointment records matching criteria.

        :return: action opening filtered appointment list view
        :rtype: dict
        """
        self.ensure_one()
        domain = []

        if self.doctor_ids:
            domain.append(('doctor_id', 'in', self.doctor_ids.ids))

        if self.patient_ids:
            domain.append(('patient_id', 'in', self.patient_ids.ids))

        if self.disease_ids:
            domain.append(('disease_ids', 'in', self.disease_ids.ids))

        start_date = self.start_date if self.start_date else date.min
        end_date = self.end_date if self.end_date else date.max

        if self.is_done_appointment:
            domain += [
                ('state', '=', appointment_status.DONE[0]),
                ('actual_datetime', '<=', end_date),
                ('actual_datetime', '>=', start_date)
            ]
        else:
            domain += [
                '|',
                '&',
                ('actual_datetime', '!=', False),
                '&',
                ('actual_datetime', '<=', end_date),
                ('actual_datetime', '>=', start_date),
                '&',
                ('actual_datetime', '=', False),
                '&',
                ('scheduled_datetime', '<=', end_date),
                ('scheduled_datetime', '>=', start_date),
            ]

        appointments = self.env['hr_hospital.appointment'].search(domain)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Visit Report',
            'res_model': 'hr_hospital.appointment',
            'view_mode': 'list,form',
            'domain': [('id', 'in', appointments.ids)],
        }
