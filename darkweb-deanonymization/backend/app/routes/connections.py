from fastapi import APIRouter
from app.crud import fetch_all

router = APIRouter()

# ✅ FIRST: no parameter route
@router.get("/connections/")
def get_connections():
    return fetch_all("SELECT * FROM connections")


# ✅ SECOND: parameter route
@router.get("/connections/{actor_id}")
def get_actor_connections(actor_id: int):
    query = """
        SELECT * FROM connections
        WHERE source_id = %s OR target_id = %s
    """
    return fetch_all(query, (actor_id, actor_id))