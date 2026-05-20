import logging
from datetime import date

from odoo import fields, models

from ..constants.appointment_constant import appointment_status

_logger = logging.getLogger(__name__)


class HrHospitalDiseaseReportWizard(models.TransientModel):
    """
    Wizard for generating disease-based visit reports.

    This wizard allows filtering completed patient appointments
    by doctors, diseases, and time period.

    It is used to:
    - generate analytical reports for diseases;
    - filter visits;
    - group results by disease;
    - support hospital reporting workflows.

    The wizard does not store persistent data and is used
    only for temporary report generation.
    """
    _name = 'hr_hospital.disease.report.wizard'
    _description = 'Wizard for Generating Disease Visit Reports'

    doctor_ids = fields.Many2many(
        comodel_name='hr_hospital.doctor',
        string='Doctors'
    )

    disease_ids = fields.Many2many(
        comodel_name='hr_hospital.disease',
        string='Diseases'
    )

    start_date = fields.Date(string='Period Start')

    end_date = fields.Date(string='Period End')

    def action_generate_report(self):
        """
        Generate disease visit report based on filters.

        Filters include:
        - selected doctors;
        - selected diseases;
        - date range;
        - only completed appointments.

        The result is a list of filtered appointments grouped by disease.

        :return: Action dictionary opening appointment list view
        :rtype: dict
        """
        self.ensure_one()
        domain = [('state', '=', appointment_status.DONE[0])]

        if self.doctor_ids:
            domain += [('doctor_id', 'in', self.doctor_ids.ids)]

        if self.disease_ids:
            domain += [('disease_ids', 'in', self.disease_ids.ids)]
        else:
            domain += [('disease_ids', '!=', False)]

        start_date = self.start_date if self.start_date else date.min
        end_date = self.end_date if self.end_date else date.max

        domain += [
            ('actual_datetime', '<=', end_date),
            ('actual_datetime', '>=', start_date)
        ]

        appointments = self.env['hr_hospital.appointment'].search(domain)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Diseases Report',
            'res_model': 'hr_hospital.appointment',
            'view_mode': 'list,form',
            'domain': [('id', 'in', appointments.ids)],
            'context': {'group_by': 'disease_ids'}
        }
