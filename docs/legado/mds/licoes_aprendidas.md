# Lições aprendidas

> Elemento "Lições aprendidas" da documentação inspirada no MPS.BR (seção 6 do
> enunciado): limitações e decisões relevantes, como reflexão sobre o processo.
> Documento do time, escrito no fechamento (E6), depois da refatoração, da
> correção do bug `TWO_FOR_AMOUNT`, dos combos e da reavaliação de segurança.

## 1. Processo e organização do time

- **Definir o contrato antes de dividir o trabalho funcionou.** O commit zero
  fixou a interface `DiscountStrategy`, as fixtures compartilhadas e as decisões
  D1–D7. Com isso, testes (P2), refatoração (P3), combos (P4) e análise (P1)
  puderam começar em paralelo, e o único ponto de dependência passou a ser a
  ordem de merge.
- **Dono por arquivo evitou conflitos.** Os merges em `development` não
  tiveram conflito porque cada arquivo tinha um responsável e os arquivos
  compartilhados só recebiam adições.
- **Documentos de processo precisam concordar entre si.** `divisao_tarefas.md`
  colocava a correção do bug `TWO_FOR_AMOUNT` depois dos combos, enquanto o
  plano de contingência (E5) exigia só a refatoração. A divergência só apareceu
  na hora de executar; vale revisar os documentos de processo juntos sempre
  que um deles muda.
- **A ordem dos commits é evidência.** O plano exigia que ele próprio entrasse
  no histórico antes da refatoração. Esperar esse merge custou pouco e deixou o
  `git log` contando a história de uma mudança controlada.

## 2. Análise do legado (P1)

- **Métricas tornam o diagnóstico verificável.** Medir a complexidade
  (`radon`: `handle_offers` com CC 13) e a cobertura (41% em
  `shopping_cart.py`) transformou "o código é ruim" em metas objetivas (RNF05,
  RNF06), que depois puderam ser conferidas.
- **Requisitos com critério verificável viram critério de aceitação.** Os
  critérios da etapa E3 do plano de contingência podem ser conferidos no
  histórico: os testes de caracterização não mudaram durante a refatoração, a
  complexidade de `handle_offers` caiu de 13 para 5 e a cobertura de `src/`
  subiu para 98%. Faltou registrar essa conferência no momento do merge (por
  exemplo, na descrição do merge ou num checklist), o que deixaria a evidência
  explícita em vez de reconstruída depois.
- **Achado de diagnóstico sem teste continua sendo hipótese.** O problema #4
  (produto vendido a peso com quantidade fracionada em "3 por 2", ex.: 3,5 kg)
  não ganhou teste de caracterização, então o risco R7 do plano segue aberto.
  Cada achado do diagnóstico deveria ter virado, já na análise, um pedido de
  teste para a P2.
- **Rastreabilidade precisa acompanhar o código.** O commit `fix:` da D6
  renomeou o teste do bug, e a matriz de requisitos e o plano passaram a citar
  um teste que não existia mais. Referências a nomes de teste devem ser
  revisadas a cada merge que mexe nos testes.

## 3. Testes de caracterização (P2)

- **Caracterizar antes de refatorar é a rede de segurança.** No legado, nenhuma
  linha de cálculo de desconto era executada pelos testes. Os 24 testes de
  caracterização e o recibo aprovado (approvaltests) permitiram refatorar sabendo
  que qualquer mudança de valor ou de texto seria detectada.
- **Caracterizar inclui os bugs.** O bug do `TWO_FOR_AMOUNT` foi encontrado e
  registrado como teste (D6) em vez de corrigido na hora. Isso separou "mudou
  sem querer" de "mudou de propósito".
- **`xfail` como contrato de aceitação.** Os testes de combo escritos antes da
  implementação documentaram o comportamento esperado e mantiveram a suíte
  verde enquanto a funcionalidade não existia. Atenção: com `raises=AttributeError`,
  testes que passarem viram `XPASS` sem quebrar a suíte, então o marcador
  precisa ser removido junto com a implementação.

## 4. Refatoração e padrões de projeto (P3)

- **Pequenos passos, cada um verificável.** A refatoração foi feita em commits
  que adicionavam código novo sem usá-lo (base, estratégias, fábrica) e só
  depois trocavam o `handle_offers`. A suíte passou em todos os commits, então
  qualquer um pode ser revertido sozinho.
- **Testes de caracterização não bastam para provar equivalência.** Além deles,
  as estratégias foram comparadas com o código legado em 7.776 combinações de
  oferta, preço e quantidade e o carrinho em 5.000 carrinhos aleatórios. Isso
  mostrou que preservar a **ordem das operações** importa: com `float`,
  reescrever uma fórmula "equivalente" pode mudar o último dígito do recibo.
- **Padrão só quando resolve um problema.** Strategy e Factory Method
  eliminaram a cadeia de `if`s (CC 13 -> 5); o Template Method surgiu da
  duplicação observada entre as quatro ofertas, não foi planejado de antemão.
- **Separar refatoração e correção vale o esforço.** A correção do bug entrou
  num commit `fix:` próprio, com o teste atualizado no mesmo commit. A
  comparação com o legado confirmou que só os casos de "2 por valor" com
  quantidade ímpar mudaram.
- **Uma abstração não precisa servir para tudo.** A fábrica foi pensada para
  ofertas de um único produto (`Offer`), e o combo envolve vários produtos.
  Em vez de forçar o combo na fábrica, ele implementa `DiscountStrategy`
  diretamente e é registrado pelo `Teller` (`add_combo_offer`). O contrato
  comum foi o que garantiu a extensão; o texto do RNF02, que previa "registro
  na fábrica", precisou ser ajustado depois.

## 5. Combos e segurança (P4)

### Combos

- **A arquitetura aceitou a promoção nova sem mexer no que existia.** O combo
  entrou com um arquivo novo (`src/combo_offer.py`) e adições no `Teller`;
  nenhuma linha de `src/offers/` nem do `ShoppingCart` foi alterada, e os 24
  testes de caracterização continuaram passando (RNF02).
- **Testes de aceitação escritos antes guiaram a implementação.** Os 5 testes
  de combo do commit zero (D1, D2, D3) definiram o comportamento esperado; ao
  implementar, bastou fazê-los passar e remover o `xfail`.
- **Revisão encontra o que os testes não previram.** Na revisão do merge do
  combo, um caso fora dos testes apareceu: dois combos que compartilham um
  produto (ex.: escova + creme e escova + fio) aplicavam desconto duas vezes na
  mesma escova, contrariando a regra de "evitar desconto duplicado". A correção
  passou a abater as unidades usadas por cada combo antes do próximo, e o caso
  ganhou testes próprios. Combinações entre promoções merecem uma lista de
  cenários desde a especificação.

### Segurança

- **Ausência de alertas não é prova de segurança.** Bandit e pip-audit não
  encontraram problemas antes nem depois das mudanças, mas o código de produção
  usa só a biblioteca padrão e as ferramentas cobrem padrões e bases de
  vulnerabilidade específicos. O próprio desconto duplicado entre combos, um
  erro de regra de negócio, passaria despercebido por todas elas.
- **Comparar antes e depois dá contexto ao resultado.** O código de `src/` mais
  que dobrou (149 -> 344 linhas, 8 módulos novos) sem nenhum alerta novo no
  Bandit, e nenhuma dependência foi adicionada, então pip-audit e Safety
  ficaram iguais à linha de base.
- **Ler além do resumo da ferramenta.** O Safety resumiu o resultado como
  "26 vulnerabilities found, 26 ignored due to policy". Só a saída detalhada
  (`--output json`) mostrou que eram dependências das próprias ferramentas e do
  `.venv` (`filelock`, `pip`, `setuptools`) e uma versão não fixada do `pytest`,
  nenhuma usada pela aplicação.
- **Limitação de acesso:** o `safety scan` exige login numa conta Safety, o que
  precisa constar nas evidências para que outra pessoa consiga reproduzir a
  análise.

## 6. Reprodutibilidade e ambiente

- **Cada integrante usou um ambiente diferente.** As evidências registram
  Python 3.12.10 (testes, P2) e 3.11.9 (segurança, P4, e refatoração, P3), e o
  README chegou a citar 3.14, versão que ninguém usou. Os resultados foram os
  mesmos, e o README foi corrigido para as versões realmente testadas, mas o
  ideal é definir uma versão única desde o início (RNF04).
- **Dependências sem versão fixa** (`requirements.txt`) geraram o alerta
  `unpinned-specification` no Safety, antes e depois, e dificultam reproduzir o
  ambiente. Ficou registrado como risco remanescente.
- **Evidência é um retrato de um momento.** As evidências finais de teste
  foram geradas com 55 testes; minutos depois, a correção dos combos
  sobrepostos acrescentou 2 testes. Evidências precisam ser geradas de novo
  depois do último merge de código, não em paralelo a ele.

## 7. O que faríamos diferente

- Revisar `divisao_tarefas.md` e `plano_contingencia.md` juntos logo no início,
  para que a ordem das etapas fosse uma só.
- Combinar a integração do combo com a fábrica de estratégias antes de começar
  a refatoração, em vez de depois.
- Fixar a versão do Python e das dependências no commit zero.
- Listar, já nos requisitos, os cenários de combinação entre promoções
  (combo com oferta individual, combos que compartilham produtos), em vez de
  descobri-los na revisão.
- Gerar as evidências finais só depois do último merge de código.

## 8. Resultado final

| Métrica | Legado (`v0-legado`) | Final (`development`) |
|---------|----------------------|-----------------------|
| Complexidade de `handle_offers` (radon) | 13 (C) | 5 (A) |
| Maior complexidade em `src/` | 13 (`handle_offers`) | 8 (B, `Teller.checks_out_articles_from`) |
| Cobertura de `src/` | 71% | 99% |
| Testes passando | 1 | 57 (0 falhas, 0 `xfail`) |
| "2 por 0,99" com 3 itens (bug D6) | 2,175 | 1,68 |
| Alertas do Bandit (High/Medium/Low) | 0 / 0 / 0 | 0 / 0 / 0 |
| Vulnerabilidades no pip-audit | 0 | 0 |
