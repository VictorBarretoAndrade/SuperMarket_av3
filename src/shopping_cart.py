"""Carrinho de compras do supermercado."""
from model_objects import ProductQuantity
from offers.factory import DiscountStrategyFactory


class ShoppingCart:
    """Registra os itens comprados e aplica as ofertas no recibo."""

    def __init__(self):
        """Crie um carrinho vazio."""
        self._items = []
        self._product_quantities = {}

    @property
    def items(self):
        """Retorne os itens na ordem em que foram adicionados."""
        return self._items

    def add_item(self, product):
        """Adicione uma unidade do produto ao carrinho."""
        self.add_item_quantity(product, 1.0)

    @property
    def product_quantities(self):
        """Retorne a quantidade total acumulada de cada produto."""
        return self._product_quantities

    def add_item_quantity(self, product, quantity):
        """Adicione uma quantidade do produto ao carrinho.

        A quantidade é registrada como um novo item e somada ao total
        acumulado do produto.

        :param product: ``Product`` adicionado.
        :param quantity: unidades ou quilos, conforme o ``ProductUnit``.
        """
        self._items.append(ProductQuantity(product, quantity))
        self._product_quantities[product] = (
            self._product_quantities.get(product, 0) + quantity)

    def handle_offers(self, receipt, offers, catalog):
        """Adicione ao recibo os descontos das ofertas aplicáveis ao carrinho.

        O cálculo de cada oferta é delegado à estratégia criada por
        ``DiscountStrategyFactory``. Os produtos são percorridos na ordem
        em que entraram no carrinho, preservando a ordem dos descontos
        no recibo.

        :param receipt: ``Receipt`` que recebe os descontos.
        :param offers: dict ``{Product: Offer}`` cadastrado no ``Teller``.
        :param catalog: catálogo que fornece ``unit_price(product)``.
        """
        for product in self._product_quantities:
            if product not in offers:
                continue
            strategy = DiscountStrategyFactory.create(offers[product])
            if strategy is None:
                continue
            for discount in strategy.calculate(self._product_quantities, catalog):
                receipt.add_discount(discount)
