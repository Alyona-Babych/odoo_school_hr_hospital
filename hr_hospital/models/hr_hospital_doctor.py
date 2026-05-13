import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

from ..constants.doctor_constant import doctor_qualification_category, doctor_specialization

_logger = logging.getLogger(__name__)


class HrHospitalDoctorCategory(models.Model):
    _name = 'hr_hospital.doctor.category'
    _description = 'Doctor qualification categories used to classify doctors and manage their ordering and assignments.'
    _order = 'sequence'

    name = fields.Char(
        required=True,
        string='Category',
        help='Custom doctor category name (defined by hospital)'
    )

    qualification_category = fields.Selection(
        list(doctor_qualification_category),
        required=True,
        string='Qualification Category',
        default=doctor_qualification_category.SPECIALIST[0],
        help="""Intern - a doctor at the stage of postgraduate training and practice.
                Specialist doctor - a doctor with a certificate who works independently.
                The second category - a doctor with work experience of 3 years or more.
                The first category - an experienced doctor with experience of 5-7 years.
                The highest category - an expert doctor with extensive experience of 10 years or more."""
    )

    sequence = fields.Integer(default=10)

    doctor_ids = fields.One2many(
        comodel_name='hr_hospital.doctor',
        inverse_name='category_id',
        string='Doctors'
    )

    doctor_amount = fields.Integer(
        string='Doctors Amount',
        compute='_compute_doctor_amount',
        store=True
    )

    _name_unique = models.Constraint(
        'UNIQUE(name)',
        'Category must be unique.',
    )

    @api.depends('doctor_ids')
    def _compute_doctor_amount(self):
        for record in self:
            record.doctor_amount = len(record.doctor_ids)


class HrHospitalDoctor(models.Model):
    _name = 'hr_hospital.doctor'
    _description = 'Hospital doctors responsible for patient diagnosis and treatment'
    _inherit = 'hr_hospital.medic.info'
    _order = 'name'

    name = fields.Char(required=True)

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User'
    )

    email = fields.Char()

    phone = fields.Char(required=True)

    category_id = fields.Many2one(
        comodel_name='hr_hospital.doctor.category',
        string='Category',
        required=True
    )

    is_intern = fields.Boolean(
        compute='_compute_is_intern',
        store=True
    )

    intern_names = fields.Char(
        compute='_compute_intern_names'
    )

    intern_ids = fields.One2many(
        comodel_name='hr_hospital.doctor',
        inverse_name='mentor_id',
        string='Interns'
    )

    specialization = fields.Selection(
        list(doctor_specialization),
        string='Specialization',
    )

    mentor_id = fields.Many2one(
        comodel_name='hr_hospital.doctor',
        string='Mentor'
    )

    mentor_name = fields.Char(
        related='mentor_id.name',
        string='Mentor name'
    )

    mentor_specialization = fields.Selection(
        related='mentor_id.specialization',
        string='Specialization',
    )

    mentor_category = fields.Char(
        related='mentor_id.category_id.name',
        string='Category'
    )

    personal_patient_ids = fields.One2many(
        comodel_name='hr_hospital.patient',
        inverse_name='personal_doctor_id',
        string='Personal Patients'
    )

    appointment_ids = fields.One2many(
        comodel_name='hr_hospital.appointment',
        inverse_name='doctor_id',
        string='Appointments'
    )

    color = fields.Integer(default=0)

    active = fields.Boolean(default=True)

    @api.depends('category_id.qualification_category')
    def _compute_is_intern(self):
        for doctor in self:
            doctor.is_intern = (
                    doctor.category_id and
                    (doctor.category_id.qualification_category == doctor_qualification_category.INTERN[0])
            )

    @api.depends('intern_ids')
    def _compute_intern_names(self):
        for doctor in self:
            doctor.intern_names = ', '.join(doctor.intern_ids.mapped('name')) if doctor.intern_ids else ''

    @api.constrains('mentor_id')
    def _check_mentor(self):
        for doctor in self:
            if doctor.mentor_id:
                if doctor.mentor_id.id == doctor.id:
                    raise ValidationError('A doctor cannot be his own mentor!')

                if doctor.mentor_id.is_intern:
                    raise ValidationError('An intern cannot be a mentor!')

    def action_create_appointment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Appointment',
            'res_model': 'hr_hospital.appointment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_doctor_id': self.id,
                'default_scheduled_datetime': fields.Datetime.now()
            }
        }

    def _get_report_base_filename(self):
        if len(self) > 1:
            return f'Appointments - Doctor {self.name}'

        return f'Appointments - Doctors({len(self)})'

    def _get_appointments(self):
        self.ensure_one()

        return self.appointment_ids.sorted(key=lambda app: app.scheduled_datetime, reverse=True)

    def _get_patients(self):
        self.ensure_one()

        return self.appointment_ids.mapped('patient_id').sorted(key=lambda p: p.name)
