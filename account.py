# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Andre@ (<a.gallina@cgsoftware.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
from tools.translate import _


class account_invoice_line(osv.osv):

    _inherit = "account.invoice.line"

    def onchange_account_id(self, cr, uid, ids, product_id,
                            partner_id, inv_type, fposition_id, account_id):
        res = super(account_invoice_line, self).onchange_account_id(
            cr, uid, ids, product_id, partner_id, inv_type,
            fposition_id, account_id)
        standard_res = res.get('value', False)
        if not standard_res:
            return res
        unique_tax_ids = standard_res.get('invoice_line_tax_id', {})
        if not unique_tax_ids:
            # -- search the defaul tax in configuration:
            field_name = 'default_sale_tax'
            if inv_type in ('in_invoice', 'in_refund'):
                field_name = 'default_purchase_tax'
            user = self.pool.get('res.users').browse(cr, uid, uid, {})
            acc_setting_obj = self.pool.get('account.config.settings')
            acc_setting_id = acc_setting_obj.search(
                cr, uid, [('company_id', '=', user.company_id.id)], {})
            if not acc_setting_id:
                return res
            default_tax = acc_setting_obj.read(
                cr, uid, acc_setting_id, ([field_name]), {})
            default_tax_id = default_tax[0][field_name]
            fpos = fposition_id or False
            unique_tax_ids = self.pool.get('account.fiscal.position').map_tax(
                cr, uid, fpos, [default_tax_id])
            return {'value': {'invoice_line_tax_id': unique_tax_ids}}
