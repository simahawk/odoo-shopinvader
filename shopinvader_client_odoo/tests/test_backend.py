# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging
from contextlib import contextmanager

from .common import LocoCommonCase

_logger = logging.getLogger(__name__)

# pylint: disable=W7936
try:
    import requests_mock
except (ImportError, IOError) as err:
    _logger.debug(err)

ODOO_STORE_JSON_KEY = ["all_filters", "available_countries", "currencies_rate"]


@contextmanager
def mock_site_api(base_url, site):
    with requests_mock.mock() as m:
        m.post(base_url + "/tokens.json", json={"token": u"744cfcfb3cd3"})
        m.get(base_url + "/sites", json=[site])
        yield m.put(
            base_url + "/sites/%s" % site["_id"],
            json={"foo": "we_do_not_care"},
        )


class TestBackend(LocoCommonCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        ref = self.env.ref
        country_ids = [ref("base.fr").id, ref("base.us").id]
        filter_ids = [
            ref("shopinvader.product_filter_1").id,
            ref("shopinvader.product_filter_2").id,
        ]
        currency_ids = [ref("base.USD").id, ref("base.EUR").id]
        self.backend.write(
            {
                "allowed_country_ids": [(6, 0, country_ids)],
                "filter_ids": [(6, 0, filter_ids)],
                "currency_ids": [(6, 0, currency_ids)],
            }
        )
        # simplified version of site data
        self.site = {
            "name": "My site",
            "handle": "shopinvader",
            "_id": "space_id",
            "metafields": json.dumps(
                {
                    "foo": "test",
                    "_store": {
                        "bar": "test",
                        "all_filters": "{}",
                        "available_countries": "{}",
                    },
                }
            ),
        }

    def _extract_metafields(self, metafields):
        metafields = json.loads(metafields)
        self.assertIn("_store", metafields)
        for key, vals in metafields["_store"].items():
            if key in ODOO_STORE_JSON_KEY:
                self.assertIsInstance(vals, str)
                metafields["_store"][key] = json.loads(vals)
        return metafields

    def test_synchronize_metadata(self):
        ref = self.env.ref
        with mock_site_api(self.base_url, self.site) as mock:
            self.backend.synchronize_metadata()
            metafields = self._extract_metafields(
                mock.request_history[0].json()["site"]["metafields"]
            )
            expected_metafields = {
                "foo": "test",
                "_store": {
                    "bar": "test",
                    "all_filters": {
                        "en": [
                            {
                                "code": "variant_attributes.color",
                                "name": "Color",
                                "help": "<p>Color of the product</p>",
                            },
                            {
                                "code": "variant_attributes.legs",
                                "name": "Memory",
                                "help": "<p>Memory of the product</p>",
                            },
                        ]
                    },
                    "available_countries": {
                        "en": [
                            {"name": "France", "id": ref("base.fr").id},
                            {"name": "United States", "id": ref("base.us").id},
                        ]
                    },
                    "currencies_rate": {
                        "USD": ref("base.USD").rate,
                        "EUR": ref("base.EUR").rate,
                    },
                },
            }
            self.assertEqual(metafields, expected_metafields)

    def test_synchronize_currency(self):
        ref = self.env.ref
        with mock_site_api(self.base_url, self.site) as mock:
            self.backend.synchronize_currency()
            metafields = self._extract_metafields(
                mock.request_history[0].json()["site"]["metafields"]
            )
            expected_metafields = {
                "foo": "test",
                "_store": {
                    "bar": "test",
                    "all_filters": {},
                    "available_countries": {},
                    "currencies_rate": {
                        "USD": ref("base.USD").rate,
                        "EUR": ref("base.EUR").rate,
                    },
                },
            }
            self.assertEqual(metafields, expected_metafields)
