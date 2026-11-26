# Divisão de tarefas e decisões do commit zero

Objetivo: permitir que os 4 integrantes trabalhem **em paralelo desde o primeiro dia**.
O que sobra de dependência é a **ordem de merge** no `main` e dois passos curtos no fechamento.

## 1. Decisões do commit zero

| ID | Decisão | Onde está |
|----|---------|-----------|
| D1 | Um produto que já tem **oferta individual não participa de combo** (sem desconto duplicado no mesmo item). | `tests/test_combos.py` |
| D2 | **Nº de combos = menor quantidade inteira** entre os produtos do combo. O excedente paga o preço normal. | `tests/test_combos.py` |
| D3 | O desconto do combo gera **um `Discount` por produto** do combo (10% sobre as unidades que entram nos combos completos). Assim `Receipt` e `ReceiptPrinter` não mudam. | contrato |
| D4 | API pública do combo: `teller.add_combo_offer(products, percent=10.0)`. | contrato |
| D5 | Interface comum `DiscountStrategy.calculate(product_quantities, catalog) -> list[Discount]`. | `src/discount_strategy.py` |
| D6 | O bug de `TWO_FOR_AMOUNT` com quantidade ímpar é **caracterizado como está**. A refatoração o preserva, e a correção vem depois num commit `fix:` separado, com o teste atualizado e a justificativa em `docs/`. | `tests/test_comportamento_legado.py` |
| D7 | A API pública existente não muda: `Teller`, `ShoppingCart` (inclusive `handle_offers`), `Receipt`, `ReceiptItem`, `Discount`, `Offer`, `SpecialOfferType`. | `docs/plano_contingencia.md` |

> Para mudar uma decisão, o time inteiro precisa concordar, e esta tabela é atualizada no mesmo PR.

## 2. Responsabilidades

| | **P1: Analista** | **P2: Testes** | **P3: Refatoração** | **P4: Combos + Segurança** |
|---|---|---|---|---|
| **Entregáveis** | Diagnóstico técnico, Requisitos RF/RNF, Plano de contingência, README final, montagem dos slides | Testes de caracterização, aprovação do recibo (approvaltests), cobertura, evidências antes/depois | Strategy + Factory Method substituindo os `if`s de `handle_offers`; documento de padrões com diagrama antes/depois | Combo (Strategy própria), testes de combo, Bandit/pip-audit/Safety antes e depois |
| **Barema** | 1,0 + 1,0 + 0,5 + 0,5 | 1,0 + 0,5 | 2,0 + 2,0 | 0,5 + 1,0 |
| **Arquivos que só essa pessoa altera** | `docs/diagnostico_tecnico.md`, `docs/requisitos.md`, `docs/plano_contingencia.md`, `README.md`, `apresentacao/` | `tests/test_comportamento_legado.py`, `tests/approved_files/`, `docs/evidencias_testes.md`, `docs/evidencias/testes/` | `src/shopping_cart.py`, `src/offers/` (novo), `docs/padroes_projeto.md` | `src/teller.py`, `src/combo_offer.py` (novo), `tests/test_combos.py`, `docs/seguranca_antes_depois.md`, `docs/evidencias/seguranca/` |
| **Depende de alguém?** | Não. Trabalha lendo o código legado | Não. Testa só a API pública | Pode começar já. O merge só entra depois dos testes da P2 | Não. Trabalha em cima do contrato D1–D5 |

**Arquivos compartilhados** (`tests/conftest.py`, `src/discount_strategy.py`, `src/model_objects.py`): só recebem **adições**, nunca alterações no que já existe.

Cada integrante também escreve **2–3 slides** e a seção da sua parte no README.

## 3. Ordem de merge no `main`

```
1. init + commit zero (feito)           -> tag v0-legado
2. P4: segurança "antes"   |  P1: diagnóstico, requisitos, plano (1ª versão)
3. P2: testes de caracterização         <- prioridade: entrar nos primeiros dias
4. P3: refatoração                      (precisa passar nos testes da P2)
5. P4: combos                           (precisa passar nos testes da P2 + nos de combo)
6. P3: fix do bug TWO_FOR_AMOUNT        (commit separado, D6)
7. Fechamento: P4 segurança "depois", P2 evidências "depois", P1 README final + slides
```

## 4. Fluxo de trabalho

- Uma branch por integrante: `docs/analise`, `test/caracterizacao`, `refactor/strategy`, `feat/combos`.
- Commits pequenos, **em inglês**, no padrão `tipo: descrição` (`feat`, `fix`, `docs`, `test`, `build`, `perf`, `style`, `refactor`, `chore`, `ci`, `raw`, `cleanup`, `remove`, `init`, `revert`, `security`).
- Antes de qualquer merge: `python -m pytest` precisa passar (o `xfail` dos combos é esperado até a P4 entregar).
- Se acontecer uma regressão: `git revert <commit>` (nunca `push --force` no `main`). A tag `v0-legado` é sempre o ponto de comparação.
