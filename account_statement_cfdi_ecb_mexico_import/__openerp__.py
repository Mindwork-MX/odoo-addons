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
{
    'name': 'Importar Estados de cuenta CFDI XML con componente ECB',
    'version': '0.1',
    "author" : "Mindwork",
    "category" : "Localization/Mexico",
    "website" : "http://www.mindwork.com.mx/",
    'summary': 'XML CFDI Mexico with ECB component statement import',
    "license" : "AGPL-3",
    'description':"""
This Module enable the import of bank statement in Mexican CFDI using the ECB complement.
=================================================================================
Contribuitors
* Jose Arcangel Salazar Delgado (arcangel.salazar@mindwork.com.mx)

""",
    'depends': [
        'account_statement_base_import','account_statement_base_completion'
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [    
        'data.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
