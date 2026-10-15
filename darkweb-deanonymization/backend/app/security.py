"""Shared API token. Keep this service behind TLS outside localhost."""
import os
import secrets
from fastapi import HTTPException, Request

def require_api_key(request:Request):
    expected=os.getenv('DARKTRACE_API_KEY','')
    if len(expected)<32: raise HTTPException(503,'Set DARKTRACE_API_KEY to a random value of at least 32 characters')
    if not secrets.compare_digest(request.headers.get('x-api-key',''),expected):
        raise HTTPException(401,'Invalid API key')
