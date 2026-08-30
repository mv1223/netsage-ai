from pathlib import Path
import pytest

# tests/conftest.py
ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
CHECKER = ROOT / "checker"

import sys

sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(CHECKER))


@pytest.fixture
def sample_state():
    import json

    path = ROOT / "data" / "sample_network_state.json"
    return json.loads(path.read_text(encoding="utf-8"))
