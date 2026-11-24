"""Testes de caracterização do comportamento legado. Dono: P2.

Objetivo: registrar o comportamento ATUAL (inclusive bugs) usando apenas a
API pública (Teller, ShoppingCart, Receipt, ReceiptPrinter), para que os
mesmos testes passem antes (tag v0-legado) e depois da refatoração.

Cenários a cobrir (checklist do Passo 6 / item 5.7 do enunciado):
  [ ] carrinho vazio
  [ ] carrinho sem ofertas (EACH e KILO)
  [ ] mesmo produto adicionado várias vezes (add_item e add_item_quantity)
  [ ] THREE_FOR_TWO: 1, 2, 3, 4, 6, 7 unidades
  [ ] TEN_PERCENT_DISCOUNT: EACH e KILO, argumento diferente de 10
  [ ] TWO_FOR_AMOUNT: 1, 2, 3, 4 unidades
  [ ] FIVE_FOR_AMOUNT: 4, 5, 6, 10, 11 unidades
  [ ] oferta para produto que não está no carrinho
  [ ] duas ofertas para o mesmo produto (a última sobrescreve)
  [ ] várias ofertas em produtos diferentes no mesmo carrinho
  [ ] recibo impresso completo (ReceiptPrinter + approvaltests)
"""
import pytest

from model_objects import SpecialOfferType


def test_two_for_amount_with_odd_quantity_charges_more_than_regular_price(
        teller, cart, cherry_tomatoes):
    """Caracteriza um BUG do legado (ver docs/diagnostico_tecnico.md).

    shopping_cart.py usa divisão real (quantity_as_int / x) em vez de inteira.
    Com 3 unidades de 0,69 e oferta "2 por 0,99" o total deveria ser
    0,99 + 0,69 = 1,68 (abaixo dos 2,07 sem oferta), mas o legado gera um
    "desconto" POSITIVO de 0,105 e cobra 2,175 - mais caro que sem oferta.
    Se o time decidir corrigir (commit fix separado), este teste deve ser
    atualizado no mesmo commit, com a justificativa documentada.
    """
    teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, cherry_tomatoes, 0.99)
    cart.add_item_quantity(cherry_tomatoes, 3)

    receipt = teller.checks_out_articles_from(cart)

    assert len(receipt.discounts) == 1
    assert receipt.discounts[0].discount_amount == pytest.approx(0.105)
    assert receipt.total_price() == pytest.approx(2.175)
