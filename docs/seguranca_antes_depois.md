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

## 5. Reavaliação (depois) e comparação

## 6. Limitações
<!-- ex.: Safety scan exige conta; ausência de alertas não prova segurança; requirements sem versões fixas -->
