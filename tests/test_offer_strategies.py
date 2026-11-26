"""Testes unitários das estratégias de oferta e da fábrica. Dono: P3.

Exercitam cada estratégia isoladamente, sem ``Teller`` nem ``Receipt``,
demonstrando o ganho de testabilidade trazido pelos padrões Strategy,
Template Method e Factory Method (ver ``docs/padroes_projeto.md``).
Preços (conftest): toothbrush 0,99 | toothpaste 1,79 | rice 2,49 |
cherry tomato box 0,69.
"""
import pytest

from discount_strategy import DiscountStrategy
from model_objects import Offer, SpecialOfferType
from offers.factory import DiscountStrategyFactory
from offers.five_for_amount import FiveForAmountStrategy
from offers.percentage_discount import PercentageDiscountStrategy
from offers.three_for_two import ThreeForTwoStrategy
from offers.two_for_amount import TwoForAmountStrategy
from receipt import Receipt


def single_discount(discounts):
    """Garanta que há exatamente um desconto e retorne-o."""
    assert len(discounts) == 1
    return discounts[0]


def test_strategy_returns_empty_list_when_product_is_not_in_cart(
        catalog, toothbrush, rice):
    strategy = ThreeForTwoStrategy(
        Offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0))

    assert strategy.calculate({rice: 3}, catalog) == []


@pytest.mark.parametrize("quantity, expected_amount", [
    (2, None),
    (3, -0.99),
    (7, -1.98),
])
def test_three_for_two_strategy(catalog, toothbrush, quantity, expected_amount):
    strategy = ThreeForTwoStrategy(
        Offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0))

    discounts = strategy.calculate({toothbrush: quantity}, catalog)

    if expected_amount is None:
        assert discounts == []
    else:
        discount = single_discount(discounts)
        assert discount.product == toothbrush
        assert discount.description == "3 for 2"
        assert discount.discount_amount == pytest.approx(expected_amount)


def test_percentage_discount_strategy(catalog, rice):
    strategy = PercentageDiscountStrategy(
        Offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, rice, 10.0))

    discount = single_discount(strategy.calculate({rice: 2}, catalog))

    assert discount.description == "10.0% off"
    assert discount.discount_amount == pytest.approx(-0.498)


@pytest.mark.parametrize("quantity, expected_amount", [
    (1, None),
    (2, -0.39),
    (3, -0.39),
    (4, -0.78),
    (5, -0.78),
])
def test_two_for_amount_strategy(
        catalog, cherry_tomatoes, quantity, expected_amount):
    strategy = TwoForAmountStrategy(
        Offer(SpecialOfferType.TWO_FOR_AMOUNT, cherry_tomatoes, 0.99))

    discounts = strategy.calculate({cherry_tomatoes: quantity}, catalog)

    if expected_amount is None:
        assert discounts == []
    else:
        discount = single_discount(discounts)
        assert discount.description == "2 for 0.99"
        assert discount.discount_amount == pytest.approx(expected_amount)


@pytest.mark.parametrize("quantity, expected_amount", [
    (4, None),
    (5, -1.46),
    (11, -2.92),
])
def test_five_for_amount_strategy(
        catalog, toothpaste, quantity, expected_amount):
    strategy = FiveForAmountStrategy(
        Offer(SpecialOfferType.FIVE_FOR_AMOUNT, toothpaste, 7.49))

    discounts = strategy.calculate({toothpaste: quantity}, catalog)

    if expected_amount is None:
        assert discounts == []
    else:
        discount = single_discount(discounts)
        assert discount.description == "5 for 7.49"
        assert discount.discount_amount == pytest.approx(expected_amount)


@pytest.mark.parametrize("offer_type, expected_class", [
    (SpecialOfferType.THREE_FOR_TWO, ThreeForTwoStrategy),
    (SpecialOfferType.TEN_PERCENT_DISCOUNT, PercentageDiscountStrategy),
    (SpecialOfferType.TWO_FOR_AMOUNT, TwoForAmountStrategy),
    (SpecialOfferType.FIVE_FOR_AMOUNT, FiveForAmountStrategy),
])
def test_factory_creates_strategy_for_each_offer_type(
        toothbrush, offer_type, expected_class):
    strategy = DiscountStrategyFactory.create(Offer(offer_type, toothbrush, 1.0))

    assert isinstance(strategy, expected_class)
    assert isinstance(strategy, DiscountStrategy)


def test_factory_returns_none_for_unknown_offer_type(toothbrush):
    assert DiscountStrategyFactory.create(
        Offer("unknown", toothbrush, 1.0)) is None


def test_cart_ignores_offer_with_unknown_type(catalog, cart, toothbrush):
    cart.add_item(toothbrush)
    receipt = Receipt()

    cart.handle_offers(
        receipt, {toothbrush: Offer("unknown", toothbrush, 1.0)}, catalog)

    assert receipt.discounts == []
