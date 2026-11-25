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
| 1 | `src/shopping_cart.py:30-68` (`handle_offers`) | Método de 39 linhas com cadeia de `if`/`elif` por tipo de oferta, mistura `if` e `elif` sem padrão e usa números mágicos (`2`, `3`, `5`, `100.0`) | Método longo / condicionais por tipo / números mágicos | Toda oferta nova obriga a mexer no mesmo método (fere o OCP). Complexidade ciclomática 13 (ver seção 3). Alto risco de regressão a cada mudança. Relação: RNF02, risco R1 do plano |
| 2 | `src/shopping_cart.py:45` | `TWO_FOR_AMOUNT` usa divisão real `quantity_as_int / x`. Com 3 unidades de 0,69 e "2 por 0,99" o legado cobra 2,175 em vez de 1,68 (o "desconto" fica **positivo**) | Bug | Cliente paga mais caro com a promoção do que sem ela. Caracterizado em `tests/test_comportamento_legado.py`, corrigido depois em commit `fix:` (D6). Relação: RF04 |
| 3 | `src/shopping_cart.py:30-68` | O carrinho calcula descontos e conhece o catálogo e o recibo | Responsabilidade misturada (SRP) / Feature envy | `ShoppingCart` muda por dois motivos (itens e regras de promoção). Impossível testar uma regra de desconto isolada sem montar carrinho, catálogo e recibo |
| 4 | `src/shopping_cart.py:36` e `46`, `54`, `63` | `quantity_as_int = int(quantity)` é usado para contar grupos, mas o desconto é calculado com `quantity` (float). Para produto `KILO` com 3,5 kg em "3 por 2", o desconto inclui o 0,5 kg extra | Inconsistência de tipos / bug latente | Valores errados para produtos vendidos a peso. Precisa ser caracterizado antes da refatoração (D6/D7) |
| 5 | `src/shopping_cart.py:47`, `56`, `59`, `65` | Descrição do desconto montada de forma diferente em cada ramo (`"2 for " + str(...)`, `str(x) + " for " + ...`, `"% off"`) | Duplicação / string mágica | O texto do recibo é parte do comportamento observável (D7). Qualquer mudança quebra o recibo aprovado |
| 6 | `src/teller.py:11-12` (`add_special_offer`) | `offers[product]` guarda só uma oferta por produto e sobrescreve a anterior sem avisar | Regra implícita | Comportamento surpresa para quem cadastra ofertas. Precisa virar requisito explícito (RF11) |
| 7 | `src/teller.py:28-29` (`product_with_name`) | Usa `catalog.products`, que só existe no `FakeCatalog` de teste; `SupermarketCatalog` não tem esse atributo | Acoplamento a implementação de teste / código morto | Falha em produção com o catálogo real. Linha nunca executada por nenhum teste |
| 8 | `src/teller.py:16` | Variável `product_quantities = the_cart.items` recebe uma lista de `ProductQuantity`, não o dicionário de quantidades | Nome enganoso | Confunde com `ShoppingCart.product_quantities`, que é outra estrutura |
| 9 | `src/catalog.py:2-8` | `SupermarketCatalog` faz papel de interface, mas é uma classe concreta que lança `Exception` genérica | Interface implícita | Não há contrato verificável (ABC). Exceção genérica dificulta tratamento |
| 10 | `src/shopping_cart.py:12-14` | `items` devolve a lista interna `_items`, que pode ser alterada por fora (já `Receipt.items` devolve cópia) | Encapsulamento quebrado / inconsistência | Quem chama pode modificar o carrinho sem passar por `add_item_quantity`, deixando `_items` e `_product_quantities` dessincronizados |
| 11 | `tests/receipt_printer.py` | Código de produção (formatação do recibo) dentro de `tests/` | Organização | A impressão do recibo não é tratada como parte do sistema. Não deve ser movida agora para não quebrar a API (D7), só registrada |
| 12 | `src/model_objects.py:4-7` | `Product` sem `__eq__`/`__hash__`: dois `Product("toothbrush", EACH)` são chaves diferentes no carrinho, mas o `FakeCatalog` indexa preço pelo **nome** | Identidade inconsistente | Duplicidade silenciosa de itens/ofertas. Afeta o combo, que compara produtos |
| 13 | geral (`receipt.py:15-21`, `shopping_cart.py`) | Dinheiro como `float`, sem arredondamento | Primitive obsession | Erros de arredondamento acumulam (ex.: 2,175). Os testes precisam de `pytest.approx` |
| 14 | geral | Nenhum type hint e nenhuma docstring no legado (0% de comentários, ver seção 3) | Legibilidade | Contratos só são descobertos lendo a implementação |
| 15 | `tests/` | Só 1 teste no legado, que não aplica nenhuma oferta | Baixa cobertura | `handle_offers` com 41% de cobertura: refatorar sem rede de segurança. Relação: RNF01, RNF05, risco R1 |

## 3. Métricas (opcional)
<!-- ex.: complexidade ciclomática com radon, cobertura inicial -->

## 4. Conclusão
