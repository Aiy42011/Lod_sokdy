from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        compute='_compute_sale_order_id',
        store=True
    )

    discount_method = fields.Selection(
        [("fixed", "Fixed"), ("percentage", "Percentage")],
        string="Discount Method",
        related="sale_order_id.discount_method",
        store=True
    )

    discount_amount = fields.Float(
        string="Discount Amount",
        related="sale_order_id.discount_amount",
        store=True
    )

    total_discount = fields.Float(
        string="- Discount",
        compute="_compute_total_discount",
        store=True
    )

    @api.depends('invoice_line_ids.sale_line_ids.order_id')
    def _compute_sale_order_id(self):
        """Link the invoice to the sale order."""
        for move in self:
            sale_order = move.invoice_line_ids.mapped('sale_line_ids.order_id')
            move.sale_order_id = sale_order[:1] if sale_order else False

    @api.depends("discount_method", "discount_amount", "amount_untaxed")
    def _compute_total_discount(self):
        """Compute the total discount based on method and amount."""
        for rec in self:
            if rec.discount_method and rec.discount_amount:
                if rec.discount_method == "fixed":
                    rec.total_discount = min(rec.discount_amount, rec.amount_untaxed)
                elif rec.discount_method == "percentage":
                    if 0 <= rec.discount_amount <= 100:
                        rec.total_discount = round((rec.discount_amount * rec.amount_untaxed) / 100, 2)
                    else:
                        rec.total_discount = 0.0
            else:
                rec.total_discount = 0.0

    @api.depends('line_ids.debit', 'line_ids.credit', 'line_ids.currency_id',
             'line_ids.amount_currency', 'line_ids.amount_residual',
             'line_ids.amount_residual_currency', 'line_ids.payment_id.state',
             'total_discount', 'amount_untaxed', 'amount_tax')
    def _compute_amount(self):
        """Recompute the total amounts of the invoice with discount applied."""
        super(AccountMove, self)._compute_amount()
        for rec in self:
            if rec.discount_method and rec.discount_amount:
                discount_amount = rec.count_total_discount()  
                rec.amount_total = rec.amount_untaxed + rec.amount_tax - discount_amount
                rec.amount_residual = rec.amount_total 
            else:
                rec.amount_total = rec.amount_untaxed + rec.amount_tax
                rec.amount_residual = rec.amount_total

            for line in rec.line_ids:
                if line.account_id.internal_type == 'receivable':
                    line.debit = rec.amount_total  
                    line.credit = 0.0  
                elif line.account_id.internal_type == 'payable':
                    line.debit = 0.0  
                    line.credit = rec.amount_total  
                elif line.account_id.internal_type == 'income':
                    line.debit = 0.0  
                    line.credit = rec.amount_total  

                elif line.account_id.internal_type == 'income':
                    if rec.discount_method == 'fixed':
                        line.debit = discount_amount
                        line.credit = rec.amount_untaxed + rec.amount_tax - discount_amount
                    elif rec.discount_method == 'percentage':
                        line.debit = discount_amount
                        line.credit = rec.amount_untaxed + rec.amount_tax - discount_amount
                else:
                    line.debit = 0.0
                    line.credit = 0.0


    @api.onchange("discount_method", "discount_amount", "amount_untaxed")
    def onchange_on_total_discount(self):
        """Recompute total discount on change of method, amount, or untaxed total."""
        if self.state == "draft":
            if self.discount_amount and self.discount_method:
                if self.amount_untaxed:
                    self.total_discount = self.count_total_discount()
                    self.amount_total = (self.amount_untaxed + self.amount_tax) - self.total_discount
                else:
                    self.total_discount = 0.0
            else:
                self.total_discount = 0.0

    def count_total_discount(self):
        """Calculate the total discount based on the selected method."""
        amount = 0
        if self.discount_amount and self.discount_method:
            if self.discount_method == "fixed":
                amount = self.discount_amount
            elif self.discount_method == "percentage":
                amount = round((self.discount_amount * self.amount_untaxed) / 100, 2)
        return amount

    def write(self, vals):
        """Override write to add validation for discounts."""
        res = super(AccountMove, self).write(vals)
        for rec in self:
            
            if 'discount_method' in vals or 'discount_amount' in vals:
                rec._compute_total_discount()

        return res
