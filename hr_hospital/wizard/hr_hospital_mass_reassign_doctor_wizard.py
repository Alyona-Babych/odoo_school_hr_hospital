import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class HrHospitalMassReassignDoctorWizard(models.TransientModel):
    _name = 'hr_hospital.mass.reassign.doctor.wizard'
    _description = 'Wizard for mass reassignment of personal doctors to patients'

    doctor_id = fields.Many2one(
        comodel_name='hr_hospital.doctor',
        domain=[('is_intern', '=', False)],
        required=True,
        string='Assigned Doctor'
    )

    reassignment_date = fields.Date(
        string='Reassignment Date',
        required=True,
        default=fields.Date.today
    )

    def action_reassign_doctor(self):
        active_ids = self.env.context.get('active_ids')
        patients = self.env['hr_hospital.patient'].browse(active_ids)

        patient_history = patients.mapped('current_doctor_history_id')

        if patient_history:
            patient_history.write({
                'doctor_change_date': self.reassignment_date
            })

        self.env['hr_hospital.doctor.history'].create([
            {
                'patient_id': patient.id,
                'doctor_id': self.doctor_id.id,
                'doctor_assignment_date': self.reassignment_date,
            }
            for patient in patients
        ])

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Doctor successfully reassigned to selected patients!\n\n'
                           'You can close the window.',
                'type': 'success',
                'sticky': False,
            },
        }
