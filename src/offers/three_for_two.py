"""Estratégia da oferta "leve 3, pague 2" (``THREE_FOR_TWO``)."""
from model_objects import Discount
from offers.single_product_offer import SingleProductOfferStrategy


class ThreeForTwoStrategy(SingleProductOfferStrategy):
    """A cada grupo completo de 3 unidades, o cliente paga apenas 2."""

    GROUP_SIZE = 3
    PAID_UNITS = 2

    def _discount_for(self, quantity, unit_price):
        """Calcule o desconto dos grupos completos de 3 unidades.

        Unidades fora de um grupo completo mantêm o preço normal. A ordem
        das operações segue a do código legado para que os valores em
        ponto flutuante do recibo permaneçam idênticos.
        """
        whole_units = int(quantity)
        if whole_units < self.GROUP_SIZE:
            return None
        groups = whole_units // self.GROUP_SIZE
        remainder = whole_units % self.GROUP_SIZE
        discount_amount = quantity * unit_price - (
            (groups * self.PAID_UNITS * unit_price) + remainder * unit_price)
        return Discount(self.product, "3 for 2", -discount_amount)
