# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2009  Renato Lima - Akretion                                  #
#                                                                             #
#This program is free software: you can redistribute it and/or modify         #
#it under the terms of the GNU Affero General Public License as published by  #
#the Free Software Foundation, either version 3 of the License, or            #
#(at your option) any later version.                                          #
#                                                                             #
#This program is distributed in the hope that it will be useful,              #
#but WITHOUT ANY WARRANTY; without even the implied warranty of               #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
#GNU Affero General Public License for more details.                          #
#                                                                             #
#You should have received a copy of the GNU Affero General Public License     #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.        #
###############################################################################

from lxml import etree

from openerp import netsvc
from openerp.osv import orm, fields
from openerp.addons import decimal_precision as dp
from openerp.tools.translate import _

from .l10n_br_account import PRODUCT_FISCAL_TYPE, PRODUCT_FISCAL_TYPE_DEFAULT

OPERATION_TYPE = {
    'out_invoice': 'output',
    'in_invoice': 'input',
    'out_refund': 'input',
    'in_refund': 'output'
}

JOURNAL_TYPE = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale_refund',
    'in_refund': 'purchase_refund'
}


class AccountInvoice(orm.Model):
    _inherit = 'account.invoice'

<<<<<<< HEAD
    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_tax_discount': 0.0,
                'amount_total': 0.0,
                'icms_base': 0.0,
                'icms_value': 0.0,
                'icms_st_base': 0.0,
                'icms_st_value': 0.0,
                'ipi_base': 0.0,
                'ipi_value': 0.0,
                'pis_base': 0.0,
                'pis_value': 0.0,
                'cofins_base': 0.0,
                'cofins_value': 0.0,
                'ii_value': 0.0,
                'amount_insurance': 0.0,
                'amount_freight': 0.0,
                'amount_costs': 0.0,
                'amount_gross': 0.0,
                'amount_discount': 0.0,
            }
            for line in invoice.invoice_line:
                res[invoice.id]['amount_untaxed'] += line.price_total
                res[invoice.id]['icms_base'] += line.icms_base
                res[invoice.id]['icms_value'] += line.icms_value
                res[invoice.id]['icms_st_base'] += line.icms_st_base
                res[invoice.id]['icms_st_value'] += line.icms_st_value
                res[invoice.id]['ipi_base'] += line.ipi_base
                res[invoice.id]['ipi_value'] += line.ipi_value
                res[invoice.id]['pis_base'] += line.pis_base
                res[invoice.id]['pis_value'] += line.pis_value
                res[invoice.id]['cofins_base'] += line.cofins_base
                res[invoice.id]['cofins_value'] += line.cofins_value
                res[invoice.id]['ii_value'] += line.ii_value
                res[invoice.id]['amount_insurance'] += line.insurance_value
                res[invoice.id]['amount_freight'] += line.freight_value
                res[invoice.id]['amount_costs'] += line.other_costs_value
                res[invoice.id]['amount_gross'] += line.price_gross
                res[invoice.id]['amount_discount'] += line.discount_value

            for invoice_tax in invoice.tax_line:
                if not invoice_tax.tax_code_id.tax_discount:
                    res[invoice.id]['amount_tax'] += invoice_tax.amount

            res[invoice.id]['amount_total'] = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed']
        return res

    def _get_fiscal_type(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('fiscal_type', 'product')

    # TODO - Melhorar esse método!
    def fields_view_get(self, cr, uid, view_id=None, view_type=False,
                        context=None, toolbar=False, submenu=False):
        result = super(account_invoice, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)

        if context is None:
            context = {}

        if not view_type:
            view_id = self.pool.get('ir.ui.view').search(
                cr, uid, [('name', '=', 'account.invoice.tree')])
            view_type = 'tree'

        if view_type == 'form':
            eview = etree.fromstring(result['arch'])

            if 'type' in context.keys():
                fiscal_types = eview.xpath("//field[@name='invoice_line']")
                for fiscal_type in fiscal_types:
                    fiscal_type.set(
                        'context', "{'type': '%s', 'fiscal_type': '%s'}" % (
                            context['type'],
                            context.get('fiscal_type', 'product')))

                fiscal_categories = eview.xpath("//field[@name='fiscal_category_id']")
                for fiscal_category_id in fiscal_categories:
                    fiscal_category_id.set('domain',
                                           "[('fiscal_type', '=', '%s'), \
                                           ('type', '=', '%s'), \
                                           ('journal_type', '=', '%s')]" \
                                           % (context.get('fiscal_type', 'product'),
                                              OPERATION_TYPE[context['type']],
                                              JOURNAL_TYPE[context['type']]))
                    fiscal_category_id.set('required', '1')

                document_series = eview.xpath("//field[@name='document_serie_id']")
                for document_serie_id in document_series:
                    document_serie_id.set('domain', "[('fiscal_type', '=', '%s')]" % (context.get('fiscal_type', 'product')))

            if context.get('fiscal_type', False):
                delivery_infos = eview.xpath("//group[@name='delivery_info']")
                for delivery_info in delivery_infos:
                    delivery_info.set('invisible', '1')

            result['arch'] = etree.tostring(eview)

        if view_type == 'tree':
            doc = etree.XML(result['arch'])
            nodes = doc.xpath("//field[@name='partner_id']")
            partner_string = _('Customer')
            if context.get('type', 'out_invoice') in ('in_invoice', 'in_refund'):
                partner_string = _('Supplier')
            for node in nodes:
                node.set('string', partner_string)
            result['arch'] = etree.tostring(doc)
        return result

    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(
            cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(
            cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()

    def _get_cfops(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            result[invoice.id] = []
            new_ids = []
            for line in invoice.invoice_line:
                if line.cfop_id and not line.cfop_id.id in new_ids:
                    new_ids.append(line.cfop_id.id)
            new_ids.sort()
            result[invoice.id] = new_ids
        return result

=======
>>>>>>> fb5e30881b5426ac7ae00320fe3ff39b203772c0
    def _get_receivable_lines(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = []
            if not invoice.move_id:
                continue
            data_lines = [x for x in invoice.move_id.line_id if x.account_id.id == invoice.account_id.id and x.account_id.type in ('receivable', 'payable') and invoice.journal_id.revenue_expense]
            New_ids = []
            for line in data_lines:
                New_ids.append(line.id)
                New_ids.sort()
            res[invoice.id] = New_ids
        return res

    _columns = {
        'issuer': fields.selection(
            [('0', u'Emissão própria'),
            ('1', 'Terceiros')], 'Emitente', readonly=True,
            states={'draft': [('readonly', False)]}),
        'internal_number': fields.char(
            'Invoice Number', size=32, readonly=True,
            states={'draft': [('readonly', False)]},
            help="""Unique number of the invoice, computed
                automatically when the invoice is created."""),
        'fiscal_type': fields.selection(
            PRODUCT_FISCAL_TYPE, 'Tipo Fiscal', required=True),
        'vendor_serie': fields.char(
            u'Série NF Entrada', size=12, readonly=True,
            states={'draft': [('readonly', False)]},
            help=u"Série do número da Nota Fiscal do Fornecedor"),
        'move_line_receivable_id': fields.function(
            _get_receivable_lines, method=True, type='many2many',
            relation='account.move.line', string='Entry Lines'),
        'document_serie_id': fields.many2one(
            'l10n_br_account.document.serie', u'Série',
            domain="[('fiscal_document_id', '=', fiscal_document_id),\
            ('company_id','=',company_id)]", readonly=True,
            states={'draft': [('readonly', False)]}),
        'fiscal_document_id': fields.many2one(
            'l10n_br_account.fiscal.document', 'Documento', readonly=True,
            states={'draft': [('readonly', False)]}),
        'fiscal_document_electronic': fields.related(
            'fiscal_document_id', 'electronic', type='boolean', readonly=True,
            relation='l10n_br_account.fiscal.document', store=True,
            string='Electronic'),
        'fiscal_category_id': fields.many2one(
            'l10n_br_account.fiscal.category', 'Categoria Fiscal',
            readonly=True, states={'draft': [('readonly', False)]}),
        'fiscal_position': fields.many2one(
            'account.fiscal.position', 'Fiscal Position', readonly=True,
            states={'draft': [('readonly', False)]},
            domain="[('fiscal_category_id','=',fiscal_category_id)]"),
<<<<<<< HEAD
        'cfop_ids': fields.function(
            _get_cfops, method=True, type='many2many',
            relation='l10n_br_account.cfop', string='CFOP'),
        'fiscal_document_related_ids': fields.one2many(
            'l10n_br_account.document.related', 'invoice_id',
            'Fiscal Document Related', readonly=True,
            states={'draft': [('readonly', False)]}),
        'carrier_name': fields.char('Nome Transportadora', size=32),
        'vehicle_plate': fields.char('Placa do Veiculo', size=7),
        'vehicle_state_id': fields.many2one(
            'res.country.state', 'UF da Placa'),
        'vehicle_l10n_br_city_id': fields.many2one('l10n_br_base.city',
            'Municipio', domain="[('state_id', '=', vehicle_state_id)]"),
        'amount_gross': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Vlr. Bruto',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (
                    _get_invoice_line, ['price_unit',
                                        'invoice_line_tax_id',
                                        'quantity', 'discount'], 20),
            }, multi='all'),
        'amount_discount': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Desconto',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (
                    _get_invoice_line, ['price_unit',
                                        'invoice_line_tax_id',
                                        'quantity', 'discount'], 20),
            }, multi='all'),                
        'amount_untaxed': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Untaxed',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (
                    _get_invoice_line, ['price_unit',
                                        'invoice_line_tax_id',
                                        'quantity', 'discount'], 20),
            }, multi='all'),
        'amount_tax': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Tax',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line,
                                         ['price_unit',
                                          'invoice_line_tax_id',
                                          'quantity', 'discount'], 20),
            }, multi='all'),
        'amount_total': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line,
                                         ['price_unit',
                                          'invoice_line_tax_id',
                                          'quantity', 'discount'], 20),
            }, multi='all'),
        'icms_base': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Base ICMS',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line,
                                         ['price_unit',
                                          'invoice_line_tax_id',
                                          'quantity', 'discount'], 20),
            }, multi='all'),
        'icms_value': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Valor ICMS',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line,
                                         ['price_unit',
                                          'invoice_line_tax_id',
                                          'quantity', 'discount'], 20),
            }, multi='all'),
        'icms_st_base': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Base ICMS ST',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line,
                                         ['price_unit',
                                          'invoice_line_tax_id',
                                          'quantity', 'discount'], 20),
            },
            multi='all'),
        'icms_st_value': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Valor ICMS ST',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line,
                                         ['price_unit',
                                          'invoice_line_tax_id',
                                          'quantity', 'discount'], 20),
            }, multi='all'),
        'ipi_base': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Base IPI',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line,
                                         ['price_unit',
                                          'invoice_line_tax_id',
                                          'quantity', 'discount'], 20),
            }, multi='all'),
        'ipi_value': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Valor IPI',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line,
                                         ['price_unit',
                                          'invoice_line_tax_id',
                                          'quantity', 'discount'], 20),
            }, multi='all'),
         'pis_base': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Base PIS',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line,
                                         ['price_unit',
                                          'invoice_line_tax_id',
                                          'quantity', 'discount'], 20),
            }, multi='all'),
        'pis_value': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Valor PIS',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line,
                                         ['price_unit',
                                          'invoice_line_tax_id',
                                          'quantity', 'discount'], 20),
            }, multi='all'),
        'cofins_base': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Base COFINS',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line,
                                         ['price_unit',
                                          'invoice_line_tax_id',
                                          'quantity', 'discount'], 20),
            }, multi='all'),
        'cofins_value': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Valor COFINS',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line,
                                         ['price_unit',
                                          'invoice_line_tax_id',
                                          'quantity', 'discount'], 20),
            }, multi='all'),
        'ii_value': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Valor II',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line,
                                         ['price_unit',
                                          'invoice_line_tax_id',
                                          'quantity', 'discount'], 20),
            }, multi='all'),
        'weight': fields.float('Gross weight', readonly=True,
                               states={'draft': [('readonly', False)]},
                               help="The gross weight in Kg.",),
        'weight_net': fields.float('Net weight', help="The net weight in Kg.",
                                    readonly=True,
                                    states={'draft': [('readonly', False)]}),
        'number_of_packages': fields.integer(
            'Volume', readonly=True, states={'draft': [('readonly', False)]}),
        'amount_insurance': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'),
            string='Valor do Seguro',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.line': (_get_invoice_line,
                                         ['insurance_value'], 20),
            }, multi='all'),
        'amount_freight': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'),
            string='Valor do Seguro',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.line': (_get_invoice_line,
                                        ['freight_value'], 20),
            }, multi='all'),
            'amount_costs': fields.function(
        _amount_all, method=True,
        digits_compute=dp.get_precision('Account'), string='Outros Custos',
        store={
            'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                ['invoice_line'], 20),
            'account.invoice.line': (_get_invoice_line,
                                     ['other_costs_value'], 20)}, multi='all')
=======
        'account_document_event_ids': fields.one2many(
            'l10n_br_account.document_event', 'document_event_ids',
            u'Eventos'),
        'fiscal_comment': fields.text(u'Observação Fiscal'),
>>>>>>> fb5e30881b5426ac7ae00320fe3ff39b203772c0
    }

    def _default_fiscal_document(self, cr, uid, context):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        fiscal_document = self.pool.get('res.company').read(
            cr, uid, user.company_id.id, ['service_invoice_id'],
            context=context)['service_invoice_id']

        return fiscal_document and fiscal_document[0] or False

    def _default_fiscal_document_serie(self, cr, uid, context):
        fiscal_document_serie = False
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company = self.pool.get('res.company').browse(
            cr, uid, user.company_id.id, context=context)

        fiscal_document_serie = company.document_serie_service_id and \
            company.document_serie_service_id.id or False

        return fiscal_document_serie

    _defaults = {
        'issuer': '0',
        'fiscal_type': PRODUCT_FISCAL_TYPE_DEFAULT,
        'fiscal_document_id': _default_fiscal_document,
        'document_serie_id': _default_fiscal_document_serie,
    }

    def _check_invoice_number(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoices = self.browse(cr, uid, ids, context=context)
        domain = []
        for invoice in invoices:
            if not invoice.number:
                continue
            fiscal_document = invoice.fiscal_document_id and \
            invoice.fiscal_document_id.id or False
            domain.extend([('internal_number', '=', invoice.number),
                           ('fiscal_type', '=', invoice.fiscal_type),
                           ('fiscal_document_id', '=', fiscal_document)
                           ])
            if invoice.issuer == '0':
                domain.extend(
                    [('company_id', '=', invoice.company_id.id),
                    ('internal_number', '=', invoice.number),
                    ('fiscal_document_id', '=', invoice.fiscal_document_id.id),
                    ('issuer', '=', '0')])
            else:
                domain.extend(
                    [('partner_id', '=', invoice.partner_id.id),
                    ('vendor_serie', '=', invoice.vendor_serie),
                    ('issuer', '=', '1')])

            invoice_id = self.pool.get('account.invoice').search(
                cr, uid, domain)
            if len(invoice_id) > 1:
                return False
        return True

    _constraints = [
        (_check_invoice_number,
        u"Error!\nNão é possível registrar \
        documentos fiscais com números repetidos.",
        ['number']),
    ]

    #TODO - Melhorar esse método!
    def fields_view_get(self, cr, uid, view_id=None, view_type=False,
                        context=None, toolbar=False, submenu=False):
        result = super(AccountInvoice, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)

        if context is None:
            context = {}

        if not view_type:
            view_id = self.pool.get('ir.ui.view').search(
                cr, uid, [('name', '=', 'account.invoice.tree')])
            view_type = 'tree'

        if view_type == 'form':
            eview = etree.fromstring(result['arch'])

            if 'type' in context.keys():
                fiscal_types = eview.xpath("//field[@name='invoice_line']")
                for fiscal_type in fiscal_types:
                    fiscal_type.set(
                        'context', "{'type': '%s', 'fiscal_type': '%s'}" % (
                            context['type'],
                            context.get('fiscal_type', 'product')))

                fiscal_categories = eview.xpath(
                    "//field[@name='fiscal_category_id']")
                for fiscal_category_id in fiscal_categories:
                    fiscal_category_id.set(
                        'domain',
                        """[('fiscal_type', '=', '%s'), ('type', '=', '%s'),
                        ('state', '=', 'approved'),
                        ('journal_type', '=', '%s')]"""
                        % (context.get('fiscal_type', 'product'),
                            OPERATION_TYPE[context['type']],
                            JOURNAL_TYPE[context['type']]))
                    fiscal_category_id.set('required', '1')

                document_series = eview.xpath(
                    "//field[@name='document_serie_id']")
                for document_serie_id in document_series:
                    document_serie_id.set(
                        'domain', "[('fiscal_type', '=', '%s')]"
                        % (context.get('fiscal_type', 'product')))

            if context.get('fiscal_type', False):
                delivery_infos = eview.xpath("//group[@name='delivery_info']")
                for delivery_info in delivery_infos:
                    delivery_info.set('invisible', '1')

            result['arch'] = etree.tostring(eview)

        if view_type == 'tree':
            doc = etree.XML(result['arch'])
            nodes = doc.xpath("//field[@name='partner_id']")
            partner_string = _('Customer')
            if context.get('type', 'out_invoice') in ('in_invoice', 'in_refund'):
                partner_string = _('Supplier')
            for node in nodes:
                node.set('string', partner_string)
            result['arch'] = etree.tostring(doc)
        return result

    def init(self, cr):
        # Remove a constraint na coluna número do documento fiscal,
        # no caso dos documentos de entradas dos fornecedores pode existir
        # documentos fiscais de fornecedores diferentes com a mesma numeração
        cr.execute("ALTER TABLE %s DROP CONSTRAINT IF EXISTS %s" % (
            'account_invoice', 'account_invoice_number_uniq'))

    # go from canceled state to draft state
    def action_cancel_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {
            'state': 'draft',
            'internal_number': False,
            'nfe_access_key': False,
            'nfe_status': False,
            'nfe_date': False,
            'nfe_export_date': False})
        wf_service = netsvc.LocalService("workflow")
        for inv_id in ids:
            wf_service.trg_delete(uid, 'account.invoice', inv_id, cr)
            wf_service.trg_create(uid, 'account.invoice', inv_id, cr)
        return True

    def copy(self, cr, uid, id, default={}, context=None):
        default.update({
            'internal_number': False,
            'nfe_access_key': False,
            'nfe_status': False,
            'nfe_protocol_number': False,
            'nfe_date': False,
            'nfe_export_date': False,
            'account_document_event_ids': False,
        })
        return super(AccountInvoice, self).copy(cr, uid, id, default, context)

    def action_internal_number(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        for inv in self.browse(cr, uid, ids):
            if inv.issuer == '0':
                sequence = self.pool.get('ir.sequence')
                sequence_read = sequence.read(
                    cr, uid, inv.document_serie_id.internal_sequence_id.id,
                    ['number_next'])
                invalid_number = self.pool.get(
                    'l10n_br_account.invoice.invalid.number').search(
                        cr, uid, [
                        ('number_start', '<=', sequence_read['number_next']),
                        ('number_end', '>=', sequence_read['number_next']),
                        ('state', '=', 'done')])

                if invalid_number:
                    raise orm.except_orm(
                        _(u'Número Inválido !'),
                        _(u"O número: %s da série: %s, esta inutilizado") % (
                            sequence_read['number_next'],
                            inv.document_serie_id.name))

                seq_no = sequence.get_id(cr, uid, inv.document_serie_id.internal_sequence_id.id, context=context)
                self.write(cr, uid, inv.id, {'ref': seq_no, 'internal_number': seq_no})
        return True

    def action_number(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        #TODO: not correct fix but required a frech values before reading it.
        self.write(cr, uid, ids, {})

        for obj_inv in self.browse(cr, uid, ids, context=context):
            inv_id = obj_inv.id
            move_id = obj_inv.move_id and obj_inv.move_id.id or False
            ref = obj_inv.internal_number or obj_inv.reference or ''

            cr.execute('UPDATE account_move SET ref=%s '
                'WHERE id=%s AND (ref is null OR ref = \'\')',
                    (ref, move_id))
            cr.execute('UPDATE account_move_line SET ref=%s '
                'WHERE move_id=%s AND (ref is null OR ref = \'\')',
                (ref, move_id))
            cr.execute('UPDATE account_analytic_line SET ref=%s '
                'FROM account_move_line '
                'WHERE account_move_line.move_id = %s '
                'AND account_analytic_line.move_id = account_move_line.id',
                (ref, move_id))

            for inv_id, name in self.name_get(cr, uid, [inv_id]):
                ctx = context.copy()
                if obj_inv.type in ('out_invoice', 'out_refund'):
                    ctx = self.get_log_context(cr, uid, context=ctx)
                message = _('Invoice ') + " '" + name + "' " + _("is validated.")
                self.log(cr, uid, inv_id, message, context=ctx)
        return True

    def finalize_invoice_move_lines(self, cr, uid, invoice_browse, move_lines):
        """finalize_invoice_move_lines(cr, uid, invoice, move_lines) -> move_lines
        Hook method to be overridden in additional modules to verify and possibly alter the
        move lines to be created by an invoice, for special cases.
        :param invoice_browse: browsable record of the invoice that is generating the move lines
        :param move_lines: list of dictionaries with the account.move.lines (as for create())
        :return: the (possibly updated) final move_lines to create for this invoice
        """
        move_lines = super(AccountInvoice, self).finalize_invoice_move_lines(cr, uid, invoice_browse, move_lines)
        cont=1
        result = []
        for move_line in move_lines:
            if (move_line[2]['debit'] or move_line[2]['credit']):
                if (move_line[2]['account_id'] == invoice_browse.account_id.id):
                    move_line[2]['name'] = '%s/%s' % ( invoice_browse.internal_number, cont)
                    cont +=1
                result.append(move_line)
        return result

    def _fiscal_position_map(self, cr, uid, result, context=None, **kwargs):

        if not context:
            context = {}
        context.update({'use_domain': ('use_invoice', '=', True)})
        kwargs.update({'context': context})

        if not kwargs.get('fiscal_category_id', False):
            return result

        obj_company = self.pool.get('res.company').browse(
            cr, uid, kwargs.get('company_id', False))
        obj_fcategory = self.pool.get('l10n_br_account.fiscal.category')

        fcategory = obj_fcategory.browse(
            cr, uid, kwargs.get('fiscal_category_id'))
        result['value']['journal_id'] = fcategory.property_journal and \
        fcategory.property_journal.id or False
        if not result['value'].get('journal_id', False):
            raise orm.except_orm(
                _(u'Nenhum Diário !'),
                _(u"Categoria fiscal: '%s', não tem um diário contábil para a \
                empresa %s") % (fcategory.name, obj_company.name))

        obj_fp_rule = self.pool.get('account.fiscal.position.rule')
        return obj_fp_rule.apply_fiscal_mapping(cr, uid, result, **kwargs)

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,
                            date_invoice=False, payment_term=False,
                            partner_bank_id=False, company_id=False,
                            fiscal_category_id=False):

        result = super(AccountInvoice, self).onchange_partner_id(
            cr, uid, ids, type, partner_id, date_invoice, payment_term,
            partner_bank_id, company_id)

        return self._fiscal_position_map(
            cr, uid, result, False, partner_id=partner_id,
            partner_invoice_id=partner_id, company_id=company_id,
            fiscal_category_id=fiscal_category_id)

    def onchange_company_id(self, cr, uid, ids, company_id, partner_id, type,
                            invoice_line, currency_id,
                            fiscal_category_id=False):

        result = super(AccountInvoice, self).onchange_company_id(
            cr, uid, ids, company_id, partner_id, type, invoice_line,
            currency_id)

        return self._fiscal_position_map(
            cr, uid, result, False, partner_id=partner_id,
            partner_invoice_id=partner_id, company_id=company_id,
            fiscal_category_id=fiscal_category_id)

    def onchange_fiscal_category_id(self, cr, uid, ids,
                                    partner_address_id=False,
                                    partner_id=False, company_id=False,
                                    fiscal_category_id=False):
        result = {'value': {}}
        return self._fiscal_position_map(
            cr, uid, result, False, partner_id=partner_id,
            partner_invoice_id=partner_id, company_id=company_id,
            fiscal_category_id=fiscal_category_id)

    def onchange_fiscal_document_id(self, cr, uid, ids, fiscal_document_id,
                                    company_id, issuer, fiscal_type,
                                    context=None):
        result = {'value': {'document_serie_id': False}}
        if not context:
            context = {}
        company = self.pool.get('res.company').browse(cr, uid, company_id,
            context=context)

        if issuer == '0':
            serie = company.document_serie_service_id and \
            company.document_serie_service_id.id or False
            result['value']['document_serie_id'] = serie

        return result


class AccountInvoiceLine(orm.Model):
    _inherit = 'account.invoice.line'

    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            res[line.id] = {
                'discount_value': 0.0,
                'price_gross': 0.0,
                'price_subtotal': 0.0,
                'price_total': 0.0,
            }
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(
                cr, uid, line.invoice_line_tax_id, price, line.quantity,
                line.product_id, line.invoice_id.partner_id,
                fiscal_position=line.fiscal_position)

            if line.invoice_id:
                currency = line.invoice_id.currency_id
                price_gross = cur_obj.round(cr, uid, currency,
                        line.price_unit * line.quantity)
                res[line.id].update({
                    'price_subtotal': cur_obj.round(
                        cr, uid, currency,
                        taxes['total'] - taxes['total_tax_discount']),
                    'price_total': cur_obj.round(
                        cr, uid, currency, taxes['total']),
                    'price_gross': price_gross,
                    'discount_value': (price_gross - taxes['total']),
                })

        return res

    _columns = {
        'fiscal_category_id': fields.many2one(
            'l10n_br_account.fiscal.category', 'Categoria'),
        'fiscal_position': fields.many2one(
            'account.fiscal.position', u'Posição Fiscal',
            domain="[('fiscal_category_id','=',fiscal_category_id)]"),
<<<<<<< HEAD
        'cfop_id': fields.many2one('l10n_br_account.cfop', 'CFOP'),
        'fiscal_classification_id': fields.many2one(
            'account.product.fiscal.classification', 'Classficação Fiscal'),
        'product_type': fields.selection(
            [('product', 'Produto'), ('service', u'Serviço')],
            'Tipo do Produto', required=True),
        'discount_value': fields.function(
            _amount_line, method=True, string='Vlr. desconto', type="float",
            digits_compute=dp.get_precision('Account'),
            store=True, multi='all'),
        'price_total': fields.function(
            _amount_line, method=True, string='Total', type="float",
            digits_compute=dp.get_precision('Account'),
            store=True, multi='all'),
        'price_gross': fields.function(
            _amount_line, method=True, string='Vlr. Bruto', type="float",
            digits_compute=dp.get_precision('Account'),
            store=True, multi='all'),
        'price_subtotal': fields.function(
            _amount_line, method=True, string='Subtotal', type="float",
            digits_compute=dp.get_precision('Account'),
            store=True, multi='all'),
=======
>>>>>>> fb5e30881b5426ac7ae00320fe3ff39b203772c0
        'price_total': fields.function(
            _amount_line, method=True, string='Total', type="float",
            digits_compute=dp.get_precision('Account'),
            store=True, multi='all'),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type=False,
                        context=None, toolbar=False, submenu=False):

        result = super(AccountInvoiceLine, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)

        if context is None:
            context = {}

        if view_type == 'form':
            eview = etree.fromstring(result['arch'])

            if 'type' in context.keys():
                fiscal_categories = eview.xpath("//field[@name='fiscal_category_id']")
                for fiscal_category_id in fiscal_categories:
                    fiscal_category_id.set(
                        'domain', """[('type', '=', '%s'),
                        ('journal_type', '=', '%s')]"""
                        % (OPERATION_TYPE[context['type']],
                        JOURNAL_TYPE[context['type']]))
                    fiscal_category_id.set('required', '1')

            product_ids = eview.xpath("//field[@name='product_id']")
            for product_id in product_ids:
                product_id.set('domain', "[('fiscal_type', '=', '%s')]" % (
                    context.get('fiscal_type', 'service')))

            result['arch'] = etree.tostring(eview)

        return result

    def _fiscal_position_map(self, cr, uid, result, context=None, **kwargs):

        if not context:
            context = {}
        context.update({'use_domain': ('use_invoice', '=', True)})
        kwargs.update({'context': context})
        result['value']['cfop_id'] = False
        obj_fp_rule = self.pool.get('account.fiscal.position.rule')
        result_rule = obj_fp_rule.apply_fiscal_mapping(
            cr, uid, result, **kwargs)
        if result['value'].get('fiscal_position', False):
            obj_fp = self.pool.get('account.fiscal.position').browse(
                cr, uid, result['value'].get('fiscal_position', False))
            result_rule['value']['cfop_id'] = obj_fp.cfop_id and obj_fp.cfop_id.id or False
            if kwargs.get('product_id', False):
                obj_product = self.pool.get('product.product').browse(
                cr, uid, kwargs.get('product_id', False), context=context)
                context['fiscal_type'] = obj_product.fiscal_type
                if context.get('type') in ('out_invoice', 'out_refund'):
                    context['type_tax_use'] = 'sale'
                    taxes = obj_product.taxes_id and obj_product.taxes_id or (kwargs.get('account_id', False) and self.pool.get('account.account').browse(cr, uid, kwargs.get('account_id', False), context=context).tax_ids or False)
                else:
                    context['type_tax_use'] = 'purchase'
                    taxes = obj_product.supplier_taxes_id and obj_product.supplier_taxes_id or (kwargs.get('account_id', False) and self.pool.get('account.account').browse(cr, uid, kwargs.get('account_id', False), context=context).tax_ids or False)
                tax_ids = self.pool.get('account.fiscal.position').map_tax(
                    cr, uid, obj_fp, taxes, context)

                result_rule['value']['invoice_line_tax_id'] = tax_ids

                result['value'].update(self._get_tax_codes(
                    cr, uid, kwargs.get('product_id'),
                    obj_fp, tax_ids, kwargs.get('company_id'),
                    context=context))

        return result_rule

    def product_id_change(self, cr, uid, ids, product, uom, qty=0, name='',
                          type='out_invoice', partner_id=False,
                          fposition_id=False, price_unit=False,
                          currency_id=False, context=None, company_id=False,
                          parent_fiscal_category_id=False,
                          parent_fposition_id=False):

        result = super(AccountInvoiceLine, self).product_id_change(
            cr, uid, ids, product, uom, qty, name, type, partner_id,
            fposition_id, price_unit, currency_id, context, company_id)

        fiscal_position = fposition_id or parent_fposition_id or False

        if not parent_fiscal_category_id or not product or not fiscal_position:
            return result
        obj_fp_rule = self.pool.get('account.fiscal.position.rule')
        product_fiscal_category_id = obj_fp_rule.product_fiscal_category_map(
            cr, uid, product, parent_fiscal_category_id)

        if product_fiscal_category_id:
            parent_fiscal_category_id = product_fiscal_category_id

        result['value']['fiscal_category_id'] = parent_fiscal_category_id

        result = self._fiscal_position_map(cr, uid, result, context,
            partner_id=partner_id, partner_invoice_id=partner_id,
            company_id=company_id, product_id=product,
            fiscal_category_id=parent_fiscal_category_id,
            account_id=result['value'].get('account_id'))

        values = {
            'partner_id': partner_id,
            'company_id': company_id,
            'product_id': product,
            'quantity': qty,
            'price_unit': price_unit,
            'fiscal_position': result['value'].get('fiscal_position'),
            'invoice_line_tax_id': [[6, 0, result['value'].get('invoice_line_tax_id')]],
        }
        result['value'].update(self._validate_taxes(cr, uid, values, context))
        return result

    def onchange_fiscal_category_id(self, cr, uid, ids, partner_id,
                                    company_id, product_id, fiscal_category_id,
                                    account_id, context):
        result = {'value': {}}
        return self._fiscal_position_map(
            cr, uid, result, context, partner_id=partner_id,
            partner_invoice_id=partner_id, company_id=company_id,
            fiscal_category_id=fiscal_category_id, product_id=product_id,
            account_id=account_id)

    def onchange_fiscal_position(self, cr, uid, ids, partner_id, company_id,
                                product_id, fiscal_category_id,
                                account_id, context):
        result = {'value': {}}
        return self._fiscal_position_map(
            cr, uid, result, context, partner_id=partner_id,
            partner_invoice_id=partner_id, company_id=company_id,
            fiscal_category_id=fiscal_category_id, product_id=product_id,
            account_id=account_id)

    def onchange_account_id(self, cr, uid, ids, product_id, partner_id,
                            inv_type, fposition_id, account_id=False,
                            context=None, fiscal_category_id=False,
                            company_id=False):

        result = super(AccountInvoiceLine, self).onchange_account_id(
            cr, uid, ids, product_id, partner_id, inv_type, fposition_id,
            account_id)
        return self._fiscal_position_map(
            cr, uid, result, context, partner_id=partner_id,
            partner_invoice_id=partner_id, company_id=company_id,
            fiscal_category_id=fiscal_category_id, product_id=product_id,
            account_id=account_id)

    def uos_id_change(self, cr, uid, ids, product, uom, qty=0, name='',
                    type='out_invoice', partner_id=False, fposition_id=False,
                    price_unit=False, currency_id=False, context=None,
                    company_id=None, fiscal_category_id=False):

        result = super(AccountInvoiceLine, self).uos_id_change(
            cr, uid, ids, product, uom, qty, name, type, partner_id,
            fposition_id, price_unit, currency_id, context, company_id)
        return self._fiscal_position_map(
            cr, uid, result, context, partner_id=partner_id,
            partner_invoice_id=partner_id, company_id=company_id,
            fiscal_category_id=fiscal_category_id, product_id=product,
            account_id=False)
