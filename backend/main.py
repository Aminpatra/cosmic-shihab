"""FLARE API. Vercel's entrypoint: it serves the FastAPI instance named `app` in this file."""

from fastapi import FastAPI

from app.routes import catalogue, downloads, ranking, runs, search

app = FastAPI(
    title="FLARE API",
    summary="NASA PSI microgravity combustion investigations, read-only.",
    # Only /api/* reaches the backend on Vercel, so the docs live there too.
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None,
)

app.include_router(catalogue.router)
app.include_router(downloads.router)
app.include_router(ranking.router)
app.include_router(search.router)
app.include_router(runs.router)
