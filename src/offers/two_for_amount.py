"""Estratégia da oferta "2 por um valor fixo" (``TWO_FOR_AMOUNT``)."""
from model_objects import Discount
from offers.single_product_offer import SingleProductOfferStrategy


class TwoForAmountStrategy(SingleProductOfferStrategy):
    """Cobra o valor do argumento a cada par de unidades."""

    GROUP_SIZE = 2

    def _discount_for(self, quantity, unit_price):
        """Calcule o desconto dos pares completos de unidades.

        A unidade que sobra fora de um par mantém o preço normal. O legado
        usava divisão real (``/``) e, com quantidade ímpar, cobrava meio
        par a mais, gerando um "desconto" positivo; a correção (decisão
        D6) usa divisão inteira (``//``).
        """
        whole_units = int(quantity)
        if whole_units < self.GROUP_SIZE:
            return None
        pairs = whole_units // self.GROUP_SIZE
        total = (self.argument * pairs
                 + whole_units % self.GROUP_SIZE * unit_price)
        discount_amount = unit_price * quantity - total
        return Discount(self.product, "2 for " + str(self.argument),
                        -discount_amount)
