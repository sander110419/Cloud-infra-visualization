import copy
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tests.fake_azure import FakeAzure, FakeCredential, collect_sample  # noqa: E402


@pytest.fixture(scope="session")
def _sample():
    return collect_sample()


@pytest.fixture
def sample(_sample):
    """The inventory collected from the fake Contoso tenant (a private copy)."""
    return copy.deepcopy(_sample)


@pytest.fixture
def fake_azure():
    with FakeAzure() as fake:
        yield fake


@pytest.fixture
def arm(fake_azure):
    from azure_func.arm import ArmClient
    client = ArmClient(FakeCredential(), fake_azure.endpoint)
    yield client
    client.close()
