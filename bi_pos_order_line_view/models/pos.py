# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class POSOderLineInherit(models.Model):
    _inherit = "pos.order.line"

    date_order =fields.Datetime(string="Order Date",related="order_id.date_order",store=True)
    partner_id = fields.Many2one(
        'res.partner',related="order_id.partner_id", string='Customer', readonly=True,store=True)
    image_128 = fields.Image(string="Image",compute="_onchange_product_images")
    user_id = fields.Many2one(
        'res.users', string='Salesperson',related="order_id.user_id",store=True) 
    session_id = fields.Many2one('pos.session', string='Session', related="order_id.session_id",store=True)
    state = fields.Selection([
    ], string='State', related="order_id.state",store=True)
    pos_reference = fields.Char(string='Receipt Number', related="order_id.pos_reference")
    categ_id = fields.Many2one(string='Receipt Number', related="product_id.categ_id")
    branch_id = fields.Many2one(string='Branch', related="session_id.branch_id")
    cost = fields.Float(string='Total Cost', related="product_id.standard_price")
    standard_cost = fields.Float(compute="_compute_standard_cost", string="Cost", store=True)
    
    @api.depends('product_id', 'product_id.standard_price')
    def _compute_standard_cost(self):
        for record in self:
            if record.product_id:
                record.standard_cost = record.product_id.standard_price
                
    @api.depends('product_id')
    def _onchange_product_images(self):
        for line in self:
            line.image_128 = line.product_id.image_128