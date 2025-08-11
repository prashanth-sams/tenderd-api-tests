"""
@Author:       Prashanth Sams
@Created:      Fri Aug  10 22:55:27 2025 (-0400)
"""
import logging
import random
import sys
import pytest

from utils.file_reader import read_json_file


@pytest.fixture
def payload():
    """
    Fixture to generate payload for testing
    """
    payload = read_json_file('payload')

    random_no = random.randint(1, 100)
    payload['name'] = payload['name'] + str(random_no)

    yield payload


@pytest.fixture(scope='session')
def logger():
    """
    This fixture is used to set up the logger for the tests.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # show logs terminal
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    # store logs in file
    file_handler = logging.FileHandler(r'test.log', mode='w')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s', '%m/%d/%Y %I:%M:%S %p')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


@pytest.hookimpl
def pytest_addoption(parser):
    """
    This function adds a new command line option to pytest.
    """
    parser.addoption("--env", action="store", default="dev", help="run dev env tests")


@pytest.fixture(scope="session")
def env(request):
    """
    This function returns the environment.
    """
    return request.config.getoption("--env")
