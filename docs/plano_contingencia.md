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

| ID | Risco | Probabilidade | Impacto | Prevenção | Teste associado | Reversão |
|----|-------|---------------|---------|-----------|-----------------|----------|
| R1 | Refatoração altera algum valor de desconto | Média | Alto | Testes de caracterização antes (E2), cobrindo todos os ramos de `handle_offers`; refatorar uma oferta por commit | `test_comportamento_legado.py` (caracterização + recibo aprovado) | `git revert` do commit da oferta que quebrou |
| R2 | Combo gera desconto duplicado com outra oferta | Média | Alto | Decisão D1 + teste específico | `test_combos.py::test_product_with_individual_offer_is_not_in_combo` | `git revert` do merge de `feat/combos` |
| R3 | Refatoração "corrige sem querer" o bug do `TWO_FOR_AMOUNT` (ex.: troca `/` por `//`) | Alta | Médio | D6: o teste de caracterização trava o valor 2,175 até o commit `fix:` | `test_two_for_amount_with_odd_quantity_charges_more_than_regular_price` | Reverter o commit e reaplicar a correção só em E5 |
| R4 | Mudança no texto ou formato do recibo | Média | Médio | Recibo aprovado com approvaltests antes da refatoração | `test_comportamento_legado.py` + `tests/approved_files/` | `git revert`; nunca reaprovar o arquivo sem acordo do time |
| R5 | Quebra da API pública (renomear método, mudar assinatura) | Baixa | Alto | D7; os testes usam só a API pública; revisão no PR | Todas as suítes | `git revert` |
| R6 | Conflito de merge entre as branches de P3 e P4 | Média | Médio | Contrato `DiscountStrategy` fixo desde o commit zero; donos de arquivo; arquivos compartilhados só recebem adições | `python -m pytest` após o merge | Desfazer o merge (`git revert -m 1`) e refazer a integração |
| R7 | Produto `KILO` com quantidade fracionada muda de valor (diagnóstico #4) | Média | Médio | Caracterizar 3 por 2 / 5 por valor com quantidade fracionada antes de refatorar | `test_percentage_discount_on_kilo_with_argument_other_than_ten`; falta cenário de 3 por 2 com quantidade fracionada (pedir à P2) | `git revert` |
| R8 | Dependência com vulnerabilidade conhecida | Média | Médio | Auditoria antes e depois (Bandit, pip-audit, Safety) | `scripts/security_audit.py` | Fixar versão segura em `requirements.txt` |
| R9 | Atraso de um integrante bloqueia a entrega | Média | Alto | Trabalho paralelo desde o início (seção 2 de `divisao_tarefas.md`); só o merge tem ordem | — | Outro integrante assume a etapa a partir da branch publicada |

## 4. Estratégia de reversão
<!-- tag v0-legado, uma branch por mudança, git revert, nada de push --force -->

## 5. Critérios de aceitação de cada etapa
