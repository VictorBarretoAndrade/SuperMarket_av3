"""Fixtures compartilhadas por todos os testes (commit zero).

Regra do time: este arquivo só recebe ADIÇÕES. Não altere fixtures
existentes, porque testes de outros integrantes dependem delas.
Preços seguem o README original do kata.
"""
import pytest

from model_objects import Product, ProductUnit
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog


@pytest.fixture
def toothbrush():
    return Product("toothbrush", ProductUnit.EACH)


@pytest.fixture
def toothpaste():
    return Product("toothpaste", ProductUnit.EACH)


@pytest.fixture
def apples():
    return Product("apples", ProductUnit.KILO)


@pytest.fixture
def rice():
    return Product("rice", ProductUnit.EACH)


@pytest.fixture
def cherry_tomatoes():
    return Product("cherry tomato box", ProductUnit.EACH)


@pytest.fixture
def catalog(toothbrush, toothpaste, apples, rice, cherry_tomatoes):
    catalog = FakeCatalog()
    catalog.add_product(toothbrush, 0.99)
    catalog.add_product(toothpaste, 1.79)
    catalog.add_product(apples, 1.99)
    catalog.add_product(rice, 2.49)
    catalog.add_product(cherry_tomatoes, 0.69)
    return catalog


@pytest.fixture
def teller(catalog):
    return Teller(catalog)


@pytest.fixture
def cart():
    return ShoppingCart()
