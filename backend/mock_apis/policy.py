"""Mock travel policy API — simulates Mundostra's policy engine."""

from __future__ import annotations

from fastapi import APIRouter, Query

router = APIRouter(prefix="/mock/policy", tags=["mock"])

_TIER_RULES: dict[str, dict[str, object]] = {
    "standard": {
        "budget_cap": 500.0,
        "auto_approve_delta": 25.0,
        "cabin_allowed": ["economy"],
        "requires_manager_approval_above": 500.0,
    },
    "manager": {
        "budget_cap": 650.0,
        "auto_approve_delta": 50.0,
        "cabin_allowed": ["economy", "premium_economy"],
        "requires_manager_approval_above": 650.0,
    },
    "executive": {
        "budget_cap": 800.0,
        "auto_approve_delta": 100.0,
        "cabin_allowed": ["economy", "premium_economy", "business"],
        "requires_manager_approval_above": 800.0,
    },
}


@router.get("/evaluate")
async def evaluate_policy(
    policy_tier: str = Query(default="executive"),
    original_price: float = Query(default=400.0),
    proposed_price: float = Query(default=420.0),
    cabin: str = Query(default="economy"),
) -> dict[str, object]:
    rules = _TIER_RULES.get(policy_tier, _TIER_RULES["standard"])

    budget_cap = float(rules["budget_cap"])  # type: ignore[arg-type]
    auto_approve_delta = float(rules["auto_approve_delta"])  # type: ignore[arg-type]
    allowed_cabins: list[str] = rules["cabin_allowed"]  # type: ignore[assignment]

    price_delta = proposed_price - original_price
    within_cap = proposed_price <= budget_cap
    cabin_allowed = cabin in allowed_cabins
    auto_approvable = within_cap and cabin_allowed and price_delta <= auto_approve_delta

    if not within_cap:
        budget_status = "exceeds_cap"
    elif price_delta <= 0:
        budget_status = "under_original"
    else:
        budget_status = "within_cap"

    return {
        "policy_tier": policy_tier,
        "rules": rules,
        "original_price": original_price,
        "proposed_price": proposed_price,
        "price_delta": price_delta,
        "budget_status": budget_status,
        "cabin_allowed": cabin_allowed,
        "within_cap": within_cap,
        "auto_approve_eligible": auto_approvable,
        "escalation_required": not within_cap,
        "policy_version": "v2.3",
    }
