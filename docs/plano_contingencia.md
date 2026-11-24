# Plano de contingência e refatoração

> Dono: **P1** · Enunciado: Passo 5 e item 5.3 · Barema: 0,5 (ausência: -3,0)
> Precisa ser commitado **antes** da refatoração (ordem no git).

## 1. Sequência das mudanças
<!-- ver docs/divisao_tarefas.md, seção 3 -->

## 2. Invariantes de negócio e interfaces que não podem mudar
<!-- D7: Teller, ShoppingCart.handle_offers, Receipt, Discount, Offer, SpecialOfferType; valores e textos do recibo -->

## 3. Riscos

| Risco | Probabilidade | Impacto | Prevenção | Teste associado | Reversão |
|-------|---------------|---------|-----------|-----------------|----------|
| Refatoração altera algum valor de desconto | | Alto | Testes de caracterização antes | | `git revert` |
| Combo gera desconto duplicado com outra oferta | | | Decisão D1 + teste | | |

## 4. Estratégia de reversão
<!-- tag v0-legado, uma branch por mudança, git revert, nada de push --force -->

## 5. Critérios de aceitação de cada etapa
