# Análise de segurança: Bandit, pip-audit e Safety

> Dono: **P4** · Enunciado: Passos 7 e 11 e item 5.8 · Barema: 1,0

Evidências brutas: `docs/evidencias/seguranca/antes/` e `docs/evidencias/seguranca/depois/`, geradas por `python scripts/security_audit.py antes|depois`.

## 1. Ambiente e versões

Ambas as execuções (`antes` e `depois`) foram realizadas no mesmo ambiente virtual e com as mesmas versões de ferramentas:

| Item | Etapa `antes` | Etapa `depois` |
|------|---------------|----------------|
| Data/hora | `2026-11-25T17:21:17` | `2026-11-25T23:22:26` |
| Commit | `2ae7e3d` | `e55ff79` |
| Python | `3.11.9` | `3.11.9` |
| Sistema operacional | `Windows-10-10.0.26200-SP0` | `Windows-10-10.0.26200-SP0` |
| Bandit | `1.9.4` | `1.9.4` |
| pip-audit | `2.10.1` | `2.10.1` |
| Safety | `3.8.1` | `3.8.1` |

> Fontes: `docs/evidencias/seguranca/antes/ambiente.txt` e `docs/evidencias/seguranca/depois/ambiente.txt`.

## 2. Escopo e comandos

| Ferramenta | O que analisa | Comando |
|------------|---------------|---------|
| Bandit | Código-fonte de `src/` (análise estática) | `python -m bandit -r src` |
| pip-audit | Dependências de `requirements.txt` (base PyPA/OSV) | `python -m pip_audit -r requirements.txt --desc` |
| Safety | Dependências (base Safety DB) | `python -m safety scan` (exige login) / `safety check -r requirements.txt` (depreciado) |

## 3. Linha de base (antes)

Executada antes da refatoração (P3) e da implementação dos combos (P4), no commit `2ae7e3d` (`docs/evidencias/seguranca/antes/`):

- **Bandit (`bandit.txt` / `bandit.json`):** `exit code: 0`, **0 alertas** (`High: 0`, `Medium: 0`, `Low: 0`, `Undefined: 0`), `0` supressões `#nosec` e `0` arquivos pulados. Escopo analisado: **149 linhas de código** em **6 arquivos** (`catalog.py`, `discount_strategy.py`, `model_objects.py`, `receipt.py`, `shopping_cart.py` e `teller.py`).
- **pip-audit (`pip-audit.txt`):** `exit code: 0`, `No known vulnerabilities found` para as dependências declaradas em `requirements.txt` (`pytest`, `approvaltests`, `pytest-approvaltests`, `coverage`).
- **Safety (`safety.txt`):** `exit code: 0`, **85 dependências** testadas (`requirements.txt`, `.venv\pyvenv.cfg` e 2 `pyproject.toml` de exemplo do pacote `stevedore` no `.venv`). Resultado: **26 vulnerabilidades encontradas, 26 ignoradas pela política padrão** (`Stage.development`), triadas na seção 4.

## 4. Triagem dos achados

| Ferramenta | Achado | Severidade | Relevante? | Ação / justificativa |
|------------|--------|------------|------------|----------------------|
| Bandit | Nenhum achado em `src/` (149 linhas analisadas, 0 alertas) | N/A | Não | Sem ação necessária na linha de base (`antes`). |
| pip-audit | Nenhuma vulnerabilidade encontrada em `requirements.txt` | N/A | Não | Sem ação necessária na linha de base (`antes`). |
| Safety | `pytest` sem versão fixada em `requirements.txt` (`SFTY-20260122-20373`, 1 de 26 ignoradas por `unpinned-specification`) | Não informada pelo Safety (ignorada pela política) | Não (no ambiente atual) | O `.venv` utiliza `pytest==9.2.0`, sem CVEs conhecidas (confirmado pelo `pip-audit`). Recomendação opcional: fixar versões em `requirements.txt` para reprodutibilidade e eliminação do alerta. |
| Safety | `filelock==3.32.7` em `.venv\pyvenv.cfg` (13 de 26 ignoradas por `environment-dependency`) | Não informada pelo Safety (ignorada pela política) | Não | Dependência exclusiva da própria ferramenta `safety` (`Required-by: safety`); não é usada pela aplicação. Nenhuma alteração necessária na política. |
| Safety | `pip==24.0` em `.venv\pyvenv.cfg` (7 de 26 ignoradas por `environment-dependency`) | Não informada pelo Safety (ignorada pela política) | Não | Instalador padrão do `.venv` (requerido também por `pip-audit` via `pip_api`); não faz parte do runtime da aplicação. Higiene opcional: `python -m pip install --upgrade pip`. |
| Safety | `setuptools==65.5.0` em `.venv\pyvenv.cfg` (5 de 26 ignoradas por `environment-dependency`) | Não informada pelo Safety (ignorada pela política) | Não | Ferramenta de empacotamento padrão criada com o `.venv` do Python 3.11; não faz parte do runtime da aplicação. Higiene opcional: `python -m pip install --upgrade setuptools`. |

> **Nota sobre a inspeção do Safety:** o relatório padrão (`docs/evidencias/seguranca/antes/safety.txt`) resume o resultado como `26 vulnerabilities found, 26 ignored due to policy`. O detalhamento acima foi obtido inspecionando a saída estruturada via `python -m safety scan --output json` e cruzando com `pip-audit` no `.venv`, sem necessidade de alterar a política padrão (`.safety-policy.yml`).

## 5. Reavaliação (depois) e comparação

Executada após a integração da refatoração com padrões de projeto (P3, pacote `src/offers/`), da correção do bug `TWO_FOR_AMOUNT` (D6) e da implementação dos combos promocionais (P4, `src/combo_offer.py` e `src/teller.py`), no commit `e55ff79` (`docs/evidencias/seguranca/depois/`):

| Ferramenta / Métrica | Antes (`2ae7e3d`) | Depois (`e55ff79`) | Variação / Análise |
|----------------------|-------------------|--------------------|--------------------|
| Bandit — arquivos em `src/` | 6 | 14 | +8 arquivos (`src/combo_offer.py` e `src/offers/*`) |
| Bandit — linhas de código (LOC) | 149 | 344 | +195 linhas analisadas |
| Bandit — alertas (High / Medium / Low) | 0 / 0 / 0 | 0 / 0 / 0 | Sem regressões; nenhum `#nosec` usado em `src/` |
| pip-audit (`requirements.txt`) | 0 vulnerabilidades | 0 vulnerabilidades | Inalterado; nenhuma dependência nova adicionada |
| Safety — dependências testadas | 85 | 85 | Mesmo conjunto de dependências do ambiente |
| Safety — vulnerabilidades (ativas / ignoradas) | 0 / 26 | 0 / 26 | Inalterado; mesmos achados de ambiente/spec já triados na seção 4 |

**Conclusão da comparação:**
- O código de produção em `src/` mais que dobrou de tamanho (`149 → 344` LOC, com 8 novos módulos) sem introduzir nenhum achado de segurança estática (`0` alertas no Bandit em todas as severidades e `0` supressões `#nosec`).
- Nenhuma nova biblioteca de terceiros foi adicionada ao runtime da aplicação (que continua usando apenas a biblioteca padrão do Python) nem a `requirements.txt`, mantendo `pip-audit` zerado e o resultado do `safety` idêntico ao da linha de base.
- O critério do **RNF03** (Bandit sem achados `High` e dependências sem vulnerabilidades não triadas) foi plenamente atendido.

## 6. Limitações

- **Ausência de alertas não prova ausência de falhas:** o Bandit realiza análise estática (AST) voltada a padrões comuns de insegurança (injeção, desserialização insegura, criptografia fraca etc.), mas não detecta erros de regra de negócio ou lógica (como o bug legado de `TWO_FOR_AMOUNT` ou desconto duplicado entre combos sobrepostos), que dependem de revisão e testes automatizados.
- **Dependências sem versão fixa em `requirements.txt`:** os pacotes estão declarados sem pinagem (`pytest` em vez de `pytest==9.2.0`), o que reduz a reprodutibilidade estrita em novas instalações e gera o alerta `unpinned-specification` no Safety.
- **Dependência de conta e política padrão no Safety 3.x:** `safety scan` exige login em uma conta Safety (sem autenticação, o script recorre ao comando depreciado `safety check`), exibe avisos internos de depreciação da biblioteca `authlib`, ignora vulnerabilidades de `.venv` por padrão (`environment-dependency`) e não inclui pontuação CVSS no plano gratuito — exigindo inspeção complementar (`--output json` + `pip-audit`).
- **Escopo da auditoria:** o Bandit foi executado sobre `src/` (código da aplicação), não incluindo `tests/` nem `scripts/` (em `scripts/security_audit.py`, o uso de `subprocess` com lista fixa de argumentos está documentado com `# nosec B404` / `# nosec B603`). Em `requirements.txt` constam apenas ferramentas de teste e cobertura, pois o código de produção não possui dependências externas.
