"""Contrato comum das políticas de desconto (definido no commit zero).

Toda modalidade de promoção (ofertas legadas e combos) implementa esta
interface. A assinatura de ``calculate`` não deve ser alterada sem acordo
do time, pois a refatoração (P3) e os combos (P4) dependem dela em paralelo.
"""
from abc import ABC, abstractmethod


class DiscountStrategy(ABC):

    @abstractmethod
    def calculate(self, product_quantities, catalog):
        """Calcula os descontos aplicáveis ao carrinho.

        :param product_quantities: dict ``{Product: quantidade}``, como em
            ``ShoppingCart.product_quantities``.
        :param catalog: catálogo que fornece ``unit_price(product)``.
        :return: ``list[Discount]`` (lista vazia quando não há desconto).
            Valores de desconto são negativos, como no código legado.
        """
