from model_objects import ProductQuantity
from offers.factory import DiscountStrategyFactory


class ShoppingCart:

    def __init__(self):
        self._items = []
        self._product_quantities = {}

    @property
    def items(self):
        return self._items

    def add_item(self, product):
        self.add_item_quantity(product, 1.0)

    @property
    def product_quantities(self):
        return self._product_quantities

    def add_item_quantity(self, product, quantity):
        self._items.append(ProductQuantity(product, quantity))
        if product in self._product_quantities.keys():
            self._product_quantities[product] = self._product_quantities[product] + quantity
        else:
            self._product_quantities[product] = quantity

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
