# Documento de requisitos

> Dono: **P1** · Enunciado: Passo 4 e item 5.2 · Barema: 1,0

Cada requisito precisa de um ID, uma descrição, um critério de aceitação verificável e o(s) teste(s) que o cobrem (rastreabilidade).

Preços usados nos exemplos (fixture `catalog` em `tests/conftest.py`): toothbrush 0,99 · toothpaste 1,79 · apples 1,99/kg · rice 2,49 · cherry tomato box 0,69.
Descontos aparecem no recibo como valores **negativos**. Comparações de valor usam `pytest.approx` (dinheiro em `float`, ver diagnóstico #13).

## 1. Requisitos funcionais

| ID | Descrição | Critério de aceitação | Teste(s) |
|----|-----------|-----------------------|----------|
| RF01 | Calcular o total do carrinho sem ofertas | Total = Σ (quantidade × preço unitário). 2,5 kg de apples -> 4,975, sem descontos. Carrinho vazio -> total 0, sem itens nem descontos | `test_supermarket.py::test_ten_percent_discount`, `test_comportamento_legado.py::test_empty_cart_produces_empty_receipt`, `test_comportamento_legado.py::test_cart_without_offers_sums_each_and_kilo_items` |
| RF02 | Oferta 3 por 2 | A cada 3 unidades, paga 2. 3 toothbrush -> desconto -0,99 com descrição `3 for 2`, total 1,98. 7 unidades -> desconto -1,98. Com 1 ou 2 unidades não há desconto | `test_comportamento_legado.py::test_three_for_two_offer` (1, 2, 3, 4, 6, 7 unidades), `test_comportamento_legado.py::test_same_product_added_multiple_times_aggregates_for_offer` |
| RF03 | Desconto percentual | Desconto = quantidade × preço × argumento / 100, descrição `<argumento>% off`. 10% em 2,5 kg de apples -> -0,4975, `10.0% off`. Vale para EACH e KILO e para argumento diferente de 10 | `test_comportamento_legado.py::test_ten_percent_discount_on_each_item`, `test_comportamento_legado.py::test_percentage_discount_on_kilo_with_argument_other_than_ten` |
| RF04 | Oferta 2 por valor | A cada 2 unidades, paga o valor da oferta. 2 cherry tomato box com "2 por 0,99" -> total 0,99, desconto -0,39, descrição `2 for 0.99`. 1 unidade -> sem desconto. Quantidade ímpar: comportamento do legado caracterizado (3 unidades -> 2,175) até o `fix:` da D6; depois dele, 3 unidades -> 1,68 | `test_comportamento_legado.py::test_two_for_amount_offer_even_and_single_quantities`, `test_comportamento_legado.py::test_two_for_amount_with_odd_quantity_charges_more_than_regular_price` |
| RF05 | Oferta 5 por valor | A cada 5 unidades, paga o valor da oferta. 5 toothpaste com "5 por 7,49" -> total 7,49, desconto -1,46, descrição `5 for 7.49`. 6 unidades -> total 9,28. 4 unidades -> sem desconto | `test_comportamento_legado.py::test_five_for_amount_offer` (4, 5, 6, 10, 11 unidades) |
| RF06 | Emitir recibo com itens, descontos e total | Cada inclusão no carrinho vira uma linha (produto, quantidade, preço unitário, total). Cada desconto mostra descrição e produto. Total = itens + descontos. O texto impresso pelo `ReceiptPrinter` (40 colunas, 2 casas decimais, 3 casas para KILO) é idêntico antes e depois da refatoração | `test_comportamento_legado.py::test_printed_receipt_matches_approved_output` + `tests/approved_files/` |
| RF07 | Combo promocional: 10% sobre os itens dos combos completos | 1 escova + 1 creme -> 10% sobre os dois: desconto total -0,278, total 2,502. Um `Discount` por produto do combo (D3). API: `teller.add_combo_offer(products, percent=10.0)` (D4) | `test_combos.py::test_one_full_combo_gets_ten_percent_off` |
| RF08 | Combo incompleto não recebe desconto | Só toothbrush no carrinho com combo toothbrush + toothpaste -> nenhum desconto, total 0,99 | `test_combos.py::test_incomplete_combo_has_no_discount` |
| RF09 | Vários combos e excedentes (D2) | Nº de combos = menor quantidade inteira entre os produtos. 2 escovas + 1 creme -> 1 combo (-0,278), a escova extra paga preço cheio (total 3,492). 2 + 2 -> 2 combos (-0,556, total 5,004) | `test_combos.py::test_extra_item_keeps_regular_price`, `test_combos.py::test_two_full_combos` |
| RF10 | Convivência com outras ofertas (D1) | Produto com oferta individual não entra no combo. Toothbrush com 10% + combo toothbrush/toothpaste -> só o desconto individual (-0,099), nenhum desconto de combo | `test_combos.py::test_product_with_individual_offer_is_not_in_combo` |
| RF11 | Uma oferta individual por produto | Cadastrar uma segunda oferta para o mesmo produto substitui a anterior (comportamento do legado, diagnóstico #6) | `test_comportamento_legado.py::test_second_offer_for_same_product_overwrites_first` |
| RF12 | Cada oferta afeta só o produto ofertado | Oferta para um produto que não foi comprado não altera o recibo. Ofertas em produtos diferentes no mesmo carrinho geram um desconto por produto, sem interferir entre si | `test_comportamento_legado.py::test_offer_for_product_not_in_cart_is_ignored`, `test_comportamento_legado.py::test_multiple_offers_on_different_products_in_same_cart` |

## 2. Requisitos não funcionais

| ID | Descrição | Critério verificável |
|----|-----------|----------------------|
| RNF01 | A API pública existente é preservada (D7) | Testes de caracterização passam sem alteração |
| RNF02 | Extensibilidade: nova promoção sem alterar as existentes | |
| RNF03 | Segurança: sem achados de severidade alta no Bandit e sem dependência vulnerável | |
| RNF04 | Reprodutibilidade | README permite rodar do zero |

## 3. Matriz de rastreabilidade
<!-- requisito -> implementação -> teste -> evidência -->
