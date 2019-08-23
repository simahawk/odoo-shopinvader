# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderBackend(models.Model):
    _description = "Shopinvader Locomotive CMS Backend"
    _name = "shopinvader.backend"
    _inherit = ["shopinvader.backend", "connector.backend"]
    _backend_name = "locomotivecms"

    location = fields.Char(
        help="Locomotive URL (see Developers section Locomotive site)",
        sparse="client_data",
    )
    username = fields.Char(
        help="Locomotive user email (see Developers section in Locomotive site)",
        sparse="client_data",
    )
    password = fields.Char(
        help="Locomotive user API key (see Developers section in Locomotive site)",
        sparse="client_data",
    )
    handle = fields.Char(
        help="Locomotive site handle (see Developers section in Locomotive site)",
    )
