import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class HrHospitalPatient(models.Model):
    """
    Patient model.

    This model stores all patients registered in the hospital system.

    It provides:
    - personal medical information (via medic.info abstraction);
    - insurance data;
    - doctor assignment history tracking;
    - appointment management;
    - current treating doctor computation.

    The model acts as a central entity connecting doctors,
    appointments, and medical history.
    """
    _name = 'hr_hospital.patient'
    _description = 'Patients registered in the hospital system for medical care'
    _inherit = 'hr_hospital.medic.info'

    name = fields.Char(required=True)

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Patient User'
    )

    email = fields.Char()

    phone = fields.Char(required=True)

    policy_number = fields.Char(
        size=20,
        string='Insurance Policy ID'
    )

    personal_doctor_id = fields.Many2one(
        comodel_name='hr_hospital.doctor',
        compute='_compute_current_doctor_history',
        store=True,
        string='Personal Doctor Name'
    )

    personal_doctor_name = fields.Char(
        related='personal_doctor_id.name',
        string='Personal Doctor',
        readonly=True
    )

    doctor_history_ids = fields.One2many(
        comodel_name='hr_hospital.doctor.history',
        inverse_name='patient_id',
        string='Doctor History'
    )

    current_doctor_history_id = fields.Many2one(
        comodel_name='hr_hospital.doctor.history',
        string='Current Doctor History',
        compute='_compute_current_doctor_history',
        store=True
    )

    appointment_ids = fields.One2many(
        comodel_name='hr_hospital.appointment',
        inverse_name='patient_id',
        string='Appointments'
    )

    doctor_ids = fields.Many2many(
        comodel_name='hr_hospital.doctor',
        compute='_compute_doctors',
        string='Treating Doctors',
    )

    @api.depends(
        'doctor_history_ids.doctor_id',
        'doctor_history_ids.doctor_assignment_date',
        'doctor_history_ids.doctor_change_date',
        'doctor_history_ids.active'
    )
    def _compute_current_doctor_history(self):
        """
        Compute current doctor and active doctor history record.

        The method:
        - filters active doctor history records;
        - selects the latest assignment;
        - assigns current doctor and history record.

        :return: None
        """
        for patient in self:
            active_histories = patient.doctor_history_ids.filtered(lambda h: h.active
                                                                             and not h.doctor_change_date
            )

            last_history = max(
                active_histories,
                key=lambda h: h.doctor_assignment_date,
                default=False
            )

            patient.personal_doctor_id = last_history.doctor_id if last_history else False
            patient.current_doctor_history_id = last_history if last_history else False

    @api.depends('appointment_ids.doctor_id')
    def _compute_doctors(self):
        """
        Compute list of all doctors who treated the patient.

        Derived from patient appointment records.

        :return: None
        """
        for patient in self:
            patient.doctor_ids = patient.appointment_ids.mapped('doctor_id')

    def action_open_appointment_list(self):
        """
        Open list view of patient appointments.

        :return: Action dictionary for list view
        :rtype: dict
        """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Patient Appointments',
            'res_model': 'hr_hospital.appointment',
            'view_mode': 'list',
            'domain': [('patient_id', '=', self.id)],
        }

    def action_create_appointment(self):
        """
        Open appointment creation form for patient.

        Pre-fills:
        - patient reference;
        - current datetime as default scheduled time.

        :return: Action dictionary for form view
        :rtype: dict
        """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Appointment',
            'res_model': 'hr_hospital.appointment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_patient_id': self.id,
                'default_scheduled_datetime': fields.Datetime.now()
            }
        }
