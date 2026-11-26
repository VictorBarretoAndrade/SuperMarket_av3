"""Estratégia da oferta "5 por um valor fixo" (``FIVE_FOR_AMOUNT``)."""
from model_objects import Discount
from offers.single_product_offer import SingleProductOfferStrategy


class FiveForAmountStrategy(SingleProductOfferStrategy):
    """Cobra o valor do argumento a cada grupo completo de 5 unidades."""

    GROUP_SIZE = 5

    def _discount_for(self, quantity, unit_price):
        """Calcule o desconto dos grupos completos de 5 unidades.

        Unidades fora de um grupo completo mantêm o preço normal.
        """
        whole_units = int(quantity)
        if whole_units < self.GROUP_SIZE:
            return None
        groups = whole_units // self.GROUP_SIZE
        remainder = whole_units % self.GROUP_SIZE
        discount_amount = unit_price * quantity - (
            self.argument * groups + remainder * unit_price)
        return Discount(self.product,
                        str(self.GROUP_SIZE) + " for " + str(self.argument),
                        -discount_amount)
