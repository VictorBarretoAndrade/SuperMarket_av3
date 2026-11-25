"""Estratégia da oferta "2 por um valor fixo" (``TWO_FOR_AMOUNT``)."""
from model_objects import Discount
from offers.single_product_offer import SingleProductOfferStrategy


class TwoForAmountStrategy(SingleProductOfferStrategy):
    """Cobra o valor do argumento a cada par de unidades."""

    GROUP_SIZE = 2

    def _discount_for(self, quantity, unit_price):
        """Calcule o desconto dos pares de unidades.

        Decisão D6: a divisão real (``/``) do legado é preservada de
        propósito. Com quantidade ímpar ela gera um "desconto" positivo,
        bug caracterizado em ``tests/test_comportamento_legado.py`` que
        será corrigido em um commit ``fix:`` separado.
        """
        whole_units = int(quantity)
        if whole_units < self.GROUP_SIZE:
            return None
        total = (self.argument * (whole_units / self.GROUP_SIZE)
                 + whole_units % self.GROUP_SIZE * unit_price)
        discount_amount = unit_price * quantity - total
        return Discount(self.product, "2 for " + str(self.argument),
                        -discount_amount)
