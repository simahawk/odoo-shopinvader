# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tools import float_round

from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _convert_shipping(self, cart):
        res = super(AbstractSaleService, self)._convert_shipping(cart)
        selected_carrier = {}
        if cart.carrier_id:
            carrier = cart.carrier_id
            selected_carrier = {
                "id": carrier.id,
                "name": carrier.name,
                "description": carrier.name,
            }
        res.update(
            {
                "amount": {
                    "tax": cart.shipping_amount_tax,
                    "untaxed": cart.shipping_amount_untaxed,
                    "total": cart.shipping_amount_total,
                },
                "selected_carrier": selected_carrier,
            }
        )
        return res

    def _convert_amount(self, sale):
        """
        Inherit to add amounts without shipping prices included
        :param sale: sale.order recordset
        :return: dict
        """
        result = super(AbstractSaleService, self)._convert_amount(sale)
        # Remove the shipping amounts for originals amounts
        shipping_amounts = self._convert_shipping(sale).get("amount", {})
        tax = result.get("tax", 0) - shipping_amounts.get("tax", 0)
        untaxed = result.get("untaxed", 0) - shipping_amounts.get("untaxed", 0)
        total = result.get("total", 0) - shipping_amounts.get("total", 0)
        precision = sale.currency_id.decimal_places
        result.update(
            {
                "tax_without_shipping": float_round(tax, precision),
                "untaxed_without_shipping": float_round(untaxed, precision),
                "total_without_shipping": float_round(total, precision),
            }
        )
        return result

    def _prepare_carrier(self, cart, carrier):
        return {
            "id": carrier.id,
            "name": carrier.name,
            "description": carrier.name,
            "price": carrier.rate_shipment(cart).get("price", 0.0),
        }

    # TODO: this method seems not used
    def _get_available_carrier(self, cart):
        return [
            self._prepare_carrier(cart, carrier)
            for carrier in cart._invader_available_carriers()
        ]

    def _is_item(self, line):
        res = super(AbstractSaleService, self)._is_item(line)
        return res and not line.is_delivery

    def _convert_one_line(self, line):
        """
        Inherit to add the qty_delivered
        :param line: sale.order.line
        :return: dict
        """
        values = super(AbstractSaleService, self)._convert_one_line(line)
        values.update({"qty_delivered": line.qty_delivered})
        return values
