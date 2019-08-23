# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2019 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import logging

from odoo.addons.component.core import AbstractComponent, Component

_logger = logging.getLogger(__name__)

try:
    import locomotivecms
except (ImportError, IOError) as err:
    _logger.debug(err)


_logger = logging.getLogger(__name__)


class LocomotiveAdapter(Component):
    _name = "locomotive.client.adapter"
    _inherit = "shopinvader.client.adapter"

    def __init__(self, work_context):
        super().__init__(work_context)
        self.client = locomotivecms.LocomotiveClient(
            self.client_data['username'],
            self.client_data['password'],
            self.client_data['handle'],
            self.client_data['location'],
        )
        self.resource = None

    def create(self, vals):
        return self.resource.create(vals)

    def write(self, external_id, vals):
        return self.resource.write(external_id, vals)

    def delete(self, binding_id):
        self.resource.delete(binding_id)

    def read(self, external_id):
        return self.resource.read(external_id)

    def search(self, page=1, per_page=80):
        return self.resource.search(page=page, per_page=per_page)


class LocomotiveContentAdapter(Component):
    _name = "locomotive.content.adapter"
    _inherit = "locomotive.client.adapter"
    _content_type = None
    _apply_on = []

    def __init__(self, work_context):
        super().__init__(work_context)
        self.resource = self.client.content(self._content_type)


class LocomotiveAssetAdapter(Component):
    _name = "locomotive.asset.adapter"
    _inherit = "locomotive.client.adapter"
    _content_type = None
    _apply_on = []

    def __init__(self, work_context):
        super().__init__(work_context)
        self.resource = self.client.asset()


class LocomotiveBackendAdapter(Component):
    _name = "locomotive.backend.adapter"
    _inherit = [
        "shopinvader.backend.client.adapter",
        "locomotive.client.adapter",
    ]

    def __init__(self, work_context):
        super().__init__(work_context)
        self.resource = self.client.site()

    def _get_site(self, handle):
        for site in self.resource.search():
            if site["handle"] == handle:
                return site
        self._site_not_found()

    def write(self, handle, vals):
        """
            The write method will only write the "store" information of
            the site in the field "_store" as this field is a custom field
            it's part of the json of the field metafields.
            To update it we need to read it, update it and push it
        """
        site = self._get_site(handle)
        metafields = json.loads(site["metafields"])
        metafields["_store"].update(vals)
        return self.resource.write(
            site["_id"], {"metafields": json.dumps(metafields)}
        )
