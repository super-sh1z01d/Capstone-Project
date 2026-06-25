import pytest

from backend.data_loader import load_demo_dataset
from backend.investigator import run_fallback_investigation
from backend.models import InvestigationRequest


@pytest.fixture
def sample_report():
    return run_fallback_investigation(load_demo_dataset(), InvestigationRequest())
