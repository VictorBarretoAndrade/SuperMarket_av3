# Lições aprendidas

> Elemento "Lições aprendidas" da documentação inspirada no MPS.BR (seção 6 do
> enunciado): limitações e decisões relevantes, como reflexão sobre o processo.
> Documento do time: cada integrante complementa a sua frente. Versão
> preliminar, escrita antes da entrega dos combos (P4); as seções marcadas como
> _a completar_ devem ser revisadas no fechamento (E6).

## 1. Processo e organização do time

- **Definir o contrato antes de dividir o trabalho funcionou.** O commit zero
  fixou a interface `DiscountStrategy`, as fixtures compartilhadas e as decisões
  D1–D7. Com isso, testes (P2), refatoração (P3), combos (P4) e análise (P1)
  puderam começar em paralelo, e o único ponto de dependência passou a ser a
  ordem de merge.
- **Dono por arquivo evitou conflitos.** Até aqui, os merges em `development`
  não tiveram conflito porque cada arquivo tinha um responsável e os arquivos
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
- **Limitação:** a fábrica foi pensada para ofertas de um único produto
  (`Offer`). O combo, que envolve vários produtos, não se encaixa diretamente
  nela; a forma de integração precisa ser combinada com a P4 (RNF02).

## 5. Segurança (P4)

- **Ausência de alertas não é prova de segurança.** Bandit e pip-audit não
  encontraram problemas na linha de base, mas o código de produção usa só a
  biblioteca padrão e as ferramentas cobrem padrões e bases de vulnerabilidade
  específicos.
- **Ler além do resumo da ferramenta.** O Safety resumiu o resultado como
  "26 vulnerabilities found, 26 ignored due to policy". Só a saída detalhada
  (`--output json`) mostrou que eram dependências das próprias ferramentas e do
  `.venv` (`filelock`, `pip`, `setuptools`) e uma versão não fixada do `pytest`,
  nenhuma usada pela aplicação.
- **Limitação de acesso:** o `safety scan` exige login numa conta Safety, o que
  precisa constar nas evidências para que outra pessoa consiga reproduzir a
  análise.

_A completar pela P4 após a reavaliação "depois" e a entrega dos combos._

## 6. Reprodutibilidade e ambiente

- **Cada integrante usou um ambiente diferente.** As evidências registram
  Python 3.12.10 (testes, P2) e 3.11.9 (segurança, P4, e refatoração, P3),
  enquanto o README cita 3.14. Os resultados foram os mesmos, mas a versão
  usada na entrega final deve ser uma só e estar no README (RNF04).
- **Dependências sem versão fixa** (`requirements.txt`) geraram alerta no Safety
  e dificultam reproduzir o ambiente. Fixar as versões é uma melhoria simples
  para o fechamento.

## 7. O que faríamos diferente

- Revisar `divisao_tarefas.md` e `plano_contingencia.md` juntos logo no início,
  para que a ordem das etapas fosse uma só.
- Combinar a integração do combo com a fábrica de estratégias antes de começar
  a refatoração, em vez de depois.
- Fixar a versão do Python e das dependências no commit zero.

_A completar pelo time no fechamento: resultado final dos combos, segurança
"depois" e comparativo final de testes._
