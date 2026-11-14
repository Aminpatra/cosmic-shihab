"""The stored results of FLARE's FLEX test-outcome model, read from backend/data/flex_model/.

pipeline/train_flex_model.py trains the model offline and writes results.json; the API only
reads it, so the deployed backend needs no machine-learning library. A pattern in NASA's FLEX
tests, not a prediction of a real fire.
"""

import json
from pathlib import Path

from app.catalogue import DATA_DIR

RESULTS: Path = DATA_DIR / "flex_model" / "results.json"


def results() -> dict:
    """The results as stored. Raises FileNotFoundError when the model has not been trained."""
    if not RESULTS.exists():
        raise FileNotFoundError(f"{RESULTS.name} is missing; run pipeline/train_flex_model.py")
    return json.loads(RESULTS.read_text(encoding="utf-8"))
