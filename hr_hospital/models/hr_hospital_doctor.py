import logging

from odoo import api, models, fields
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
        help='Користувацька назва категорії лікаря (визначається лікарнею)'
    )

    # Вычисляемое поле "Лікар є інтерном" (п.3.4) зависит от конкретного значения категории.
    # Во избежание ошибок, связанных с произвольным вводом или изменения xml-id в data файлах категории интерн
    # добавлено поле медицинской категории с фиксированным набором значений согласно украинской классификации.
    qualification_category = fields.Selection(
        list(doctor_qualification_category),
        required=True,
        string='Qualification Category',
        default=doctor_qualification_category.SPECIALIST[0],
        help="""Інтерн — лікар на етапі післядипломного навчання та практики.
        Лікар-спеціаліст — лікар із сертифікатом, що працює самостійно.
        Друга категорія — лікар із досвідом роботи від 3 років.
        Перша категорія — досвідчений лікар із стажем від 5–7 років.
        Вища категорія — лікар-експерт із великим досвідом від 10 років."""
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

    personal_patient_ids = fields.One2many(
        comodel_name='hr_hospital.patient',
        inverse_name='personal_doctor_id',
        string='Personal Patients'
    )

    @api.depends('category_id.qualification_category')
    def _compute_is_intern(self):
        for doctor in self:
            doctor.is_intern = (
                    doctor.category_id and
                    (doctor.category_id.qualification_category == doctor_qualification_category.INTERN[0])
            )


    @api.constrains('mentor_id')
    def _check_mentor(self):
        for doctor in self:
            if doctor.mentor_id and doctor.mentor_id.id == doctor.id:
                raise ValidationError('A doctor cannot be his own mentor!')

            if doctor.mentor_id and doctor.mentor_id.is_intern:
                raise ValidationError('An intern cannot be a mentor!')





