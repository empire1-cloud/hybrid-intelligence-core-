"""
Team-Scoped Canon Run Service ("My Systems" library).

Persists four-part canon outputs per team, mirroring the isolation and
soft-delete pattern already established by `services/pipeline_service.py`.
Canon: WE EVOLVE, NEVER DELETE -- `delete_canon_run` flips `is_active` rather
than removing the document.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from bson import ObjectId

from database import canon_runs_collection
from models.canon_contract import CanonRunResponse, FourPartOutput


class CanonRunError(Exception):
    """Raised for canon-run persistence errors."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


async def save_canon_run(
    team_id: str,
    user_id: str,
    goal: str,
    task_type: str,
    four_part: FourPartOutput,
    metadata: Dict[str, Any],
    title: Optional[str] = None,
) -> CanonRunResponse:
    """Persist a canon run into the team's My Systems library."""
    now = datetime.now(timezone.utc)

    doc = {
        "team_id": team_id,
        "created_by": user_id,
        "title": title,
        "goal": goal,
        "task_type": task_type,
        "four_part": four_part.model_dump(),
        "metadata": metadata,
        "is_active": True,
        "created_at": now,
    }

    result = await canon_runs_collection().insert_one(doc)
    run_id = str(result.inserted_id)

    return CanonRunResponse(
        id=run_id,
        team_id=team_id,
        created_by=user_id,
        title=title,
        goal=goal,
        task_type=task_type,
        four_part=four_part,
        metadata=metadata,
        created_at=now,
    )


async def get_team_canon_runs(
    team_id: str,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """List a team's saved canon runs, most recent first."""
    filter_query = {"team_id": team_id, "is_active": True}

    total = await canon_runs_collection().count_documents(filter_query)
    cursor = (
        canon_runs_collection()
        .find(filter_query)
        .sort("created_at", -1)
        .skip(offset)
        .limit(limit)
    )
    docs = await cursor.to_list(length=limit)

    runs = [
        {
            "id": str(doc["_id"]),
            "team_id": doc["team_id"],
            "created_by": doc["created_by"],
            "title": doc.get("title"),
            "goal": doc["goal"],
            "task_type": doc["task_type"],
            "four_part": doc["four_part"],
            "metadata": doc.get("metadata", {}),
            "created_at": doc["created_at"],
        }
        for doc in docs
    ]

    return {"runs": runs, "total": total, "limit": limit, "offset": offset}


async def get_canon_run_by_id(team_id: str, run_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a single canon run, scoped to the requesting team."""
    if not ObjectId.is_valid(run_id):
        return None

    doc = await canon_runs_collection().find_one(
        {"_id": ObjectId(run_id), "team_id": team_id, "is_active": True}
    )
    if not doc:
        return None

    return {
        "id": str(doc["_id"]),
        "team_id": doc["team_id"],
        "created_by": doc["created_by"],
        "title": doc.get("title"),
        "goal": doc["goal"],
        "task_type": doc["task_type"],
        "four_part": doc["four_part"],
        "metadata": doc.get("metadata", {}),
        "created_at": doc["created_at"],
    }


async def delete_canon_run(team_id: str, run_id: str) -> None:
    """Soft-delete a canon run. WE EVOLVE, NEVER DELETE -- flips a flag, keeps the record."""
    if not ObjectId.is_valid(run_id):
        raise CanonRunError("Invalid run id", status_code=404)

    result = await canon_runs_collection().update_one(
        {"_id": ObjectId(run_id), "team_id": team_id},
        {"$set": {"is_active": False}},
    )
    if result.matched_count == 0:
        raise CanonRunError("Canon run not found", status_code=404)
