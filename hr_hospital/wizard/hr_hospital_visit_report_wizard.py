import logging
from datetime import date

from odoo import Command, fields, models

from ..constants.appointment_constant import appointment_status


_logger = logging.getLogger(__name__)


class HrHospitalVisitReportWizard(models.TransientModel):
    _name = 'hr_hospital.visit.report.wizard'
    _description = 'Patient Visit Report Wizard allowing filtering by doctors, patients, date range, disease, and visit status'

    doctor_ids = fields.Many2many(
        comodel_name='hr_hospital.doctor',
        string='Doctor'
    )

    patient_ids = fields.Many2many(
        comodel_name='hr_hospital.patient',
        string = 'Patient'
    )

    start_date = fields.Date(string='Period Start')

    end_date = fields.Date(string='Period End')

    is_done_appointment = fields.Boolean(strind='Completed Visits Only')

    disease_id = fields.Many2one(
        comodel_name='hr_hospital.disease',
        string='Disease'
    )

    def default_get(self, fields):
        res = super().default_get(fields)

        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])

        if active_model == 'hr_hospital.patient':
            res['patient_ids'] =  [Command.set(active_ids)]

        if active_model == 'hr_hospital.doctor':
            res['doctor_ids'] =  [Command.set(active_ids)]

        return res


    def action_generate_report(self):
        domain = []

        if self.doctor_ids:
            domain.append(('doctor_id', 'in', self.doctor_ids.ids))

        if self.patient_ids:
            domain.append(('patient_id', 'in', self.patient_ids.ids))

        if self.disease_id:
            domain.append(('disease_id', '=', self.disease_id.id))

        start_date = self.start_date if self.start_date else date.min
        end_date = self.end_date if self.end_date else date.max

        if self.is_done_appointment:
            domain += [
                ('state', '=', appointment_status.DONE[0]),
                ('actual_datetime', '<=', end_date),
                ('actual_datetime', '>=', start_date)
            ]

        if not self.is_done_appointment:
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