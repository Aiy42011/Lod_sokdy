# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'POS Order Line View',
    'version': '16.0.0.0',
    'category': 'Point Of Sale',
    'summary': 'Pos sales order line view point of sale order line view pos order line view pos order line in form view point of sales order line list view pos order line menu search pos order line pos session order line view pos product orderline view pos orderline view',
    'description' :"""
        
        POS Order Line View Odoo App helps users to view POS order line in list view. User can shown POS order line in kanban view and form view also they can search by receipt number, product, salesperson, customer and session option then group by session, user, customer, status, order date, etc.

    """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    'depends': ['base','point_of_sale','multi_branch_pos'],
    'data': [
        'views/pos_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    "images":['static/description/POS-Order-Line-View-Banner.gif'],
}
