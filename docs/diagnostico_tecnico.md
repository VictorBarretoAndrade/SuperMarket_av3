# Diagnóstico técnico

> Dono: **P1** · Enunciado: Passo 3 e item 5.1 · Barema: 1,0 (ausência: -3,0)

Para cada problema: arquivo e linha, trecho, tipo de smell, impacto em evolução/manutenção/testabilidade e relação com algum RF/RNF ou risco.

## 1. Visão geral do sistema legado
<!-- fluxo: ShoppingCart -> Teller.checks_out_articles_from -> handle_offers -> Receipt -> ReceiptPrinter -->

## 2. Problemas encontrados

| # | Arquivo:linha | Problema | Categoria | Impacto |
|---|---------------|----------|-----------|---------|
| 1 | `src/shopping_cart.py` (`handle_offers`) | Método longo; cadeia de `if`/`elif` por tipo de oferta; números mágicos | Método longo / condicionais | Toda oferta nova obriga a mexer no mesmo método (fere o OCP) |
| 2 | `src/shopping_cart.py` | `TWO_FOR_AMOUNT` usa divisão real `quantity_as_int / x`: com quantidade ímpar o cliente paga mais caro | Bug | Ver `tests/test_comportamento_legado.py` e a decisão D6 |
| 3 | `src/shopping_cart.py` | O carrinho calcula descontos | Responsabilidade misturada (SRP) | |
| 4 | `src/teller.py` (`add_special_offer`) | `offers[product]` só guarda uma oferta por produto e sobrescreve a anterior sem avisar | | |
| 5 | `src/teller.py` (`product_with_name`) | Usa `catalog.products`, que só existe no `FakeCatalog` | Acoplamento / baixa testabilidade | |
| 6 | `tests/receipt_printer.py` | Código de produção dentro de `tests/` | Organização | |
| 7 | geral | Dinheiro como `float`; `Product` sem `__eq__`/`__hash__`; mistura de `quantity` com `quantity_as_int` | | |
| 8 | `tests/` | Só 1 teste no legado | Baixa cobertura | |

## 3. Métricas (opcional)
<!-- ex.: complexidade ciclomática com radon, cobertura inicial -->

## 4. Conclusão
