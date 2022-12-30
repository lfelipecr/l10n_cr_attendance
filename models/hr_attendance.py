# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
import requests
from datetime import date, datetime, time, timedelta
from pytz import timezone
import threading
import math
from odoo.exceptions import UserError

segudos_x_minuto = 3600.0

STATES = [('new', 'Nuevo'),
          ('validate', 'Validado'),
          ('validate_not', 'No Validado'),
          ]


ip = False
class HrAttendance(models.Model):
    _name = 'hr.attendance'
    _inherit = ['mail.thread','hr.attendance']

    dir_ip = fields.Char('Dirección IP', copy=False, store=True)
    tardanza = fields.Float('Tardanza')
    delta = fields.Char('Delta')
    mail_from = fields.Char('Email Salida')
    jutify_id = fields.Many2one('hr.attendance.justify', string='Justificación')
    justify_state = fields.Selection(STATES, string='Estado de la justificación', related='jutify_id.state', readonly=False)
    date_now = fields.Date('Fecha')

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        r = super(HrAttendance, self)._check_validity()
        for attendance in self:
            if attendance.check_in and attendance.check_out==False:
                attendance.get_tardanza(attendance)
        return r

    def get_tardanza(self, attendance):
        zone = timezone(attendance.employee_id.tz) #ZONA DEL EMPLEADO
        fecha_inicio = False
        hoy = datetime.now()
        hoy_cr = datetime.strptime(hoy.astimezone(zone).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

        horario = attendance.employee_id.resource_calendar_id

        for i in horario.attendance_ids:
            if hoy_cr.weekday() == int(i.dayofweek):
                hora_min = float(str(hoy_cr.hour)+'.'+str(hoy_cr.minute))
                if i.hour_from <= hora_min and hora_min <= i.hour_to:
                    h_m = str(i.hour_from).split('.')
                    resource_h = h_m[0]
                    resource_m = h_m[1]
                    fecha_inicio = datetime(hoy_cr.year,hoy_cr.month,hoy_cr.day,int(resource_h),int(resource_m),0)
                    break

        attendance.date_now = hoy_cr.date()
        if fecha_inicio:
            delta = hoy_cr - fecha_inicio
            ht = delta.total_seconds() / segudos_x_minuto
            attendance.delta = str(delta)
            attendance.tardanza = ht

            query = """ select key,value from ir_config_parameter where key='time_max_check_in' order by id desc limit 1 """
            self.env.cr.execute(query)
            data = self.env.cr.dictfetchone()

            if len(data)>0:

                #time_max = self.env['ir.config_parameter'].get_param('time_max_check_in')
                minuts = 60 * float(data['value']) #TIEMPO EN MINUTOS
                seconds= minuts*60
                if delta.seconds > seconds:
                    attendance.send_mail_delay(attendance)
                    attendance.send_mail_employee(attendance)
            else:
                raise UserError(_("No tiene configurado un tiempo máximo para entrada del trabajador"))

        return 1

    #
    @api.model
    def get_dir_ip(self,attendance, ip):
        if attendance[0]['dir_ip']==False:
            att = self.env['hr.attendance'].browse(attendance[0]['id'])
            att.write({'dir_ip': ip[0]})

    def send_mail_delay(self, attendance):

        query = """ select id,smtp_user from ir_mail_server order by id desc limit 1 """
        self.env.cr.execute(query)
        data = self.env.cr.dictfetchone()

        if len(data)>0:
            template = self.env.ref('l10n_cr_attendance.email_template_hr_attendance', raise_if_not_found=False)
            email_from = data['smtp_user']
            attendance.mail_from = email_from
            if template and email_from:
                template.send_mail(self.id, force_send=True, notif_layout='mail.mail_notification_light')
        else:
            raise UserError(_("No se ha configurado un servidor de envío de correo"))


    def send_mail_employee(self, attendance):
        query = """ select id,smtp_user from ir_mail_server order by id desc limit 1 """
        self.env.cr.execute(query)
        data = self.env.cr.dictfetchone()

        if len(data) > 0:
            template = self.env.ref('l10n_cr_attendance.email_template_hr_attendance_employee', raise_if_not_found=False)
            email_from = data['smtp_user']
            attendance.mail_from = email_from
            if template and email_from:
                template.send_mail(self.id, force_send=True, notif_layout='mail.mail_notification_light')
        else:
            raise UserError(_("No se ha configurado un servidor de envío de correo"))

    @api.onchange("justify_state")
    def _onchange_justify_state(self):
        for rec in self:
            if rec.employee_id.coach_id.id == rec.env.user.employee_id.id:
                if rec.justify_state=='validate':
                    rec.jutify_id.name_show = 'Validado'
                else:
                    rec.jutify_id.name_show = 'No Validado'

                if rec.justify_state!='new':
                    rec.jutify_id.state = rec.justify_state
                    email_from = rec.mail_from
                    template = self.env.ref('l10n_cr_attendance.template_model_hr_attendance_justify_validate', raise_if_not_found=False)

                    if template and email_from:
                        template.send_mail(rec.ids[0], force_send=True, notif_layout='mail.mail_notification_light')
                        # MENSAJE DE RETORNO EXITOSO
                        rec.env.user.notify_success(message='Se ha validado es estado de la justificación número: ' + str(rec.jutify_id.name), title="BIEN! ")
                        rec.write({
                            'justify_state': rec.justify_state
                        })
            else:
                raise UserError(_("Estimado Usuario: Solo el monitor de este trabajador está autorizado para validar la justificación de éste trabajador."))

