# Diagnóstico técnico

> Dono: **P1** · Enunciado: Passo 3 e item 5.1 · Barema: 1,0 (ausência: -3,0)

Para cada problema: arquivo e linha, trecho, tipo de smell, impacto em evolução/manutenção/testabilidade e relação com algum RF/RNF ou risco.

Base da análise: tag `v0-legado` (código original do kata, versão `python_pytest`). Os números de linha se referem a essa tag.

## 1. Visão geral do sistema legado

O sistema calcula o preço de um carrinho de supermercado e emite o recibo. São cinco módulos em `src/` e um em `tests/`:

| Módulo | Papel |
|--------|-------|
| `model_objects.py` | Objetos de domínio: `Product`, `ProductUnit` (`EACH`/`KILO`), `ProductQuantity`, `SpecialOfferType`, `Offer`, `Discount` |
| `catalog.py` | `SupermarketCatalog`: "interface" do catálogo de preços (os métodos só lançam exceção, porque o real acessaria o banco) |
| `shopping_cart.py` | `ShoppingCart`: guarda os itens **e** calcula os descontos (`handle_offers`) |
| `teller.py` | `Teller`: registra as ofertas e faz o checkout |
| `receipt.py` | `Receipt` e `ReceiptItem`: itens, descontos e total |
| `tests/receipt_printer.py` | `ReceiptPrinter`: formata o recibo em texto (40 colunas) |

Fluxo de um checkout:

```
Teller.add_special_offer(tipo, produto, argumento)   -> offers[produto] = Offer(...)
ShoppingCart.add_item / add_item_quantity            -> _items (lista) + _product_quantities (dict)
Teller.checks_out_articles_from(cart)
  ├─ para cada ProductQuantity em cart.items: Receipt.add_product(...)   (uma linha por inclusão)
  └─ cart.handle_offers(receipt, offers, catalog)
        └─ para cada produto com oferta: calcula Discount -> Receipt.add_discount(...)
Receipt.total_price()  = soma dos itens + soma dos descontos (negativos)
ReceiptPrinter.print_receipt(receipt)                -> texto do recibo
```

Pontos que chamam atenção logo de início:

- toda a regra de negócio das promoções está concentrada em **um único método** (`ShoppingCart.handle_offers`);
- o carrinho, que deveria só guardar itens, é quem calcula desconto;
- o legado tem **um único teste** (`test_ten_percent_discount`), que nem exercita uma oferta aplicada.

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
