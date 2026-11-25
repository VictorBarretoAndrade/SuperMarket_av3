"""Classe base das ofertas aplicadas a um único produto.

Aplica o padrão Template Method: o algoritmo comum (localizar o produto
no carrinho, obter o preço unitário e montar a lista de descontos) fica
em ``calculate``, e cada oferta concreta implementa apenas o passo
variável ``_discount_for``.
"""
from abc import abstractmethod

from discount_strategy import DiscountStrategy


class SingleProductOfferStrategy(DiscountStrategy):
    """Estratégia base para ofertas vinculadas a um único produto."""

    def __init__(self, offer):
        """Guarde a oferta que será aplicada.

        :param offer: ``Offer`` com o produto e o argumento da promoção.
        """
        self._offer = offer

    @property
    def product(self):
        """Retorne o produto ao qual a oferta se aplica."""
        return self._offer.product

    @property
    def argument(self):
        """Retorne o argumento da oferta (percentual ou preço do pacote)."""
        return self._offer.argument

    def calculate(self, product_quantities, catalog):
        """Calcule o desconto da oferta para o carrinho informado.

        :param product_quantities: dict ``{Product: quantidade}`` do carrinho.
        :param catalog: catálogo que fornece ``unit_price(product)``.
        :return: lista com um ``Discount`` ou lista vazia quando a oferta
            não se aplica.
        """
        if self.product not in product_quantities:
            return []
        quantity = product_quantities[self.product]
        unit_price = catalog.unit_price(self.product)
        discount = self._discount_for(quantity, unit_price)
        return [discount] if discount is not None else []

    @abstractmethod
    def _discount_for(self, quantity, unit_price):
        """Calcule o desconto para a quantidade e o preço unitário.

        :param quantity: quantidade total do produto no carrinho.
        :param unit_price: preço unitário do produto no catálogo.
        :return: ``Discount`` com valor negativo, ou ``None`` quando a
            quantidade não atinge o mínimo da oferta.
        """
