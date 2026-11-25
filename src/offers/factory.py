"""Criação da estratégia de desconto adequada a cada oferta.

Aplica o padrão Factory Method: o código cliente (``ShoppingCart``)
pede uma estratégia para uma ``Offer`` sem conhecer as classes
concretas, eliminando a cadeia de ``if``/``elif`` sobre
``SpecialOfferType``.
"""
from model_objects import SpecialOfferType
from offers.five_for_amount import FiveForAmountStrategy
from offers.percentage_discount import PercentageDiscountStrategy
from offers.three_for_two import ThreeForTwoStrategy
from offers.two_for_amount import TwoForAmountStrategy


class DiscountStrategyFactory:
    """Seleciona e instancia a estratégia correspondente ao tipo de oferta.

    Para suportar uma nova modalidade de oferta basta criar a estratégia
    e registrá-la em ``_strategies``, sem alterar o carrinho (OCP).
    """

    _strategies = {
        SpecialOfferType.THREE_FOR_TWO: ThreeForTwoStrategy,
        SpecialOfferType.TEN_PERCENT_DISCOUNT: PercentageDiscountStrategy,
        SpecialOfferType.TWO_FOR_AMOUNT: TwoForAmountStrategy,
        SpecialOfferType.FIVE_FOR_AMOUNT: FiveForAmountStrategy,
    }

    @classmethod
    def create(cls, offer):
        """Crie a estratégia de desconto para a oferta informada.

        :param offer: ``Offer`` cujo ``offer_type`` define a estratégia.
        :return: instância de ``DiscountStrategy``, ou ``None`` quando o
            tipo de oferta não é suportado (o legado ignorava esses casos
            sem gerar desconto).
        """
        strategy_class = cls._strategies.get(offer.offer_type)
        if strategy_class is None:
            return None
        return strategy_class(offer)
