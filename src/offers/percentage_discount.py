"""Estratégia de desconto percentual (``TEN_PERCENT_DISCOUNT``)."""
from model_objects import Discount
from offers.single_product_offer import SingleProductOfferStrategy


class PercentageDiscountStrategy(SingleProductOfferStrategy):
    """Aplica o percentual do argumento sobre o valor total do produto.

    Apesar do nome legado ``TEN_PERCENT_DISCOUNT``, o percentual vem do
    argumento da oferta e pode ser diferente de 10.
    """

    def _discount_for(self, quantity, unit_price):
        """Calcule o desconto percentual sobre quantidade x preço unitário.

        Assim como no legado, o desconto é gerado para qualquer
        quantidade, inclusive fracionada (produtos vendidos por quilo).
        """
        return Discount(self.product, str(self.argument) + "% off",
                        -quantity * unit_price * self.argument / 100.0)
