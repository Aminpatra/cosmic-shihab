"""The FLEX model's results: scores against the baseline, confusion matrices and SHAP summaries."""

from typing import Any

from fastapi import APIRouter, HTTPException

from app import flex_model

router = APIRouter(prefix="/api", tags=["flex model"])


@router.get("/flex-model")
def get_flex_model() -> dict[str, Any]:
    """How FLEX tests ended, learned from what was set before them. Not a prediction of a real fire."""
    try:
        return flex_model.results()
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
