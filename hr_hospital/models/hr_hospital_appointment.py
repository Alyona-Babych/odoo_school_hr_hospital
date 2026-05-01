import logging

from odoo import api, models, fields
from odoo.exceptions import ValidationError

from ..constants.appointment_constant import appointment_status


_logger = logging.getLogger(__name__)


class HrHospitalAppointment(models.Model):
    _name = 'hr_hospital.appointment'
    _description = 'Patient appointments with doctors including scheduled medical visits'
    _order = 'scheduled_datetime desc'
    _rec_name = 'scheduled_datetime'

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
    )

    state = fields.Selection(
        list(appointment_status),
        default=appointment_status.PLANNED[0],
        required=True,
        string='Status'
    )

    disease_id = fields.Many2one(
        comodel_name='hr_hospital.disease',
        string='Disease',
        ondelete='restrict'
    )

    summary = fields.Html(string='Summary')

    active = fields.Boolean(default=True)

    @api.depends('doctor_id')
    def _compute_mentor(self):
        for doctor in self:
            if doctor.doctor_id.is_intern:
                doctor.mentor_id = doctor.doctor_id.mentor_id


    @api.onchange('actual_datetime')
    def _onchange_state(self):
        if self.actual_datetime:
            self.state = appointment_status.DONE[0]


    @api.onchange('state')
    def _onchange_state(self):
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
                    appointment.actual_datetime and
                    appointment.state != appointment_status.DONE[0]
            ):
                raise ValidationError('An appointment that has taken place must have the status "Done"')

            if (
                    appointment.state == appointment_status.DONE[0] and
                    not appointment.actual_datetime
            ):
                raise ValidationError('An appointment with the status "Done" must have an actual appointment date.')


    def write(self, vals):
        forbidden_fields = (
            'state',
            'scheduled_datetime',
            'actual_datetime',
            'doctor_id',
            'active'
        )
        for appointment in self:
            if (
                    appointment.state == appointment_status.DONE[0] and
                    any(field in vals for field in forbidden_fields)
            ):
                raise ValidationError('You cannot modify an appointment with the status "Done".')
        
        return super().write(vals)


    def unlink(self):
        for appointment in self:
            if appointment.state == appointment_status.DONE[0]:
                raise ValidationError('You cannot delete an appointment with the status "Done".')
            
        return super().unlink()
