# Análise de segurança: Bandit, pip-audit e Safety

> Dono: **P4** · Enunciado: Passos 7 e 11 e item 5.8 · Barema: 1,0

Evidências brutas: `docs/evidencias/seguranca/antes/` e `docs/evidencias/seguranca/depois/`, geradas por `python scripts/security_audit.py antes|depois`.

## 1. Ambiente e versões
<!-- copiar de ambiente.txt -->

## 2. Escopo e comandos

| Ferramenta | O que analisa | Comando |
|------------|---------------|---------|
| Bandit | Código-fonte de `src/` (análise estática) | `python -m bandit -r src` |
| pip-audit | Dependências de `requirements.txt` (base PyPA/OSV) | `python -m pip_audit -r requirements.txt --desc` |
| Safety | Dependências (base Safety DB) | `python -m safety scan` (exige login) / `safety check -r requirements.txt` (depreciado) |

## 3. Linha de base (antes)

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

## 6. Limitações
<!-- ex.: Safety scan exige conta; ausência de alertas não prova segurança; requirements sem versões fixas -->
