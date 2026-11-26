"""Testes de caracterização do comportamento legado. Dono: P2.

Objetivo: registrar o comportamento ATUAL (inclusive bugs) usando apenas a
API pública (Teller, ShoppingCart, Receipt, ReceiptPrinter), para que os
mesmos testes passem antes (tag v0-legado) e depois da refatoração.

Cenários a cobrir (checklist do Passo 6 / item 5.7 do enunciado):
  [x] carrinho vazio
  [x] carrinho sem ofertas (EACH e KILO)
  [x] mesmo produto adicionado várias vezes (add_item e add_item_quantity)
  [x] THREE_FOR_TWO: 1, 2, 3, 4, 6, 7 unidades
  [x] TEN_PERCENT_DISCOUNT: EACH e KILO, argumento diferente de 10
  [x] TWO_FOR_AMOUNT: 1, 2, 3, 4 unidades
  [x] FIVE_FOR_AMOUNT: 4, 5, 6, 10, 11 unidades
  [x] oferta para produto que não está no carrinho
  [x] duas ofertas para o mesmo produto (a última sobrescreve)
  [x] várias ofertas em produtos diferentes no mesmo carrinho
  [x] recibo impresso completo (ReceiptPrinter + approvaltests)
"""
import pytest
from approvaltests import verify

from model_objects import SpecialOfferType
from tests.receipt_printer import ReceiptPrinter


def test_empty_cart_produces_empty_receipt(teller, cart):
    receipt = teller.checks_out_articles_from(cart)

    assert receipt.items == []
    assert receipt.discounts == []
    assert receipt.total_price() == 0


def test_cart_without_offers_sums_each_and_kilo_items(
        teller, cart, toothbrush, apples):
    cart.add_item(toothbrush)
    cart.add_item_quantity(apples, 2.5)

    receipt = teller.checks_out_articles_from(cart)

    assert len(receipt.items) == 2
    assert receipt.discounts == []
    assert receipt.total_price() == pytest.approx(0.99 + 2.5 * 1.99)


def test_same_product_added_multiple_times_aggregates_for_offer(
        teller, cart, toothbrush):
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)
    cart.add_item(toothbrush)
    cart.add_item_quantity(toothbrush, 2)

    receipt = teller.checks_out_articles_from(cart)

    assert len(receipt.items) == 2
    assert len(receipt.discounts) == 1
    assert receipt.discounts[0].discount_amount == pytest.approx(-0.99)
    assert receipt.total_price() == pytest.approx(1.98)


@pytest.mark.parametrize(
    "quantity, expected_discounts, expected_discount_amount, expected_total",
    [
        (1, 0, 0.0, 0.99),
        (2, 0, 0.0, 1.98),
        (3, 1, -0.99, 1.98),
        (4, 1, -0.99, 2.97),
        (6, 1, -1.98, 3.96),
        (7, 1, -1.98, 4.95),
    ],
)
def test_three_for_two_offer(
        teller, cart, toothbrush,
        quantity, expected_discounts, expected_discount_amount, expected_total):
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)
    cart.add_item_quantity(toothbrush, quantity)

    receipt = teller.checks_out_articles_from(cart)

    assert len(receipt.discounts) == expected_discounts
    if expected_discounts:
        assert receipt.discounts[0].description == "3 for 2"
        assert receipt.discounts[0].discount_amount == pytest.approx(
            expected_discount_amount)
    assert receipt.total_price() == pytest.approx(expected_total)


def test_ten_percent_discount_on_each_item(teller, cart, rice):
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, rice, 10.0)
    cart.add_item_quantity(rice, 2)

    receipt = teller.checks_out_articles_from(cart)

    assert len(receipt.discounts) == 1
    assert receipt.discounts[0].description == "10.0% off"
    assert receipt.discounts[0].discount_amount == pytest.approx(-0.498)
    assert receipt.total_price() == pytest.approx(4.482)


def test_percentage_discount_on_kilo_with_argument_other_than_ten(
        teller, cart, apples):
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, apples, 20.0)
    cart.add_item_quantity(apples, 2.5)

    receipt = teller.checks_out_articles_from(cart)

    assert len(receipt.discounts) == 1
    assert receipt.discounts[0].description == "20.0% off"
    assert receipt.discounts[0].discount_amount == pytest.approx(-0.995)
    assert receipt.total_price() == pytest.approx(3.98)


@pytest.mark.parametrize(
    "quantity, expected_discounts, expected_discount_amount, expected_total",
    [
        (1, 0, 0.0, 0.69),
        (2, 1, -0.39, 0.99),
        (4, 1, -0.78, 1.98),
    ],
)
def test_two_for_amount_offer_even_and_single_quantities(
        teller, cart, cherry_tomatoes,
        quantity, expected_discounts, expected_discount_amount, expected_total):
    teller.add_special_offer(
        SpecialOfferType.TWO_FOR_AMOUNT, cherry_tomatoes, 0.99)
    cart.add_item_quantity(cherry_tomatoes, quantity)

    receipt = teller.checks_out_articles_from(cart)

    assert len(receipt.discounts) == expected_discounts
    if expected_discounts:
        assert receipt.discounts[0].description == "2 for 0.99"
        assert receipt.discounts[0].discount_amount == pytest.approx(
            expected_discount_amount)
    assert receipt.total_price() == pytest.approx(expected_total)


def test_two_for_amount_with_odd_quantity_charges_leftover_at_regular_price(
        teller, cart, cherry_tomatoes):
    """Verifica a correção do bug do legado (D6, ver docs/padroes_projeto.md).

    O legado usava divisão real (quantity_as_int / x) e, com 3 unidades de
    0,69 e oferta "2 por 0,99", gerava um "desconto" POSITIVO de 0,105 e
    cobrava 2,175, mais caro que sem oferta. Após o commit fix, 1 par sai
    por 0,99 e a unidade excedente por 0,69: total 1,68, desconto -0,39.
    """
    teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, cherry_tomatoes, 0.99)
    cart.add_item_quantity(cherry_tomatoes, 3)

    receipt = teller.checks_out_articles_from(cart)

    assert len(receipt.discounts) == 1
    assert receipt.discounts[0].discount_amount == pytest.approx(-0.39)
    assert receipt.total_price() == pytest.approx(1.68)


@pytest.mark.parametrize(
    "quantity, expected_discounts, expected_discount_amount, expected_total",
    [
        (4, 0, 0.0, 7.16),
        (5, 1, -1.46, 7.49),
        (6, 1, -1.46, 9.28),
        (10, 1, -2.92, 14.98),
        (11, 1, -2.92, 16.77),
    ],
)
def test_five_for_amount_offer(
        teller, cart, toothpaste,
        quantity, expected_discounts, expected_discount_amount, expected_total):
    teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, toothpaste, 7.49)
    cart.add_item_quantity(toothpaste, quantity)

    receipt = teller.checks_out_articles_from(cart)

    assert len(receipt.discounts) == expected_discounts
    if expected_discounts:
        assert receipt.discounts[0].description == "5 for 7.49"
        assert receipt.discounts[0].discount_amount == pytest.approx(
            expected_discount_amount)
    assert receipt.total_price() == pytest.approx(expected_total)


def test_offer_for_product_not_in_cart_is_ignored(
        teller, cart, toothbrush, rice):
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, rice, 10.0)
    cart.add_item(toothbrush)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.discounts == []
    assert receipt.total_price() == pytest.approx(0.99)


def test_second_offer_for_same_product_overwrites_first(teller, cart, rice):
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, rice, 10.0)
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, rice, 25.0)
    cart.add_item(rice)

    receipt = teller.checks_out_articles_from(cart)

    assert len(receipt.discounts) == 1
    assert receipt.discounts[0].description == "25.0% off"
    assert receipt.discounts[0].discount_amount == pytest.approx(-0.6225)
    assert receipt.total_price() == pytest.approx(1.8675)


def test_multiple_offers_on_different_products_in_same_cart(
        teller, cart, toothbrush, toothpaste, apples, rice, cherry_tomatoes):
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)
    teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, toothpaste, 7.49)
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, apples, 10.0)
    teller.add_special_offer(
        SpecialOfferType.TWO_FOR_AMOUNT, cherry_tomatoes, 0.99)

    cart.add_item_quantity(toothbrush, 3)
    cart.add_item_quantity(toothpaste, 5)
    cart.add_item_quantity(apples, 2.0)
    cart.add_item_quantity(cherry_tomatoes, 2)
    cart.add_item(rice)

    receipt = teller.checks_out_articles_from(cart)

    assert len(receipt.discounts) == 4
    expected_total = 1.98 + 7.49 + (2.0 * 1.99 * 0.9) + 0.99 + 2.49
    assert receipt.total_price() == pytest.approx(expected_total)


def test_printed_receipt_matches_approved_output(
        teller, cart, toothbrush, toothpaste, apples, rice, cherry_tomatoes):
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)
    teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, toothpaste, 7.49)
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, apples, 10.0)
    teller.add_special_offer(
        SpecialOfferType.TWO_FOR_AMOUNT, cherry_tomatoes, 0.99)

    cart.add_item_quantity(toothbrush, 3)
    cart.add_item_quantity(toothpaste, 5)
    cart.add_item_quantity(apples, 2.5)
    cart.add_item_quantity(cherry_tomatoes, 2)
    cart.add_item(rice)

    receipt = teller.checks_out_articles_from(cart)
    printed = ReceiptPrinter().print_receipt(receipt)

    verify(printed)
