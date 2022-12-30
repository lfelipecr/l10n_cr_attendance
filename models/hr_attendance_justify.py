# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from pytz import timezone

STATES = [('new', 'Nuevo'),
          ('validate', 'Validado'),
          ('validate_not', 'No Validado'),
          ]

class HrAttendanceJustify(models.Model):
    _name = 'hr.attendance.justify'
    _inherit = 'mail.thread'
    _description = 'Asistencias: Justifacion para empleados'
    _rec_name = 'name'
    _order = "id desc"

    def _default_employee(self):
        return self.env.user.employee_id

    def _default_name(self):
        name = self.env['ir.sequence'].next_by_code('hr.attendance.justify.sequence')
        return name

    name = fields.Char(store=True, copy=False, default=_default_name)
    description = fields.Text(string='Descripción', required=True)
    date = fields.Date('Fecha', default=fields.Date.context_today)
    state = fields.Selection(STATES, string='Estado', readonly=True, default='new')
    employee_id = fields.Many2one('hr.employee',string='Empleado', store=True, readonly=True,default=_default_employee,ondelete='cascade',)
    mail_from = fields.Char('Email Salida')
    name_show = fields.Char('Nombre estado')



    def send(self):
        #zone = timezone(self.employee_id.tz)  # ZONA DEL EMPLEADO
        #hoy_cr = datetime.strptime(datetime.now().astimezone(zone).strftime('%Y-%m-%d'), '%Y-%m-%d')

        name_employee = self.employee_id.name

        attendance = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id),('date_now','=',self.date)],limit=1)

        template = self.env.ref('l10n_cr_attendance.email_template_hr_attendance_justify', raise_if_not_found=False)
        if attendance:
            query = """ select id,smtp_user from ir_mail_server order by id desc limit 1 """
            self.env.cr.execute(query)
            data = self.env.cr.dictfetchone()

            if len(data) > 0:
                self.mail_from = data['smtp_user']
                if template and data['smtp_user']:
                    template.send_mail(self.id, force_send=True, notif_layout='mail.mail_notification_light')

                attendance.jutify_id = self
                attendance.justify_state = self.state
                #MENSAJE DE RETORNO EXITOSO
                mensaje = str(name_employee) + ', la socilitud de su justificación ha sido enviada para su posterior validación. Se le envió un mensaje a su correo.'
                self.env.user.notify_success(message=mensaje, title="BIEN! ")
            else:
                raise UserError(_("No se ha configurado un servidor de envío de correo"))

        else:
            raise UserError(_("No tiene tardanzas que justificar el día de hoy"))

    #
    # @api.onchange("state")
    # def _onchange_state(self):
    #     for rec in self:
    #         if rec.state == 'validate':
    #             rec.name_show = 'Validado'
    #         else:
    #             rec.name_show = 'No Validado'
    #
    #         if rec.state!='new':
    #             email_from = rec.mail_from
    #             template = self.env.ref('l10n_cr_attendance.email_template_hr_attendance_justify', raise_if_not_found=False)
    #
    #             if template and email_from:
    #                 template.send_mail(self.id, force_send=True, notif_layout='mail.mail_notification_light')
    #
    #             # MENSAJE DE RETORNO EXITOSO
    #             self.env.user.notify_success(
    #                 message='Se ha validado es estado de la justificación número: ' + str(rec.name), title="BIEN! ")

