# Plano de contingência e refatoração

> Dono: **P1** · Enunciado: Passo 5 e item 5.3 · Barema: 0,5 (ausência: -3,0)
> Precisa ser commitado **antes** da refatoração (ordem no git).

## 1. Sequência das mudanças

A ordem segue `docs/divisao_tarefas.md`, seção 3. Cada etapa só entra no `main` quando `python -m pytest` passa.

| Etapa | Responsável | Branch | O que entra | Pré-requisito |
|-------|-------------|--------|-------------|---------------|
| E0 | time | `main` | Código legado + commit zero (contrato `DiscountStrategy`, fixtures, testes de combo como `xfail`) | — (tag `v0-legado`) |
| E1 | P1 / P4 | `docs/analise`, `feat/combos` | Diagnóstico, requisitos, este plano; auditoria de segurança "antes" | E0 |
| E2 | P2 | `test/caracterizacao` | Testes de caracterização + recibo aprovado (approvaltests) | E0 |
| E3 | P3 | `refactor/strategy` | Strategy + Factory Method no lugar dos `if`s de `handle_offers` | E1 (este plano) e E2 |
| E4 | P4 | `feat/combos` | Combo como nova estratégia; remove o `xfail` de `test_combos.py` | E2 e E3 |
| E5 | P3 | `refactor/strategy` | `fix:` do bug `TWO_FOR_AMOUNT` com quantidade ímpar (D6) | E3 |
| E6 | P1 / P2 / P4 | todas | Segurança "depois", evidências "depois", README final e slides | E4 e E5 |

Regras da sequência:

- refatoração (E3) e correção de bug (E5) **nunca no mesmo commit**: a refatoração preserva o comportamento, inclusive o bug;
- cada etapa é pequena o bastante para ser revertida sozinha;
- nenhuma etapa altera os arquivos de outro integrante (ver dono de cada arquivo em `docs/divisao_tarefas.md`).

## 2. Invariantes de negócio e interfaces que não podem mudar

**Interfaces públicas (D7).** Nomes, parâmetros e retorno permanecem iguais:

| Classe | Membros preservados |
|--------|---------------------|
| `Teller` | `Teller(catalog)`, `add_special_offer(offer_type, product, argument)`, `checks_out_articles_from(cart) -> Receipt`, `product_with_name(name)` |
| `ShoppingCart` | `add_item(product)`, `add_item_quantity(product, quantity)`, `items`, `product_quantities`, `handle_offers(receipt, offers, catalog)` |
| `Receipt` / `ReceiptItem` | `total_price()`, `add_product(...)`, `add_discount(...)`, `items`, `discounts`; atributos `product`, `quantity`, `price`, `total_price` |
| `Discount`, `Offer`, `Product`, `ProductQuantity` | construtores e atributos atuais |
| `SpecialOfferType`, `ProductUnit` | membros e valores atuais |
| `SupermarketCatalog` | `add_product(product, price)`, `unit_price(product)` |

A nova API do combo (`teller.add_combo_offer(products, percent=10.0)`, D4) é **adição**, não alteração.

**Invariantes de negócio:**

1. O valor de cada desconto é o mesmo do legado para qualquer carrinho (exceto o caso corrigido pela D6, após E5).
2. Descontos são valores **negativos** e `Receipt.total_price() = Σ itens + Σ descontos`.
3. O texto das descrições (`3 for 2`, `10.0% off`, `2 for 0.99`, `5 for 7.49`) e a formatação do recibo impresso não mudam.
4. A ordem das linhas do recibo continua sendo a ordem de inclusão no carrinho.
5. Uma oferta individual por produto; a última cadastrada vale (RF11).
6. Produto com oferta individual não entra em combo (D1).
7. Nº de combos = menor quantidade inteira entre os produtos do combo (D2); o excedente paga preço normal.

## 3. Riscos

| Risco | Probabilidade | Impacto | Prevenção | Teste associado | Reversão |
|-------|---------------|---------|-----------|-----------------|----------|
| Refatoração altera algum valor de desconto | | Alto | Testes de caracterização antes | | `git revert` |
| Combo gera desconto duplicado com outra oferta | | | Decisão D1 + teste | | |

## 4. Estratégia de reversão
<!-- tag v0-legado, uma branch por mudança, git revert, nada de push --force -->

## 5. Critérios de aceitação de cada etapa
