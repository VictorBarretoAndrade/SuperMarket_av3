from discount_strategy import DiscountStrategy
from model_objects import Discount


class ComboOffer(DiscountStrategy):
    # Estratégia de desconto para combos de múltiplos produtos (D5).

    def __init__(self, products, percent=10.0):
        # Remove duplicatas preservando a ordem para evitar desconto duplicado no mesmo produto.
        self.products = list(dict.fromkeys(products))
        self.percent = percent

    def calculate(self, product_quantities, catalog):
        # Calcula o nº de combos completos pela menor quantidade inteira (D2)
        # e gera um Discount por produto do combo (D3).
        if not self.products or self.percent <= 0:
            return []

        num_combos = min(int(product_quantities.get(p, 0)) for p in self.products)
        if num_combos <= 0:
            return []

        description = f"combo {self.percent:g}% off"
        discounts = []
        for product in self.products:
            unit_price = catalog.unit_price(product)
            discount_amount = -num_combos * unit_price * (self.percent / 100.0)
            discounts.append(Discount(product, description, discount_amount))
        return discounts
