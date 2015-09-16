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

from cStringIO import StringIO
from datetime import datetime

from openerp.addons.account_statement_base_import.parser import (
    BankStatementImportParser,
)
from openerp.addons.account_statement_base_import.parser.file_parser import (
    float_or_zero
)

from lxml import etree

TD_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'


class CFDIParser(BankStatementImportParser):
    """ Parser for CFDI ECB Mexico XML format """
    PARSER_NAME = 'cfdi_ecb_mexico'

    @classmethod
    def parser_for(cls, parser_name):
        """ Return if this parser is suitable for parser_name """
        return parser_name == cls.PARSER_NAME

    def _parse(self, *args, **kwargs):
        self.result_row_list = []
        xml_string = StringIO(self.filebuffer)
        root = etree.fromstring(xml_string.getvalue())
        
        nms = {'ecb': 'http://factura.ecodex.com.mx:4044/Banorte/ecb', 'tfd':'http://www.sat.gob.mx/TimbreFiscalDigital'}
        
        temp = root.xpath(".//ecb:EstadoDeCuentaBancario", namespaces=nms)
        if temp is not None:
            self.statement_name = temp[0].attrib['periodo']
        
        temp = root.xpath(".//tfd:TimbreFiscalDigital", namespaces=nms)
        if temp is not None:
            self.statement_date =datetime.strptime(temp[0].attrib['FechaTimbrado'], TD_DATE_FORMAT,).date()
        
        temp = root.xpath(".//ecb:MovimientoECB", namespaces=nms)
        for child in temp:
            row_list= {}
            row_list['label'] = child.attrib['descripcion']
            row_list['date'] = child.attrib['fecha']
            row_list['amount'] = child.attrib['importe']
            row_list['ref'] = "N/A"
            self.result_row_list.append(row_list)
        
        temp = root.xpath(".//ecb:MovimientoECBFiscal", namespaces=nms)
        for child in temp:
            row_list= {}
            row_list['label'] = child.attrib['descripcion']
            row_list['date'] = child.attrib['fecha']
            row_list['amount'] = child.attrib['importe']
            row_list['ref'] = child.attrib['RFCenajenante']
            self.result_row_list.append(row_list)
        

    def _post(self, *args, **kwargs):
        for line in self.result_row_list:
            line['amount'] = float_or_zero(line['amount'])
            line['date'] = datetime.strptime(
                line['date'], TD_DATE_FORMAT,
            ).date()

    def get_st_line_vals(self, line, *args, **kwargs):
        """
        This method must return a dict of vals that can be passed to create
        method of statement line in order to record it. It is the
        responsibility of every parser to give this dict of vals, so each one
        can implement his own way of recording the lines.
            :param:  line: a dict of vals that represent a line of
              result_row_list
            :return: dict of values to give to the create method of statement
              line, it MUST contain at least:
                {
                    'name':value,
                    'date':value,
                    'amount':value,
                    'ref':value,
                    'label':value,
                }
        """
        return {
            'name': line.get('label', line.get('ref', '')),
            'date': line.get('date', datetime.now().date()),
            'amount': line.get('amount', 0.0),
            'ref': line.get('ref', ''),
            'label': line.get('label', ''),
        }
