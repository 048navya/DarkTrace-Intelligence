import os
from fastapi import FastAPI, Depends, HTTPException
from app.security import require_api_key
from app.crud import fetch_one
from app.routes import interop
from fastapi.middleware.cors import CORSMiddleware

from app.config import (
    APP_NAME,
    APP_VERSION,
)

from app.routes import (
    actors,
    blockchain,
    handles,
    intelligence,
    posts,
    profile,
    search,
)


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Evidence-driven DarkForums behavioral "
        "persona analysis API."
    ),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in os.getenv("DARKTRACE_CORS_ORIGINS","http://localhost:3000").split(",") if x.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTES
# ============================================================

app.include_router(search.router, dependencies=[Depends(require_api_key)])
app.include_router(profile.router, dependencies=[Depends(require_api_key)])
app.include_router(actors.router, dependencies=[Depends(require_api_key)])
app.include_router(handles.router, dependencies=[Depends(require_api_key)])
app.include_router(posts.router, dependencies=[Depends(require_api_key)])
app.include_router(intelligence.router, dependencies=[Depends(require_api_key)])
app.include_router(blockchain.router, dependencies=[Depends(require_api_key)])


# ============================================================
# HEALTH
# ============================================================

app.include_router(interop.router, dependencies=[Depends(require_api_key)])

@app.get("/")
def home():

    return {
        "message": "DarkTrace Intelligence API Running",
        "version": APP_VERSION,
    }


@app.get('/health')
def health():
    try:
        fetch_one('SELECT 1 AS ready')
    except Exception:
        raise HTTPException(503,'Database is unavailable')
    return {'status':'ok','database':'PostgreSQL'}
