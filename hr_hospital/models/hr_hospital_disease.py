import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class HrHospitalDisease(models.Model):
    _name = 'hr_hospital.disease'
    _description = 'Medical diseases and ICD-coded conditions used for patient diagnosis and visit tracking in the hospital system'
    _parent_name = 'parent_id'
    _parent_store = True
    _order = 'display_name'

    name = fields.Char(
        string='Name',
        required=True
    )

    icd_code = fields.Char(
        string='ICD code',
        required=True,
        index=True,
        help=(
            'Вкажіть код МКХ (ICD): це може бути код класу захворювань або код'
            'конкретного діагнозу відповідно до міжнародної класифікації.'
        )
    )

    display_name = fields.Char(
        string='Disease Name',
        compute='_compute_display_name',
        store=True
    )

    parent_id = fields.Many2one(
        comodel_name = 'hr_hospital.disease',
        string = 'ICD class',
        index = True,
        ondelete = 'cascade',
        help=(
            'Клас захворювання: при виборі конкретного захворювання необхідно'
            'вказати відповідний клас МКХ. У разі створення класу захворювання'
            'поле слід залишити порожнім.'
        )
    )

    parent_path = fields.Char(index=True)

    child_ids = fields.One2many(
        comodel_name='hr_hospital.disease',
        inverse_name='parent_id',
        string='Child Diseases'
    )

    _icd_code_unique = models.Constraint(
        'UNIQUE(icd_code)',
        'ICD-code must be unique.',
    )

    @api.depends('name', 'icd_code')
    def _compute_display_name(self):
        for disease in self:
            disease.display_name = f"[{disease.icd_code or ''}] {disease.name or ''}"


    @api.constrains('parent_id')
    def _check_parent_id(self):
        if self._has_cycle():
            raise ValidationError('You cannot create recursive categories.')
