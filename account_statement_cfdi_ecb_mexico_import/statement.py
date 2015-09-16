# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 Mindwork - http://www.mindwork.com.mx/
#    All Rights Reserved.
#    Contact Mindwork (arcangel.salazar@mindwork.com.mx)
############################################################################
#    Coded by: José Arcángel Salazar Delgado (arcangel.salazar@mindwork.com.mx)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp.tools.translate import _
from openerp.osv import orm

from .parser.cfdi_mexico import CFDIParser
from openerp.addons.account_statement_base_completion.statement import ErrorTooManyPartner

class AccountStatementProfile(orm.Model):
    _inherit = "account.statement.profile"

    def _get_import_type_selection(self, cr, uid, context=None):
        """Inherited from parent to add parser."""
        selection = super(AccountStatementProfile, self
                          )._get_import_type_selection(cr, uid,
                                                       context=context)
        selection.append((CFDIParser.PARSER_NAME, _('XML - CFDI ECB Mexico')))
        return selection

class AccountStatementCompletionRule(orm.Model):
    _inherit = "account.statement.completion.rule"
    
    def _get_functions(self, cr, uid, context=None):
        res = super(AccountStatementCompletionRule, self)._get_functions(
            cr, uid, context=context)
        res.append(('get_from_reference_and_partner_rfc',
             'From line reference (based on partner rfc)'))
        return res
    
    def get_from_reference_and_partner_rfc(self, cr, uid, st_line, context=None):
        """Match the partner based on the reference field of the statement line and
        the rfc(vat) of the partner. Then, call the generic get_values_for_line
        method to complete other values. If more than one partner matched,
        raise the ErrorTooManyPartner error.

        :param dict st_line: read of the concerned account.bank.statement.line
        :return:
            A dict of value that can be passed directly to the write method of
            the statement line or {}
           {'partner_id': value,
            'account_id': value,

            ...}
            """
        res = {}
        # We memoize allowed partner
        if not context.get('partner_memoizer'):
            context['partner_memoizer'] = tuple(
                self.pool['res.partner'].search(cr, uid, []))
        if not context['partner_memoizer']:
            return res
        st_obj = self.pool.get('account.bank.statement.line')
        # The regexp_replace() escapes the name to avoid false positive
        # example: 'John J. Doe (No 1)' is escaped to 'John J\. Doe \(No 1\)'
        # See http://stackoverflow.com/a/400316/1504003 for a list of
        # chars to escape. Postgres is POSIX-ARE, compatible with
        # POSIX-ERE excepted that '\' must be escaped inside brackets according
        # to:
        #  http://www.postgresql.org/docs/9.0/static/functions-matching.html
        # in chapter 9.7.3.6. Limits and Compatibility
        sql = r"""
        SELECT id FROM (
            SELECT id,
                regexp_matches(%s,
                    regexp_replace(vat,'([\.\^\$\*\+\?\(\)\[\{\\\|])', %s,
                        'g'), 'i') AS vat_match
            FROM res_partner
            WHERE is_company = 't' AND id IN %s)
            AS res_patner_matcher
        WHERE vat_match IS NOT NULL"""
        cr.execute(
            sql, (st_line['ref'], r"\\\1", context['partner_memoizer']))
        result = cr.fetchall()
        if not result:
            return res
        if len(result) > 1:
            raise ErrorTooManyPartner(
                _('Line named "%s" (Ref:%s) was matched by more than one '
                  'partner while looking on partner by vat') %
                (st_line['name'], st_line['ref']))
        res['partner_id'] = result[0][0]
        st_vals = st_obj.get_values_for_line(
            cr, uid, profile_id=st_line['profile_id'],
            master_account_id=st_line['master_account_id'],
            partner_id=res['partner_id'], line_type=False,
            amount=st_line['amount'] if st_line['amount'] else 0.0,
            context=context)
        res.update(st_vals)
        return res