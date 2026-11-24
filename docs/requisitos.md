# Documento de requisitos

> Dono: **P1** · Enunciado: Passo 4 e item 5.2 · Barema: 1,0

Cada requisito precisa de um ID, uma descrição, um critério de aceitação verificável e o(s) teste(s) que o cobrem (rastreabilidade).

## 1. Requisitos funcionais

| ID | Descrição | Critério de aceitação | Teste(s) |
|----|-----------|-----------------------|----------|
| RF01 | Calcular o total do carrinho sem ofertas | | |
| RF02 | Oferta 3 por 2 | | |
| RF03 | Desconto percentual | | |
| RF04 | Oferta 2 por valor | | |
| RF05 | Oferta 5 por valor | | |
| RF06 | Emitir recibo com itens, descontos e total | | |
| RF07 | Combo promocional: 10% sobre os itens dos combos completos | 1 escova + 1 creme -> 10% sobre os dois | `test_combos.py` |
| RF08 | Combo incompleto não recebe desconto | | |
| RF09 | Vários combos e excedentes (D2) | | |
| RF10 | Convivência com outras ofertas (D1) | | |

## 2. Requisitos não funcionais

| ID | Descrição | Critério verificável |
|----|-----------|----------------------|
| RNF01 | A API pública existente é preservada (D7) | Testes de caracterização passam sem alteração |
| RNF02 | Extensibilidade: nova promoção sem alterar as existentes | |
| RNF03 | Segurança: sem achados de severidade alta no Bandit e sem dependência vulnerável | |
| RNF04 | Reprodutibilidade | README permite rodar do zero |

## 3. Matriz de rastreabilidade
<!-- requisito -> implementação -> teste -> evidência -->
