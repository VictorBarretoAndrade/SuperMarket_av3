# Evidências de testes

> Dono: **P2** · Enunciado: Passos 2, 6 e 10 e itens 5.7 e 5.9 · Barema: 1,0 + 0,5

Logs brutos: `docs/evidencias/testes/`.

## 1. Execução inicial (Passo 2)

- **Ambiente**: Python `3.12.10` em `.venv` (`pytest==9.2.0`, `approvaltests==21.1.0`, `pytest-approvaltests==0.2.4`, `coverage==7.17.5`). Lista completa de pacotes em [ambiente.txt](evidencias/testes/ambiente.txt).
- **Comandos executados na tag `v0-legado`**:

```bash
git checkout v0-legado -- src
python -m pytest -v tests/test_supermarket.py
git checkout HEAD -- src
```

- **Resultado observado** ([execucao_inicial_v0_legado.txt](evidencias/testes/execucao_inicial_v0_legado.txt)):
  - `1 passed in 0.02s` (`test_supermarket.py::test_ten_percent_discount`).
  - O legado possuía apenas 1 teste unitário cobrindo um carrinho com maçãs sem oferta aplicada e uma oferta não utilizada em `toothbrush`.

## 2. Testes de caracterização: rodando na tag `v0-legado`

Foram implementados em `tests/test_comportamento_legado.py` **24 casos de teste** cobrindo todos os cenários do checklist da P2 usando exclusivamente a API pública (`Teller`, `ShoppingCart`, `Receipt`, `ReceiptPrinter` e `approvaltests`):

- Carrinho vazio e carrinho sem ofertas (`EACH` e `KILO`);
- Mesmo produto adicionado várias vezes via `add_item` e `add_item_quantity`;
- `THREE_FOR_TWO` (1, 2, 3, 4, 6 e 7 unidades);
- `TEN_PERCENT_DISCOUNT` (`EACH` e `KILO`, com argumento `10.0` e `20.0`);
- `TWO_FOR_AMOUNT` (1, 2, 4 unidades e o comportamento legado com bug em 3 unidades);
- `FIVE_FOR_AMOUNT` (4, 5, 6, 10 e 11 unidades);
- Oferta para produto ausente no carrinho, sobrescrita de oferta no mesmo produto e múltiplas ofertas simultâneas;
- Recibo completo formatado pelo `ReceiptPrinter` validado com `approvaltests` ([arquivo aprovado](../../tests/approved_files/test_comportamento_legado.test_printed_receipt_matches_approved_output.approved.txt)).

- **Comandos executados contra `v0-legado`**:

```bash
git checkout v0-legado -- src
python -m pytest -v tests/test_comportamento_legado.py
git checkout HEAD -- src
```

- **Resultado observado** ([caracterizacao_v0_legado.txt](evidencias/testes/caracterizacao_v0_legado.txt)):
  - `24 passed in 0.07s`.

- **Execução completa na branch `test/caracterizacao`** (`python -m pytest -v`, [pytest_atual.txt](evidencias/testes/pytest_atual.txt)):
  - `25 passed, 5 xfailed in 0.19s` (`1` teste original + `24` de caracterização passando; `5` testes de aceitação de combos em `tests/test_combos.py` permanecem como `xfail` esperado até a entrega da P4).

## 3. Testes após a refatoração e os combos

Após os merges da refatoração (P3, Strategy + Factory Method + Template Method), dos combos promocionais (P4) e da correção de `TWO_FOR_AMOUNT`, toda a suíte executou sem nenhuma falha nem `xfail`.

- **Comando**: `python -m pytest -v` (na branch `development`, Python `3.12.10` em `.venv`).
- **Resultado observado** ([pytest_final.txt](evidencias/testes/pytest_final.txt)): **`55 passed in 0.52s`** (`0 failed`, `0 xfailed`):
  - `tests/test_supermarket.py`: `1 passed`
  - `tests/test_comportamento_legado.py`: `24 passed`
  - `tests/test_offer_strategies.py`: `19 passed`
  - `tests/test_combos.py`: `11 passed`

### Correção do bug `TWO_FOR_AMOUNT` (P3, decisão D6)

- **Comando**: `python -m pytest -v`, após o commit `fix:` (Python `3.11.9` em `.venv`).
- **Resultado** ([pytest_pos_fix_two_for_amount.txt](evidencias/testes/pytest_pos_fix_two_for_amount.txt)): `44 passed, 5 xfailed`.
- **Mudança intencional** (única exceção prevista no RNF01): o teste que caracterizava o bug foi atualizado no mesmo commit `fix:`.

| Teste | Antes (legado) | Depois do `fix:` |
|-------|----------------|------------------|
| `test_two_for_amount_with_odd_quantity_charges_more_than_regular_price` -> renomeado para `test_two_for_amount_with_odd_quantity_charges_leftover_at_regular_price` | desconto `+0,105`, total `2,175` | desconto `-0,39`, total `1,68` |

Justificativa e trecho antes/depois: [padroes_projeto.md, seção 7](padroes_projeto.md). Os demais testes de caracterização e o recibo aprovado não mudaram.

## 4. Comparativo antes/depois

| Suíte | `v0-legado` (inicial) | `test/caracterizacao` (baseline P2) | Final (pós P3 + P4) |
|-------|-----------------------|-------------------------------------|---------------------|
| `tests/test_supermarket.py` | 1 passed | 1 passed | 1 passed |
| `tests/test_comportamento_legado.py` | — (não existia na tag; 24 passed ao rodar contra `v0-legado`) | 24 passed | 24 passed |
| `tests/test_offer_strategies.py` | — | — | 19 passed |
| `tests/test_combos.py` | — | 5 xfailed (esperado) | 11 passed |
| **Total** | **1 passed** | **25 passed, 5 xfailed** | **55 passed** |

## 5. Cobertura

### Baseline (`test/caracterizacao`, antes da refatoração e combos)

Comandos executados na branch `test/caracterizacao`:

```bash
python -m coverage run --source=src -m pytest
python -m coverage report -m
```

- **Cobertura em `src/`** ([cobertura_baseline.txt](evidencias/testes/cobertura_baseline.txt)):
  - `src/model_objects.py`: `100%` (27/27)
  - `src/receipt.py`: `100%` (27/27)
  - `src/shopping_cart.py`: `98%` (48/49; apenas a property `product_quantities` na linha 21 não foi acessada externamente)
  - `src/teller.py`: `95%` (20/21; apenas `product_with_name` na linha 29)
  - `src/catalog.py`: `60%` (3/5; métodos base abstratos que lançam exceção)
  - `src/discount_strategy.py`: `0%` (0/4; contrato criado no commit zero, ainda sem implementações concretas antes da P3/P4)
  - **Total em `src/`**: **94%** (`133` declarações, `8` não cobertas).

- **Cobertura executando `python -m coverage run -m pytest && python -m coverage report`** ([cobertura_completa.txt](evidencias/testes/cobertura_completa.txt)):
  - **Total geral (`src/` + `tests/`)**: **93%** (`402` declarações, `29` não cobertas), com `100%` em `tests/receipt_printer.py` e `tests/test_comportamento_legado.py`.

### Final (`development`, pós P3 + P4)

Comandos executados na branch `development`:

```bash
python -m coverage run --source=src -m pytest
python -m coverage report -m
```

- **Cobertura em `src/`** ([cobertura_final_src.txt](evidencias/testes/cobertura_final_src.txt)):
  - `src/combo_offer.py`: `100%` (19/19)
  - `src/discount_strategy.py`: `100%` (4/4)
  - `src/model_objects.py`: `100%` (27/27)
  - `src/offers/__init__.py`: `100%` (0/0)
  - `src/offers/factory.py`: `100%` (13/13)
  - `src/offers/five_for_amount.py`: `100%` (12/12)
  - `src/offers/percentage_discount.py`: `100%` (5/5)
  - `src/offers/single_product_offer.py`: `100%` (20/20)
  - `src/offers/three_for_two.py`: `100%` (13/13)
  - `src/offers/two_for_amount.py`: `100%` (12/12)
  - `src/receipt.py`: `100%` (27/27)
  - `src/shopping_cart.py`: `100%` (26/26)
  - `src/teller.py`: `97%` (28/29; apenas `product_with_name` na linha 45)
  - `src/catalog.py`: `60%` (3/5; métodos base abstratos que lançam exceção)
  - **Total em `src/`**: **99%** (`212` declarações, `3` não cobertas).

- **Cobertura completa (`python -m coverage run -m pytest && python -m coverage report`)** ([cobertura_final_completa.txt](evidencias/testes/cobertura_final_completa.txt)):
  - **Total geral (`src/` + `tests/`)**: **99%** (`593` declarações, `3` não cobertas — `100%` em todos os arquivos de `tests/`).
