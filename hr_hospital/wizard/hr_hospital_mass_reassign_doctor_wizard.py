import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class HrHospitalMassReassignDoctorWizard(models.TransientModel):
    """
    Wizard for mass reassignment of personal doctors.

    This wizard allows bulk reassignment of doctors for multiple patients.

    It performs:
    - closing previous doctor assignment history;
    - creating new doctor history records;
    - updating patient doctor assignment state implicitly via history;
    - bulk processing from list view (active_ids context).

    Used for hospital administrative workflows where multiple patients
    need to be reassigned to a different doctor at once.
    """

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
        """
        Reassign personal doctor for selected patients.

        Workflow:
        1. Retrieves selected patients from context (active_ids).
        2. Closes current doctor history by setting change date.
        3. Creates new doctor history records for selected patients.
        4. Displays success notification to user.

        return: Client action with success notification
        :rtype: dict
        """
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
