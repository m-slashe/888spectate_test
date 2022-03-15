import logging
import pytest
from pytest_mysql import factories

mysql_in_docker = factories.mysql_noproc()
mysql = factories.mysql("mysql_in_docker")

@pytest.fixture(autouse=True)
def configure_logger(caplog):
    caplog.set_level(logging.INFO)