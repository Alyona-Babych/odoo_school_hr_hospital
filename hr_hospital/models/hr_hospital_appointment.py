import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from ..constants.appointment_constant import appointment_status

_logger = logging.getLogger(__name__)


class HrHospitalAppointment(models.Model):
    """
    Medical appointment model.

    The model stores information about patient visits,
    assigned doctors, appointment states, diseases,
    summaries, and related analytical information.

    It also contains business rules for:
    - appointment state management;
    - appointment validation;
    - mentor assignment;
    - visit reporting;
    - protection of completed appointments.
    """

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
        """
        Compute display name for appointments.
        The display name is based on the patient name.
        """
        for appointment in self:
            appointment.display_name = f'{appointment.patient_id.name}'

    @api.depends('state')
    def _compute_color(self):
        """
        Compute color index depending on appointment status.
        Colors are used in calendar view.
        """
        for appointment in self:
            if appointment.state == appointment_status.DONE[0]:
                appointment.color = 10

            elif appointment.state == appointment_status.CANCELLED[0]:
                appointment.color = 1

            elif appointment.state == appointment_status.PLANNED[0]:
                appointment.color = 3

    @api.depends('doctor_id')
    def _compute_mentor(self):
        """Compute mentor for appointments assigned to intern doctors."""
        for appointment in self:
            if appointment.doctor_id.is_intern:
                appointment.mentor_id = appointment.doctor_id.mentor_id

    @api.depends('disease_ids')
    def _compute_diseases_appointment_count(self):
        """Compute number of appointments related to the same diseases."""
        for appointment in self:
            appointment.diseases_appointment_count = self.env[
                'hr_hospital.appointment'
            ].search_count([
                ('disease_ids', 'in', appointment.disease_ids.ids)
            ])

    @api.onchange('state')
    def _onchange_actual_datetime(self):
        """
        Automatically set actual appointment datetime.

        The current datetime is assigned automatically
        when appointment status becomes "Done".
        """
        if self.state and self.state == appointment_status.DONE[0]:
            self.actual_datetime = fields.Datetime.now()

    @api.constrains('scheduled_datetime', 'actual_datetime')
    def _check_appointment_dates(self):
        """
        Validate appointment dates consistency.

        :raises ValidationError:
            If actual appointment datetime
            is earlier than scheduled datetime.
        """
        for appointment in self:
            if appointment.scheduled_datetime and appointment.actual_datetime:
                if appointment.actual_datetime < appointment.scheduled_datetime:
                    raise ValidationError(self.env._('The actual date and time cannot be earlier than the scheduled date and time.'))

    @api.constrains('actual_datetime', 'state')
    def _check_state(self):
        """
        Validate completed appointment data.

        :raises ValidationError:
            If appointment state is "Done"
            but actual datetime is not specified.
        """
        for appointment in self:
            if (
                    appointment.state == appointment_status.DONE[0] and
                    not appointment.actual_datetime
            ):
                raise ValidationError(self.env._('An appointment with the status "Done" must have an actual appointment date.'))

    def _search(self, domain, offset=0, limit=None, order=None, **kwargs):
        """
        Extend default search behavior.
        Adds automatic filtering by current year
        when the corresponding search context is enabled.

        :param list domain: Search domain.
        :param int offset: Search offset.
        :param int limit: Maximum number of records.
        :param str order: Ordering expression.
        :param dict kwargs: Additional search arguments.

        :return: Search result identifiers.
        :rtype: list[int]
        """
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
        """
        Update appointment records.

        Prevents modification of protected fields
        for completed appointments.

        :param dict vals: Values to update.

        :return: Result of parent write operation.
        :rtype: bool

        :raises UserError:
            If user tries to modify protected fields
            of completed appointments.
        """
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
                raise UserError(self.env._('You cannot modify an appointment with the status "Done".'))
        return super().write(vals)

    def unlink(self):
        """
        Delete appointment records.

        :return: Result of parent unlink operation.
        :rtype: bool

        :raises UserError:
            If user tries to delete
            completed appointments.
        """
        for appointment in self:
            if appointment.state == appointment_status.DONE[0]:
                raise UserError(self.env._('You cannot delete an appointment with the status "Done".'))
        return super().unlink()

    def action_archive(self):
        """
        Prevent manual archiving of appointments.

        :raises UserError:
            Archiving is not allowed
            for appointment records.
        """
        raise UserError(self.env._('Archiving is not allowed for records in this table.'))

    def action_set_done_state(self):
        """
        Mark appointment as completed.

        Updates appointment status to "Done"
        and reloads the current view.

        :return: Client reload action.
        :rtype: dict

        :raises UserError:
            If actual appointment datetime
            is not specified.
        """
        self.ensure_one()
        for appointment in self:
            if not appointment.actual_datetime:
                raise UserError(self.env._('Please specify the current appointment date and time.'))

            appointment.write({
                'state': appointment_status.DONE[0],
                'actual_datetime': appointment.actual_datetime
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_set_cancelled_state(self):
        """
        Mark appointment as cancelled.

        :return: Client reload action.
        :rtype: dict

        :raises UserError:
            If user tries to cancel
            a completed appointment.
        """
        self.ensure_one()
        for appointment in self:
            if appointment.state == appointment_status.DONE[0]:
                raise UserError(self.env._('You cannot cancel an appointment with status "Done".'))

            appointment.write({
                'state': appointment_status.CANCELLED[0]
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_open_diseases_appointment_list(self):
        """
        Open appointments related to the same diseases.

        :return: Window action for appointments.
        :rtype: dict
        """
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
        """
        Get report color for appointment state.

        :return: Color name for report rendering.
        :rtype: str
        """
        self.ensure_one()

        colors = {
            appointment_status.DONE[0]: 'green',
            appointment_status.CANCELLED[0]: 'red',
            appointment_status.PLANNED[0]: 'orange',
        }

        return colors.get(self.state, 'black')
