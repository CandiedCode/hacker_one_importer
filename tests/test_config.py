import pytest
import hacker_one_importer.config as config


def test_singleton():
    dev_config = config.DevelopmentConfig()
    dev_config2 = config.DevelopmentConfig()

    assert dev_config2 == dev_config


def test_development_configuration(monkeypatch):
    monkeypatch.setenv('TOKEN', 'token')
    monkeypatch.setenv('USERNAME', 'username')
    monkeypatch.setenv('PASSWORD', 'password')

    dev_config = config.DevelopmentConfig()

    assert dev_config.TOKEN == 'token'
    assert dev_config.USERNAME == 'username'
    assert dev_config.PASSWORD == 'password'
    assert dev_config.DYNAMODB_ENDPOINT_URL == 'http://dynamodb:8000'


def test_production_configuration(monkeypatch):
    monkeypatch.setenv('TOKEN', 'token')
    monkeypatch.setenv('USERNAME', 'username')
    monkeypatch.setenv('PASSWORD', 'password')

    prod_config = config.ProductionConfig()

    assert prod_config.TOKEN == 'token'
    assert prod_config.USERNAME == 'username'
    assert prod_config.PASSWORD == 'password'
    assert prod_config.DYNAMODB_ENDPOINT_URL == 'https://dynamodb.us-east-1.amazonaws.com'


def test_ssm_configuration():
    dev_config = config.DevelopmentConfig()
    assert dev_config.TOKEN is not None
    assert dev_config.USERNAME is not None
    assert dev_config.PASSWORD is not None


@pytest.mark.parametrize("environment, type_name",
                         [('development', config.DevelopmentConfig),
                          ('production', config.ProductionConfig)])
def test_get_config(monkeypatch, environment, type_name):
    monkeypatch.setenv('ENVIRONMENT', environment)
    config_info = config.get_config()

    assert type(config_info) == type_name
