"""Testes de aceitação dos combos promocionais. Dono: P4.

Contrato definido no commit zero (docs/divisao_tarefas.md):
  - API pública: teller.add_combo_offer(products, percent=10.0)
  - o desconto gera um Discount por produto do combo
  - D1: produto com oferta individual NÃO participa de combo
  - D2: nº de combos = menor quantidade inteira entre os produtos do combo

Enquanto o combo não existe, os testes ficam como xfail (AttributeError).
Ao implementar, remova o marcador ``pytestmark``.
Preços (conftest): toothbrush 0,99 | toothpaste 1,79 -> combo = 2,78.
"""
import pytest

from model_objects import SpecialOfferType
from tests.receipt_printer import ReceiptPrinter


def total_discount(receipt):
    return sum(d.discount_amount for d in receipt.discounts)


def test_one_full_combo_gets_ten_percent_off(teller, cart, toothbrush, toothpaste):
    teller.add_combo_offer([toothbrush, toothpaste])
    cart.add_item(toothbrush)
    cart.add_item(toothpaste)

    receipt = teller.checks_out_articles_from(cart)

    assert total_discount(receipt) == pytest.approx(-0.278)
    assert receipt.total_price() == pytest.approx(2.502)


def test_extra_item_keeps_regular_price(teller, cart, toothbrush, toothpaste):
    teller.add_combo_offer([toothbrush, toothpaste])
    cart.add_item_quantity(toothbrush, 2)
    cart.add_item(toothpaste)

    receipt = teller.checks_out_articles_from(cart)

    assert total_discount(receipt) == pytest.approx(-0.278)
    assert receipt.total_price() == pytest.approx(3.492)


def test_two_full_combos(teller, cart, toothbrush, toothpaste):
    teller.add_combo_offer([toothbrush, toothpaste])
    cart.add_item_quantity(toothbrush, 2)
    cart.add_item_quantity(toothpaste, 2)

    receipt = teller.checks_out_articles_from(cart)

    assert total_discount(receipt) == pytest.approx(-0.556)
    assert receipt.total_price() == pytest.approx(5.004)


def test_incomplete_combo_has_no_discount(teller, cart, toothbrush, toothpaste):
    teller.add_combo_offer([toothbrush, toothpaste])
    cart.add_item(toothbrush)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.discounts == []
    assert receipt.total_price() == pytest.approx(0.99)


def test_product_with_individual_offer_is_not_in_combo(teller, cart, toothbrush, toothpaste):
    """Decisão D1: evita desconto duplicado no mesmo item."""
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, toothbrush, 10.0)
    teller.add_combo_offer([toothbrush, toothpaste])
    cart.add_item(toothbrush)
    cart.add_item(toothpaste)

    receipt = teller.checks_out_articles_from(cart)

    assert [d.product for d in receipt.discounts] == [toothbrush]
    assert total_discount(receipt) == pytest.approx(-0.099)


def test_combo_generates_one_discount_per_product_and_prints(teller, cart, toothbrush, toothpaste):
    """Decisão D3: um Discount por produto, sem alterar Receipt nem ReceiptPrinter."""
    teller.add_combo_offer([toothbrush, toothpaste])
    cart.add_item(toothbrush)
    cart.add_item(toothpaste)

    receipt = teller.checks_out_articles_from(cart)

    assert len(receipt.discounts) == 2
    assert [d.product for d in receipt.discounts] == [toothbrush, toothpaste]
    assert receipt.discounts[0].discount_amount == pytest.approx(-0.099)
    assert receipt.discounts[1].discount_amount == pytest.approx(-0.179)

    printed = ReceiptPrinter().print_receipt(receipt)
    assert "combo 10% off (toothbrush)" in printed
    assert "combo 10% off (toothpaste)" in printed


def test_combo_with_custom_percent(teller, cart, toothbrush, toothpaste):
    """Decisão D4: permite configurar percentual diferente de 10%."""
    teller.add_combo_offer([toothbrush, toothpaste], percent=20.0)
    cart.add_item(toothbrush)
    cart.add_item(toothpaste)

    receipt = teller.checks_out_articles_from(cart)

    assert total_discount(receipt) == pytest.approx(-0.556)
    assert receipt.total_price() == pytest.approx(2.224)


def test_combo_registered_before_individual_offer_still_respects_d1(teller, cart, toothbrush, toothpaste):
    """Decisão D1 independe da ordem de cadastro no Teller."""
    teller.add_combo_offer([toothbrush, toothpaste])
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, toothbrush, 10.0)
    cart.add_item(toothbrush)
    cart.add_item(toothpaste)

    receipt = teller.checks_out_articles_from(cart)

    assert [d.product for d in receipt.discounts] == [toothbrush]
    assert total_discount(receipt) == pytest.approx(-0.099)


def test_combo_with_fractional_quantity_uses_integer_floor(teller, cart, apples, rice):
    """Decisão D2: usa a menor quantidade inteira; fração excedente paga preço normal."""
    teller.add_combo_offer([apples, rice])
    cart.add_item_quantity(apples, 2.5)
    cart.add_item_quantity(rice, 3)

    receipt = teller.checks_out_articles_from(cart)

    # 2 combos completos: -10% sobre 2 * (1.99 + 2.49) = -0.896
    assert total_discount(receipt) == pytest.approx(-0.896)
    assert receipt.total_price() == pytest.approx((2.5 * 1.99 + 3 * 2.49) - 0.896)


def test_combo_with_three_products(teller, cart, toothbrush, toothpaste, rice):
    teller.add_combo_offer([toothbrush, toothpaste, rice])
    cart.add_item_quantity(toothbrush, 2)
    cart.add_item_quantity(toothpaste, 3)
    cart.add_item_quantity(rice, 1)

    receipt = teller.checks_out_articles_from(cart)

    # 1 combo completo: -10% sobre (0.99 + 1.79 + 2.49) = -0.527
    assert len(receipt.discounts) == 3
    assert total_discount(receipt) == pytest.approx(-0.527)


def test_empty_combo_generates_no_discount(teller, cart, toothbrush):
    teller.add_combo_offer([])
    cart.add_item(toothbrush)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.discounts == []
    assert receipt.total_price() == pytest.approx(0.99)

