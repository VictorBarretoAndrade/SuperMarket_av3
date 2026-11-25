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
