# Supermarket Receipt: modernização de sistema legado

Trabalho prático de **Alta Qualidade de Software**: modernização incremental do
[SupermarketReceipt-Refactoring-Kata](https://github.com/emilybache/SupermarketReceipt-Refactoring-Kata)
(versão `python_pytest`, branch `main`).

O trabalho tem quatro frentes:
- testes de caracterização;
- refatoração com padrões de projeto (Strategy e Factory Method);
- nova regra de **combos promocionais** (10% sobre os combos completos);
- auditoria de segurança com Bandit, pip-audit e Safety, antes e depois.

> O código legado original está na tag **`v0-legado`**. Toda comparação "antes/depois" usa essa tag.

## Estrutura

```
.
├── src/                     código da aplicação (legado + refatorado)
│   ├── discount_strategy.py contrato comum das promoções (commit zero)
│   ├── combo_offer.py       estratégia do combo promocional (ComboOffer)
│   └── offers/              estratégias de desconto e fábrica (Strategy + Factory Method)
├── tests/
│   ├── conftest.py                  fixtures compartilhadas
│   ├── test_supermarket.py          teste original do kata
│   ├── test_comportamento_legado.py testes de caracterização
│   ├── test_combos.py               testes de aceitação dos combos
│   └── test_offer_strategies.py     testes unitários das estratégias
├── scripts/security_audit.py        roda Bandit, pip-audit e Safety e salva as evidências
├── docs/                            documentos de entrega em PDF
│   ├── diagnostico_tecnico.pdf
│   ├── requisitos.pdf
│   ├── plano_contingencia.pdf
│   ├── padroes_projeto.pdf
│   ├── seguranca_antes_depois.pdf
│   ├── evidencias_testes.pdf
│   ├── licoes_aprendidas.pdf
│   ├── evidencias/                  logs brutos (testes e segurança, antes/depois)
│   └── legado/
│       ├── README_original.md       README original do kata
│       └── mds/                     fontes em Markdown dos PDFs + divisao_tarefas.md
└── apresentacao/                    slides.pdf
```

Os documentos de entrega estão em PDF em `docs/`. As fontes em Markdown, usadas para gerar os PDFs, ficam em `docs/legado/mds/` (a pasta `legado/` guarda material de apoio, não o código legado, que está na tag `v0-legado`).

## Ambiente

- Python 3.10 ou mais recente (testes e evidências gerados com 3.11.9 e 3.12.10)
- Windows, Linux ou macOS

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

python -m pip install -r requirements.txt       # aplicação + testes
python -m pip install -r requirements-dev.txt   # ferramentas de segurança
```

## Testes

```bash
python -m pytest                     # todos os testes
python -m pytest -v tests/test_combos.py
python -m coverage run -m pytest && python -m coverage report
```

Resultado esperado: **57 testes passando**, sem `xfail` (caracterização, unidade das estratégias e combos), com cobertura de 99% em `src/`.

Para rodar os testes de caracterização no código legado:

```bash
git checkout v0-legado -- src && python -m pytest tests/test_comportamento_legado.py
git checkout HEAD -- src
```

## Combos promocionais

Regra nova: comprando todos os produtos de um combo, o cliente ganha 10% de desconto sobre os itens que formam combos completos.

```python
teller.add_combo_offer([toothbrush, toothpaste])            # 10% por padrão
teller.add_combo_offer([toothbrush, toothpaste], percent=15.0)
```

- **Combos completos (D2):** o número de combos é a menor quantidade inteira entre os produtos; o excedente paga preço normal. Ex.: 2 escovas + 1 creme = 1 combo.
- **Um desconto por produto (D3):** cada produto do combo gera uma linha `combo 10% off` no recibo.
- **Convivência com outras ofertas (D1):** produto que já tem oferta individual não entra no combo, e cada unidade consumida por um combo é abatida antes de avaliar os demais combos, para não haver desconto duplicado.
- **Extensibilidade:** `ComboOffer` implementa o mesmo contrato `DiscountStrategy` e foi adicionado sem alterar nenhuma estratégia existente (RNF02).

Requisitos RF07–RF10 em [docs/requisitos.pdf](docs/requisitos.pdf); testes em `tests/test_combos.py`.

## Segurança

```bash
python scripts/security_audit.py antes    # ou: depois
```

As saídas ficam em `docs/evidencias/seguranca/<etapa>/`. O `safety scan` exige uma conta Safety. Sem login, o script registra essa limitação e tenta o modo legado `safety check`. A análise completa está em [docs/seguranca_antes_depois.pdf](docs/seguranca_antes_depois.pdf).

Resultado da auditoria, antes (legado) e depois (refatoração + combos):

| Ferramenta | Antes | Depois |
|------------|-------|--------|
| Bandit em `src/` (High / Medium / Low) | 0 / 0 / 0 em 149 linhas | 0 / 0 / 0 em 344 linhas |
| pip-audit (`requirements.txt`) | nenhuma vulnerabilidade | nenhuma vulnerabilidade |
| Safety (85 dependências) | 0 ativas, 26 ignoradas pela política | 0 ativas, 26 ignoradas pela política |

O código cresceu (novas estratégias e o combo) sem introduzir nenhum achado, e nenhuma dependência nova foi adicionada. Os 26 itens do Safety são do ambiente de desenvolvimento e estão triados no documento (RNF03 atendido).

## Análise do legado

Documentos da análise feita antes de qualquer mudança no código (base: tag `v0-legado`):

- [Diagnóstico técnico](docs/diagnostico_tecnico.pdf): 15 problemas com arquivo e linha, métricas (radon e coverage) e prioridades.
- [Requisitos](docs/requisitos.pdf): RF01–RF12 e RNF01–RNF07, com critérios de aceitação e matriz de rastreabilidade.
- [Plano de contingência](docs/plano_contingencia.pdf): sequência das etapas, invariantes, riscos e estratégia de reversão.

Resumo: toda a regra de promoções está em `ShoppingCart.handle_offers` (complexidade ciclomática 13), que no legado não era executada por nenhum teste (cobertura de 41% em `shopping_cart.py`). Por isso a ordem é: caracterizar, refatorar, estender (combos) e só então corrigir o bug do `TWO_FOR_AMOUNT`.

## Como o time trabalha

Divisão de tarefas, quem é dono de cada arquivo, ordem de merge e decisões de negócio: [docs/legado/mds/divisao_tarefas.md](docs/legado/mds/divisao_tarefas.md).

Commits pequenos, em inglês, no formato `tipo: descrição` (`feat`, `fix`, `docs`, `test`, `build`, `refactor`, `chore`, `security`, ...).

## Decisões arquiteturais

O cálculo de ofertas saiu de um único método com uma cadeia de `if`s
(`ShoppingCart.handle_offers`, complexidade 13) para **uma classe por
modalidade de oferta**. Detalhes, diagramas antes/depois e testes
relacionados: [docs/padroes_projeto.pdf](docs/padroes_projeto.pdf).

| Padrão | Onde | Problema que resolve |
|--------|------|----------------------|
| **Strategy** | `src/offers/` (`ThreeForTwoStrategy`, `PercentageDiscountStrategy`, `TwoForAmountStrategy`, `FiveForAmountStrategy`) | Cada regra de desconto fica isolada numa classe que implementa o contrato `DiscountStrategy` e pode ser testada sozinha. |
| **Factory Method** | `src/offers/factory.py` (`DiscountStrategyFactory`) | Concentra a escolha da estratégia pelo `SpecialOfferType`, eliminando os `if`s sobre o tipo de oferta. |
| **Template Method** | `src/offers/single_product_offer.py` (`SingleProductOfferStrategy`) | Reúne os passos comuns das ofertas de um produto; cada oferta implementa só o cálculo do desconto. |

Decisões que guiaram a refatoração:

- **API pública preservada (D7):** `Teller`, `ShoppingCart.handle_offers`,
  `Receipt` e demais classes mantêm nomes e assinaturas; os testes de
  caracterização passam sem alteração.
- **Comportamento idêntico ao legado:** as fórmulas mantêm a ordem de
  operações original. O bug do `TWO_FOR_AMOUNT` foi preservado durante a
  refatoração e corrigido depois num commit `fix:` separado (D6): com 3
  unidades, o total passou de 2,175 para 1,68 (ver
  [docs/padroes_projeto.pdf](docs/padroes_projeto.pdf), seção 7).
- **Extensível (SOLID):** uma nova promoção é uma nova classe; o carrinho
  depende só da abstração `DiscountStrategy`.

| Métrica | Legado (`v0-legado`) | Após a refatoração | Final (com combos) | Meta |
|---------|----------------------|--------------------|--------------------|------|
| Complexidade de `handle_offers` (radon) | 13 (C) | 5 (A) | 5 (A) | ≤ 10 (RNF06) |
| Maior complexidade em `src/` | 13 (C) | 5 (A) | 8 (B) | ≤ 10 (RNF06) |
| Cobertura de `src/` | 71% | 98% | 99% | ≥ 90% (RNF05) |
| Testes passando | 1 | 44 (+ 5 `xfail`) | 57 | — |
| "2 por 0,99" com 3 unidades | 2,175 (bug) | 1,68 | 1,68 | — |

## Evidências e lições aprendidas

- [Evidências de testes](docs/evidencias_testes.pdf): execução no legado, após a refatoração e final (57 testes), com comparativo e cobertura. Logs brutos em `docs/evidencias/testes/`.
- [Segurança antes/depois](docs/seguranca_antes_depois.pdf): triagem dos achados e comparação. Logs brutos em `docs/evidencias/seguranca/`.
- [Lições aprendidas](docs/licoes_aprendidas.pdf): processo do time, lições de cada frente (análise, testes, refatoração, combos e segurança), o que faríamos diferente e resultado final.

## Licença

Código-base: MIT, © 2018 Emily Bache (ver [license.txt](license.txt)).
