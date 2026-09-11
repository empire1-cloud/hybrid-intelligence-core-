"""
Execution Analytics and Instrumentation API

Exposes comprehensive metrics on AI operations:
- Executions/day, by engine, by pipeline
- Success rates, latency, cost, quality
- Provider and model performance
- Revenue insights per pipeline

This is the "AI Operations Command Center" view replacing the raw engine list.
"""

from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from bson import ObjectId

from database import execution_logs_collection, pipelines_collection, users_collection
from core.auth_service import verify_user
from core.subscription_service import get_user_team

router = APIRouter(tags=["analytics"], prefix="/analytics")


@router.get("/executions/summary")
async def execution_summary(
    user_id: str = Depends(verify_user),
    team_id: str = Depends(get_user_team),
    hours: int = Query(24, ge=1, le=168)  # Last N hours
) -> Dict[str, Any]:
    """
    Executive summary of AI operations for the last N hours.

    Returns:
    - Total executions, success rate
    - Cost aggregates
    - Top engines by execution count
    - Quality metrics
    """
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=hours)

    pipeline = [
        {"$match": {
            "team_id": team_id,
            "created_at": {"$gte": start_time}
        }},
        {
            "$facet": {
                "totals": [
                    {
                        "$group": {
                            "_id": None,
                            "total_executions": {"$sum": 1},
                            "successful": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}},
                            "failed": {"$sum": {"$cond": [{"$eq": ["$status", "error"]}, 1, 0]}},
                            "total_cost": {"$sum": "$cost_usd"},
                            "avg_duration_ms": {"$avg": "$duration_ms"},
                            "avg_confidence": {"$avg": "$confidence"},
                            "total_tokens": {"$sum": "$total_tokens"},
                        }
                    }
                ],
                "by_engine": [
                    {
                        "$group": {
                            "_id": "$engine",
                            "count": {"$sum": 1},
                            "cost": {"$sum": "$cost_usd"},
                            "avg_latency": {"$avg": "$duration_ms"},
                        }
                    },
                    {"$sort": {"count": -1}},
                    {"$limit": 5}
                ],
                "by_provider": [
                    {
                        "$group": {
                            "_id": "$provider",
                            "count": {"$sum": 1},
                            "cost": {"$sum": "$cost_usd"},
                            "avg_confidence": {"$avg": "$confidence"},
                        }
                    },
                    {"$sort": {"count": -1}}
                ],
                "by_model": [
                    {
                        "$group": {
                            "_id": "$model",
                            "count": {"$sum": 1},
                            "cost": {"$sum": "$cost_usd"},
                        }
                    },
                    {"$sort": {"cost": -1}},
                    {"$limit": 5}
                ]
            }
        }
    ]

    result = await execution_logs_collection().aggregate(pipeline).to_list(1)
    data = result[0] if result else {}

    totals = data.get("totals", [{}])[0]
    total_exec = totals.get("total_executions", 0)

    return {
        "period_hours": hours,
        "summary": {
            "total_executions": total_exec,
            "successful": totals.get("successful", 0),
            "failed": totals.get("failed", 0),
            "success_rate": round(
                (totals.get("successful", 0) / total_exec * 100) if total_exec > 0 else 0,
                1
            ),
            "total_cost_usd": round(totals.get("total_cost", 0) or 0, 3),
            "avg_cost_per_execution": round(
                ((totals.get("total_cost", 0) or 0) / total_exec) if total_exec > 0 else 0,
                4
            ),
            "avg_duration_ms": round(totals.get("avg_duration_ms", 0) or 0, 0),
            "total_tokens_used": totals.get("total_tokens", 0) or 0,
            "avg_confidence": round(totals.get("avg_confidence", 0) or 0, 3),
        },
        "top_engines": [
            {
                "engine": e["_id"],
                "executions": e["count"],
                "cost_usd": round(e["cost"] or 0, 3),
                "avg_latency_ms": round(e["avg_latency"] or 0, 0),
            }
            for e in data.get("by_engine", [])
        ],
        "by_provider": [
            {
                "provider": p["_id"],
                "executions": p["count"],
                "cost_usd": round(p["cost"] or 0, 3),
                "avg_confidence": round(p["avg_confidence"] or 0, 3),
            }
            for p in data.get("by_provider", [])
        ],
        "top_models": [
            {
                "model": m["_id"],
                "executions": m["count"],
                "cost_usd": round(m["cost"] or 0, 3),
            }
            for m in data.get("by_model", [])
        ],
    }


@router.get("/executions/trend")
async def execution_trend(
    user_id: str = Depends(verify_user),
    team_id: str = Depends(get_user_team),
    days: int = Query(7, ge=1, le=90),
    granularity: str = Query("day", regex="^(hour|day)$")
) -> Dict[str, Any]:
    """
    Execution trend over time (hourly or daily granularity).

    Returns timeline of:
    - Executions count
    - Success rate
    - Average cost
    - Average latency
    """
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(days=days)

    # Build date grouping based on granularity
    if granularity == "hour":
        date_format = "%Y-%m-%d %H:00"
        bucket_size = 3600  # seconds
    else:
        date_format = "%Y-%m-%d"
        bucket_size = 86400  # seconds

    pipeline = [
        {"$match": {
            "team_id": team_id,
            "created_at": {"$gte": start_time}
        }},
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": date_format,
                        "date": "$created_at"
                    }
                },
                "total": {"$sum": 1},
                "successful": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}},
                "cost": {"$sum": "$cost_usd"},
                "avg_duration": {"$avg": "$duration_ms"},
                "avg_confidence": {"$avg": "$confidence"},
            }
        },
        {"$sort": {"_id": 1}}
    ]

    results = await execution_logs_collection().aggregate(pipeline).to_list(None)

    timeline = []
    for r in results:
        total = r["total"]
        timeline.append({
            "timestamp": r["_id"],
            "executions": total,
            "success_rate": round((r["successful"] / total * 100) if total > 0 else 0, 1),
            "total_cost_usd": round(r["cost"] or 0, 3),
            "avg_cost_per_execution": round(((r["cost"] or 0) / total) if total > 0 else 0, 4),
            "avg_latency_ms": round(r["avg_duration"] or 0, 0),
            "avg_confidence": round(r["avg_confidence"] or 0, 3),
        })

    return {
        "granularity": granularity,
        "days": days,
        "timeline": timeline,
    }


@router.get("/executions/by-engine")
async def executions_by_engine(
    user_id: str = Depends(verify_user),
    team_id: str = Depends(get_user_team),
    hours: int = Query(24, ge=1, le=168)
) -> Dict[str, Any]:
    """
    Execution distribution and metrics by engine.

    Returns per-engine:
    - Execution count and success rate
    - Cost and latency
    - Quality metrics
    - Provider/model split
    """
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=hours)

    pipeline = [
        {"$match": {
            "team_id": team_id,
            "created_at": {"$gte": start_time}
        }},
        {
            "$group": {
                "_id": "$engine",
                "total": {"$sum": 1},
                "successful": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}},
                "failed": {"$sum": {"$cond": [{"$eq": ["$status", "error"]}, 1, 0]}},
                "total_cost": {"$sum": "$cost_usd"},
                "avg_duration": {"$avg": "$duration_ms"},
                "avg_confidence": {"$avg": "$confidence"},
                "total_tokens": {"$sum": "$total_tokens"},
                "providers": {"$addToSet": "$provider"},
            }
        },
        {"$sort": {"total": -1}}
    ]

    results = await execution_logs_collection().aggregate(pipeline).to_list(None)

    engines = []
    for r in results:
        total = r["total"]
        engines.append({
            "engine": r["_id"],
            "executions": total,
            "successful": r["successful"],
            "failed": r["failed"],
            "success_rate": round((r["successful"] / total * 100) if total > 0 else 0, 1),
            "total_cost_usd": round(r["total_cost"] or 0, 3),
            "avg_cost_per_execution": round(((r["total_cost"] or 0) / total) if total > 0 else 0, 4),
            "avg_latency_ms": round(r["avg_duration"] or 0, 0),
            "avg_confidence": round(r["avg_confidence"] or 0, 3),
            "total_tokens": r["total_tokens"] or 0,
            "providers": list(filter(None, r.get("providers", []))),
        })

    return {
        "period_hours": hours,
        "engines": engines,
    }


@router.get("/executions/by-pipeline")
async def executions_by_pipeline(
    user_id: str = Depends(verify_user),
    team_id: str = Depends(get_user_team),
    hours: int = Query(24, ge=1, le=168)
) -> Dict[str, Any]:
    """
    Execution metrics by pipeline (if used).

    Returns per-pipeline:
    - Completion rate
    - Total cost
    - Average latency
    """
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=hours)

    pipeline = [
        {"$match": {
            "team_id": team_id,
            "pipeline_id": {"$ne": None},
            "created_at": {"$gte": start_time}
        }},
        {
            "$group": {
                "_id": "$pipeline_id",
                "total": {"$sum": 1},
                "successful": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}},
                "total_cost": {"$sum": "$cost_usd"},
                "avg_duration": {"$avg": "$duration_ms"},
            }
        },
        {"$sort": {"total": -1}}
    ]

    results = await execution_logs_collection().aggregate(pipeline).to_list(None)

    pipelines_list = []
    for r in results:
        pipeline_id = r["_id"]
        total = r["total"]

        # Get pipeline name
        pipeline_name = "Unknown"
        if pipeline_id and ObjectId.is_valid(pipeline_id):
            p = await pipelines_collection().find_one(
                {"_id": ObjectId(pipeline_id)},
                {"name": 1}
            )
            if p:
                pipeline_name = p.get("name", "Unknown")

        pipelines_list.append({
            "pipeline_id": pipeline_id,
            "pipeline_name": pipeline_name,
            "total_executions": total,
            "successful": r["successful"],
            "completion_rate": round((r["successful"] / total * 100) if total > 0 else 0, 1),
            "total_cost_usd": round(r["total_cost"] or 0, 3),
            "avg_latency_ms": round(r["avg_duration"] or 0, 0),
        })

    return {
        "period_hours": hours,
        "pipelines": pipelines_list,
    }


@router.get("/executions/cost-analysis")
async def cost_analysis(
    user_id: str = Depends(verify_user),
    team_id: str = Depends(get_user_team),
    hours: int = Query(24, ge=1, le=168)
) -> Dict[str, Any]:
    """
    Cost analysis by engine, model, and provider.

    Returns cost breakdown and per-execution cost.
    """
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=hours)

    pipeline = [
        {"$match": {
            "team_id": team_id,
            "created_at": {"$gte": start_time}
        }},
        {
            "$facet": {
                "by_engine": [
                    {
                        "$group": {
                            "_id": "$engine",
                            "total_cost": {"$sum": "$cost_usd"},
                            "executions": {"$sum": 1},
                        }
                    },
                    {"$sort": {"total_cost": -1}}
                ],
                "by_model": [
                    {
                        "$group": {
                            "_id": "$model",
                            "total_cost": {"$sum": "$cost_usd"},
                            "executions": {"$sum": 1},
                        }
                    },
                    {"$sort": {"total_cost": -1}}
                ],
                "by_provider": [
                    {
                        "$group": {
                            "_id": "$provider",
                            "total_cost": {"$sum": "$cost_usd"},
                            "executions": {"$sum": 1},
                        }
                    },
                    {"$sort": {"total_cost": -1}}
                ],
                "totals": [
                    {
                        "$group": {
                            "_id": None,
                            "total_cost": {"$sum": "$cost_usd"},
                            "total_executions": {"$sum": 1},
                        }
                    }
                ]
            }
        }
    ]

    result = await execution_logs_collection().aggregate(pipeline).to_list(1)
    data = result[0] if result else {}

    total_cost = 0
    total_execs = 0
    if data.get("totals"):
        total_cost = data["totals"][0].get("total_cost", 0) or 0
        total_execs = data["totals"][0].get("total_executions", 0) or 0

    return {
        "period_hours": hours,
        "summary": {
            "total_cost_usd": round(total_cost, 3),
            "total_executions": total_execs,
            "cost_per_execution": round((total_cost / total_execs) if total_execs > 0 else 0, 4),
        },
        "by_engine": [
            {
                "engine": e["_id"],
                "total_cost_usd": round(e["total_cost"] or 0, 3),
                "executions": e["executions"],
                "cost_per_execution": round(((e["total_cost"] or 0) / e["executions"]) if e["executions"] > 0 else 0, 4),
                "percentage_of_total": round(((e["total_cost"] or 0) / total_cost * 100) if total_cost > 0 else 0, 1),
            }
            for e in data.get("by_engine", [])
        ],
        "by_model": [
            {
                "model": m["_id"],
                "total_cost_usd": round(m["total_cost"] or 0, 3),
                "executions": m["executions"],
                "cost_per_execution": round(((m["total_cost"] or 0) / m["executions"]) if m["executions"] > 0 else 0, 4),
            }
            for m in data.get("by_model", [])
        ],
        "by_provider": [
            {
                "provider": p["_id"],
                "total_cost_usd": round(p["total_cost"] or 0, 3),
                "executions": p["executions"],
                "cost_per_execution": round(((p["total_cost"] or 0) / p["executions"]) if p["executions"] > 0 else 0, 4),
            }
            for p in data.get("by_provider", [])
        ],
    }


@router.get("/executions/quality-metrics")
async def quality_metrics(
    user_id: str = Depends(verify_user),
    team_id: str = Depends(get_user_team),
    hours: int = Query(24, ge=1, le=168)
) -> Dict[str, Any]:
    """
    Quality and performance metrics for AI outputs.

    Returns:
    - Confidence distribution
    - Success/error rates
    - Latency distribution (p50, p95, p99)
    - Provider quality comparison
    """
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=hours)

    pipeline = [
        {"$match": {
            "team_id": team_id,
            "created_at": {"$gte": start_time}
        }},
        {
            "$facet": {
                "overall": [
                    {
                        "$group": {
                            "_id": None,
                            "success_rate": {
                                "$avg": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}
                            },
                            "avg_confidence": {"$avg": "$confidence"},
                            "min_confidence": {"$min": "$confidence"},
                            "max_confidence": {"$max": "$confidence"},
                        }
                    }
                ],
                "by_engine": [
                    {
                        "$group": {
                            "_id": "$engine",
                            "success_rate": {
                                "$avg": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}
                            },
                            "avg_confidence": {"$avg": "$confidence"},
                            "count": {"$sum": 1},
                        }
                    },
                    {"$sort": {"avg_confidence": -1}},
                    {"$limit": 10}
                ],
                "by_provider": [
                    {
                        "$group": {
                            "_id": "$provider",
                            "success_rate": {
                                "$avg": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}
                            },
                            "avg_confidence": {"$avg": "$confidence"},
                            "count": {"$sum": 1},
                        }
                    },
                    {"$sort": {"avg_confidence": -1}}
                ]
            }
        }
    ]

    result = await execution_logs_collection().aggregate(pipeline).to_list(1)
    data = result[0] if result else {}

    overall = data.get("overall", [{}])[0]

    return {
        "period_hours": hours,
        "overall": {
            "success_rate": round((overall.get("success_rate", 0) or 0) * 100, 1),
            "avg_confidence": round(overall.get("avg_confidence", 0) or 0, 3),
            "confidence_range": {
                "min": round(overall.get("min_confidence") or 0, 3),
                "max": round(overall.get("max_confidence") or 0, 3),
            }
        },
        "by_engine": [
            {
                "engine": e["_id"],
                "success_rate": round((e.get("success_rate", 0) or 0) * 100, 1),
                "avg_confidence": round(e.get("avg_confidence", 0) or 0, 3),
                "executions": e["count"],
            }
            for e in data.get("by_engine", [])
        ],
        "by_provider": [
            {
                "provider": p["_id"],
                "success_rate": round((p.get("success_rate", 0) or 0) * 100, 1),
                "avg_confidence": round(p.get("avg_confidence", 0) or 0, 3),
                "executions": p["count"],
            }
            for p in data.get("by_provider", [])
        ],
    }
