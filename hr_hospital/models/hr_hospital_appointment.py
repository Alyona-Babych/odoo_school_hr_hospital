import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from ..constants.appointment_constant import appointment_status

_logger = logging.getLogger(__name__)


class HrHospitalAppointment(models.Model):
    _name = 'hr_hospital.appointment'
    _description = 'Patient appointments with doctors including scheduled medical visits'
    _order = 'scheduled_datetime desc'

    display_name = fields.Char(
        compute='_compute_display_name',
        store=True
    )

    doctor_id = fields.Many2one(
        comodel_name='hr_hospital.doctor',
        string='Doctor',
        required=True,
        ondelete='restrict'
    )

    mentor_id = fields.Many2one(
        comodel_name='hr_hospital.doctor',
        compute='_compute_mentor',
        store=True,
        string='Mentor',
    )

    patient_id = fields.Many2one(
        comodel_name='hr_hospital.patient',
        string='Patient',
        required=True,
        ondelete='restrict'
    )

    scheduled_datetime = fields.Datetime(
        string='Scheduled Date & Time',
        required=True
    )

    actual_datetime = fields.Datetime(
        string='Actual Date & Time',
        copy=False
    )

    state = fields.Selection(
        list(appointment_status),
        default=appointment_status.PLANNED[0],
        required=True,
        string='Status'
    )

    disease_ids = fields.Many2many(
        comodel_name='hr_hospital.disease',
        string='Disease',
        ondelete='restrict',
        copy=False
    )

    summary = fields.Html(string='Summary')

    active = fields.Boolean(default=True)

    color = fields.Integer(compute='_compute_color')

    diseases_appointment_count = fields.Integer(
        compute="_compute_diseases_appointment_count"
    )

    @api.depends('patient_id.name')
    def _compute_display_name(self):
        for appointment in self:
            appointment.display_name = f'{appointment.patient_id.name}'

    @api.depends('state')
    def _compute_color(self):
        for appointment in self:
            if appointment.state == appointment_status.DONE[0]:
                appointment.color = 10

            elif appointment.state == appointment_status.CANCELLED[0]:
                appointment.color = 1

            elif appointment.state == appointment_status.PLANNED[0]:
                appointment.color = 3

    @api.depends('doctor_id')
    def _compute_mentor(self):
        for appointment in self:
            if appointment.doctor_id.is_intern:
                appointment.mentor_id = appointment.doctor_id.mentor_id

    @api.depends('disease_ids')
    def _compute_diseases_appointment_count(self):
        for appointment in self:
            appointment.diseases_appointment_count = self.env[
                'hr_hospital.appointment'
            ].search_count([
                ('disease_ids', 'in', appointment.disease_ids.ids)
            ])

    @api.onchange('state')
    def _onchange_actual_datetime(self):
        if self.state and self.state == appointment_status.DONE[0]:
            self.actual_datetime = fields.Datetime.today()

    @api.constrains('scheduled_datetime', 'actual_datetime')
    def _check_appointment_dates(self):
        for appointment in self:
            if appointment.scheduled_datetime and appointment.actual_datetime:
                if appointment.actual_datetime < appointment.scheduled_datetime:
                    raise ValidationError('The actual date and time cannot be earlier than the scheduled date and time.')

    @api.constrains('actual_datetime', 'state')
    def _check_state(self):
        for appointment in self:
            if (
                    appointment.state == appointment_status.DONE[0] and
                    not appointment.actual_datetime
            ):
                raise ValidationError('An appointment with the status "Done" must have an actual appointment date.')

    def _search(self, domain, offset=0, limit=None, order=None, **kwargs):

        if self.env.context.get('search_default_current_year'):
            today = fields.Datetime.now()
            first_day_year = today.replace(month=1, day=1, hour=0, minute=0, second=0)
            last_day_year = today.replace(month=12, day=31, hour=23, minute=59, second=0)

            domain = [
                ('scheduled_datetime', '>=', first_day_year),
                ('scheduled_datetime', '<=', last_day_year),
            ] + domain

        return super()._search(domain, offset=offset, limit=limit, order=order)

    def write(self, vals):
        forbidden_fields = (
            'state',
            'scheduled_datetime',
            'actual_datetime',
            'doctor_id',
        )
        for appointment in self:
            if (
                    appointment.state == appointment_status.DONE[0] and
                    any(field in vals for field in forbidden_fields)
            ):
                raise UserError('You cannot modify an appointment with the status "Done".')
        return super().write(vals)

    def unlink(self):
        for appointment in self:
            if appointment.state == appointment_status.DONE[0]:
                raise UserError('You cannot delete an appointment with the status "Done".')
        return super().unlink()

    def action_archive(self):
        raise UserError('Archiving is not allowed for records in this table.')

    def action_set_done_state(self):
        self.ensure_one()
        for appointment in self:
            if not appointment.actual_datetime:
                raise UserError('Please specify the current appointment date and time.')

            appointment.write({
                'state': appointment_status.DONE[0],
                'actual_datetime': appointment.actual_datetime
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_set_cancelled_state(self):
        self.ensure_one()
        for appointment in self:
            if appointment.state == appointment_status.DONE[0]:
                raise UserError('You cannot cancel an appointment with status "Done".')

            appointment.write({
                'state': appointment_status.CANCELLED[0]
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_open_diseases_appointment_list(self):
        self.ensure_one()
        domain = [('disease_ids', 'in', self.disease_ids.ids)] if self.disease_ids else [('id', '=', False)]
        return {
            'type': 'ir.actions.act_window',
            'name': 'Disease Appointments',
            'res_model': 'hr_hospital.appointment',
            'view_mode': 'list,form',
            'domain': domain,
        }

    def _get_state_color(self):
        self.ensure_one()

        colors = {
            appointment_status.DONE[0]: 'green',
            appointment_status.CANCELLED[0]: 'red',
            appointment_status.PLANNED[0]: 'orange',
        }

        return colors.get(self.state, 'black')
