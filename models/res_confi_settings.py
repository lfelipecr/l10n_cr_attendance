# -*- coding: utf-8 -*-

from odoo import api,fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    time_max_check_in = fields.Float(string='Tiempo Máximo')

    def set_values(self):
        #_logger.info('ResConfigSettings.set_values()')
        self.env['ir.config_parameter'].set_param('time_max_check_in', self.time_max_check_in)

    @api.model
    def get_values(self):
        #_logger.info('ResConfigSettings.get_values()')
        res = super(ResConfigSettings, self).get_values()
        res.update(
            time_max_check_in = self.env['ir.config_parameter'].get_param('time_max_check_in'),
        )
        return res
