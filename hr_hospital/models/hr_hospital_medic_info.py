import logging

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

from ..constants.person_constant import person_blood_group, person_gender, person_rh_factor

_logger = logging.getLogger(__name__)


class HrHospitalMedicInfo(models.AbstractModel):
    _name = 'hr_hospital.medic.info'
    _description = """Abstract model for storing basic medical information such
    as blood group, gender, date of birth, and computed age."""

    blood_group = fields.Selection(
        list(person_blood_group),
        string='Blood Group'
    )

    rh_factor = fields.Selection(
        list(person_rh_factor),
        string='Rh Factor'
    )

    gender = fields.Selection(
        list(person_gender),
        string='Gender',
        required=True,
        default=person_gender.OTHER[0]
    )

    birth_date = fields.Date(
        string='Birth Date',
        required=True
    )

    age = fields.Integer(
        compute='_compute_age',
        store=False,
        string='Age (full years)'
    )

    @api.depends('birth_date')
    def _compute_age(self):
        for medic_info in self:
            if medic_info.birth_date:
                today = fields.Date.today()
                medic_info.age = relativedelta(today, medic_info.birth_date).years
            else:
                medic_info.age = 0
