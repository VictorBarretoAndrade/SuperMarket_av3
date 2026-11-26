from combo_offer import ComboOffer
from model_objects import Offer
from receipt import Receipt


class Teller:

    def __init__(self, catalog):
        self.catalog = catalog
        self.offers = {}
        self.combo_offers = []

    def add_special_offer(self, offer_type, product, argument):
        self.offers[product] = Offer(offer_type, product, argument)

    def add_combo_offer(self, products, percent=10.0):
        # Registra uma estratégia de combo pela API pública definida em D4.
        self.combo_offers.append(ComboOffer(products, percent))

    def checks_out_articles_from(self, the_cart):
        receipt = Receipt()
        product_quantities = the_cart.items
        for pq in product_quantities:
            p = pq.product
            quantity = pq.quantity
            unit_price = self.catalog.unit_price(p)
            price = quantity * unit_price
            receipt.add_product(p, quantity, unit_price, price)

        the_cart.handle_offers(receipt, self.offers, self.catalog)

        # D1: exclui produtos com oferta individual antes de avaliar combos.
        eligible_quantities = {
            product: qty
            for product, qty in the_cart.product_quantities.items()
            if product not in self.offers
        }
        for combo in self.combo_offers:
            discounts = combo.calculate(eligible_quantities, self.catalog)
            if not discounts:
                continue
            # Abate as unidades já usadas para evitar desconto duplicado entre combos.
            used = combo.complete_combos(eligible_quantities)
            for product in combo.products:
                eligible_quantities[product] -= used
            for discount in discounts:
                receipt.add_discount(discount)

        return receipt

    def product_with_name(self, name):
        return self.catalog.products.get(name, None)