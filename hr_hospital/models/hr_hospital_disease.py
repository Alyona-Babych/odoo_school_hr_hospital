import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HrHospitalDiseaseCategory(models.Model):
    """
    Hierarchical ICD disease category model.

    This model is used to classify and group medical diseases
    into a hierarchical structure based on ICD classification.

    It supports:
    - tree structure of categories (parent/child relations)
    - linking diseases to categories
    - ICD code uniqueness validation
    - navigation actions for related diseases
    """

    _name = 'hr_hospital.disease.category'
    _description = 'Hierarchical ICD disease categories used for classification and grouping of medical conditions in the hospital system'
    _parent_name = 'parent_id'
    _parent_store = True
    _rec_name = 'display_name'

    name = fields.Char(
        string='Name',
        required=True,
        translate=True
    )

    icd_code = fields.Char(
        string='ICD code',
        required=True,
        index=True,
    )

    display_name = fields.Char(
        string='Category Disease Name',
        compute='_compute_display_name',
        store=False,
    )

    parent_id = fields.Many2one(
        comodel_name='hr_hospital.disease.category',
        string='ICD class',
        index=True,
        ondelete='cascade',
    )

    parent_path = fields.Char(index=True)

    child_ids = fields.One2many(
        comodel_name='hr_hospital.disease.category',
        inverse_name='parent_id',
        string='Child Diseases'
    )

    disease_ids = fields.One2many(
        comodel_name='hr_hospital.disease',
        inverse_name='category_id',
        string='Diseases'
    )

    _icd_code_unique = models.Constraint(
        'UNIQUE(icd_code)',
        'ICD-code must be unique.',
    )

    disease_count = fields.Integer(
        compute="_compute_disease_count"
    )

    def _compute_disease_count(self):
        """
        Compute number of diseases in the category.

        :return: None
        """
        for disease in self:
            disease.disease_count = self.env['hr_hospital.disease'].search_count([
                ('category_id', '=', disease.id)
            ])

    @api.depends('name', 'icd_code')
    @api.depends_context('lang')
    def _compute_display_name(self):
        """
        Compute category display name.

        Format: [ICD_CODE] Category Name

        :return: None
        """
        for disease in self:
            disease.display_name = f"[{disease.icd_code or ''}] {disease.name or ''}"

    @api.constrains('parent_id')
    def _check_parent_id(self):
        """
        Validate recursive hierarchy structure.

        Prevents cyclic references in category tree.

        :raises ValidationError:
            If recursive (cyclic) category structure is detected.
        """
        if self._has_cycle():
            raise ValidationError('You cannot create recursive categories.')

    def action_create_disease(self):
        """
        Open form view to create a new disease.

        Pre-fills category field with current category.

        :return: Action dictionary for opening form view.
        :rtype: dict
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Disease',
            'res_model': 'hr_hospital.disease',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_category_id': self.id
            }
        }

    def action_open_disease(self):
        """
        Open list view of diseases under this category.

        :return: Action dictionary for list view.
        :rtype: dict
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Diseases',
            'res_model': 'hr_hospital.disease',
            'view_mode': 'list',
            'domain': [('category_id', '=', self.id)],
        }


class HrHospitalDisease(models.Model):
    """
    Medical disease model.

    This model represents diseases and diagnoses used in the hospital system.

    It is linked to ICD categories and used in:
    - patient visits
    - diagnosis tracking
    - medical reporting
    """

    _name = 'hr_hospital.disease'
    _description = 'Medical diseases and diagnoses classified according to ICD categories and used in patient treatment and appointment records'
    _order = 'icd_code'

    name = fields.Char(
        required=True,
        translate=True
    )

    icd_code = fields.Char(
        required=True
    )

    display_name = fields.Char(
        string='Disease Name',
        compute='_compute_display_name',
        store=False,
    )

    category_id = fields.Many2one(
        comodel_name='hr_hospital.disease.category',
        string='ICD Category',
        required=True,
        ondelete='restrict'
    )

    _icd_code_unique = models.Constraint(
        'UNIQUE(icd_code)',
        'ICD-code must be unique.',
    )

    @api.depends('name', 'icd_code')
    @api.depends_context('lang')
    def _compute_display_name(self):
        """
        Compute disease display name.

        Format: [ICD_CODE] Disease Name

        :return: None
        """
        for disease in self:
            disease.display_name = f"[{disease.icd_code or ''}] {disease.name or ''}"

    def action_open_appointments_for_one_disease(self):
        """
        Open appointments related to this disease.

        :return: Action dictionary for appointment list view.
        :rtype: dict
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Disease Appointments',
            'res_model': 'hr_hospital.appointment',
            'view_mode': 'list,form',
            'domain': [
                ('disease_ids', 'in', self.ids)
            ],
        }
