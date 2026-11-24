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

pytestmark = pytest.mark.xfail(
    raises=AttributeError, reason="combo ainda não implementado (P4)")


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
