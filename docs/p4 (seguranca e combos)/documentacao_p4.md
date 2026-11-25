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