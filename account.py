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
import pickle


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
        if unique_tax_ids:
            return res
        import pdb; pdb.set_trace()
        # -- search the defaul tax in configuration:
        field_name = 'taxes_id'
        if inv_type in ('in_invoice', 'in_refund'):
            field_name = 'supplier_taxes_id'
        ir_values_obj = self.pool.get('ir.values')
        filter_value = [
            ('key', '=', 'default'),
            ('model', '=', 'product.product'),
            ('name', '=', field_name)]
        ir_values_ids = self.search(cr, uid, filter_value, {})
        if not ir_values_ids:
            return res
        value = ir_values_obj.browse(cr, uid, ir_values_ids[0], {})
        default_tax_id = pickle.loads(value.value.encode('utf-8'))
        fpos = fposition_id or False
        unique_tax_ids = self.pool.get('account.fiscal.position').map_tax(
            cr, uid, fpos, [default_tax_id])
        return {'value': {'invoice_line_tax_id': unique_tax_ids}}
