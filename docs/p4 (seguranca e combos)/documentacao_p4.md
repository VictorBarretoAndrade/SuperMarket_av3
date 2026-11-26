processo:

testes de segurança antes: (Bandit, pip-audit e Safety)
Codagem dos combos
Testes dos combos
testes de segurança depois: (Bandit, pip-audit e Safety)

Bandit
pra que:  Verifica pacotes instalados ou arquivos de dependências (requirements.txt, pyproject.toml) contra bases de vulnerabilidades (como OSV e PyPA Advisory Database) e aponta versões corrigidas.
uso:
bandit -r meu_projeto/


pip-audit
pra que: Audita bibliotecas de terceiros em busca de CVEs conhecidas e sugere correções.
uso:
pip-audit

Safety
pra que:  Audita bibliotecas de terceiros em busca de CVEs conhecidas e sugere correções.
uso:
safety check

---

## Análise dos achados ignorados no Safety (etapa `antes`)

Na execução inicial (`python -m safety scan`, registrada em `docs/evidencias/seguranca/antes/safety.txt`), o Safety reportou:

> `26 vulnerabilities found, 26 ignored due to policy.`

Para não aceitar o filtro padrão sem verificação, foi realizada a inspeção detalhada via `python -m safety scan --output json` e cruzamento com `pip-audit` no `.venv`. As 26 vulnerabilidades ignoradas se dividem em dois grupos:

1. **`requirements.txt` — 1 vulnerabilidade ignorada (`unpinned-specification`)**
   - **Pacote:** `pytest` (`SFTY-20260122-20373`).
   - **Motivo:** `requirements.txt` declara `pytest` sem versão fixa. A política padrão do Safety (`ignore-unpinned-requirements: True`) ignora alertas gerados por especificações sem versão pinada.
   - **Relevância:** Nula no ambiente atual (`pytest==9.2.0` instalado no `.venv` não possui vulnerabilidades conhecidas, conforme confirmado pelo `pip-audit`). Ainda assim, fixar as versões em `requirements.txt` é recomendável para reprodutibilidade e eliminação do alerta.

2. **`.venv\pyvenv.cfg` — 25 vulnerabilidades ignoradas (`environment-dependency`)**
   - **Motivo:** Na política padrão (`Stage.development`), o Safety ignora vulnerabilidades detectadas diretamente no ambiente virtual (`.venv`), priorizando os manifestos do projeto.
   - **Pacotes envolvidos (nenhum usado em tempo de execução pela aplicação):**
     - `filelock==3.32.7` (13 vulnerabilidades): dependência exclusiva do próprio `safety` (`Required-by: safety`).
     - `pip==24.0` (7 vulnerabilidades): instalador padrão do `.venv` (também requerido pelo `pip-audit` via `pip_api`).
     - `setuptools==65.5.0` (5 vulnerabilidades): ferramenta padrão de empacotamento criada junto com o `.venv` do Python 3.11.

### Conclusão e ações
- **Impacto na aplicação:** Nenhum. O código de produção utiliza apenas a biblioteca padrão do Python, e as dependências de teste instaladas estão limpas.
- **Alteração de política:** Não é necessário alterar a política padrão do Safety (`.safety-policy.yml`); a inspeção pontual com `--output json` é suficiente para auditoria.
- **Melhorias opcionais de higiene do ambiente:**
  - Fixar as versões das dependências em `requirements.txt` (`pytest==9.2.0`, `approvaltests==21.1.0`, `pytest-approvaltests==0.2.4`, `coverage==7.17.5`).
  - Atualizar `pip` e `setuptools` no `.venv` (`python -m pip install --upgrade pip setuptools`), eliminando 12 das 25 vulnerabilidades de ambiente (restando apenas `filelock`, trazido pelo próprio `safety`).

---

## Implementação dos combos (decisões do commit zero — D1 a D7)

### O que foi visto antes da alteração
- `src/discount_strategy.py` já definia a interface abstrata `DiscountStrategy.calculate(product_quantities, catalog) -> list[Discount]` (D5).
- `src/teller.py` cadastrava apenas ofertas individuais (`self.offers` via `add_special_offer`) e delegava o cálculo delas para `the_cart.handle_offers(...)`.
- `src/shopping_cart.py` pertence à P3 (refatoração) e concentra as ofertas legadas (incluindo o bug caracterizado de `TWO_FOR_AMOUNT`, D6), portanto não foi alterado.
- `tests/test_combos.py` tinha 5 testes de aceitação marcados com `pytestmark = pytest.mark.xfail(raises=AttributeError, ...)` aguardando `teller.add_combo_offer`.
- Os testes de caracterização da P2 (`tests/test_comportamento_legado.py`, incluindo o recibo aprovado via `approvaltests`) já estavam integrados na branch.

### Estratégia adotada
- **Padrão Strategy isolado (`src/combo_offer.py`):** criar `ComboOffer(DiscountStrategy)` sem tocar em `ShoppingCart`, `Receipt` ou `ReceiptPrinter` (respeitando D3, D5, D6 e D7 e evitando conflito com a branch da P3).
- **Filtro de elegibilidade no checkout (D1):** em `Teller.checks_out_articles_from`, montar `eligible_quantities` excluindo qualquer produto presente em `self.offers`. Fazer esse filtro no checkout garante que a regra funciona independentemente da ordem em que `add_special_offer` e `add_combo_offer` foram chamados.
- **Quantidade inteira mínima (D2):** calcular `num_combos = min(int(product_quantities.get(p, 0)) for p in self.products)`. Se algum item faltar ou tiver quantidade menor que 1, nenhum desconto é gerado; unidades ou frações excedentes permanecem com preço normal.
- **Um `Discount` por produto (D3):** para cada produto do combo, gerar `Discount(product, description, -num_combos * unit_price * (percent / 100.0))`. Assim o total do recibo e a impressão pelo `ReceiptPrinter` funcionam sem qualquer alteração nessas classes.
- **Proteção contra entradas de borda:** deduplicar a lista de produtos recebida (`dict.fromkeys`) e retornar lista vazia quando a lista de produtos for vazia ou `percent <= 0`.

### O que foi alterado
1. **`src/combo_offer.py` (criado):** classe `ComboOffer(DiscountStrategy)` implementando `calculate(product_quantities, catalog)` conforme D2, D3 e D5.
2. **`src/teller.py` (alterado):**
   - adicionado `self.combo_offers = []` no `__init__`;
   - adicionado método público `add_combo_offer(self, products, percent=10.0)` (D4);
   - em `checks_out_articles_from`, filtrado `the_cart.product_quantities` removendo itens de `self.offers` (D1) e aplicados os descontos retornados por cada `ComboOffer`.
3. **`tests/test_combos.py` (alterado):**
   - removido o marcador `pytestmark = pytest.mark.xfail(...)`;
   - mantidos os 5 testes de aceitação originais e adicionados 6 testes extras cobrindo D3 (1 `Discount` por produto + `ReceiptPrinter`), D4 (percentual customizado), D1 com ordem inversa de cadastro, D2 com quantidade fracionária (`KILO`), combo com 3 produtos e combo vazio.

### Resultado dos testes
Execução de `python -m pytest -v`: **36 passed, 0 failed** (11 testes de combo em `tests/test_combos.py`, 24 testes de caracterização/aprovação da P2 em `tests/test_comportamento_legado.py` e 1 teste legado em `tests/test_supermarket.py`).

