"""Mock virtual card API — simulates Stripe Issuing / Marqeta."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/mock/cards", tags=["mock"])


class CardAuthorizationRequest(BaseModel):
    booking_ref: str
    amount: float
    currency: str = "USD"
    merchant: str = ""


@router.post("/authorize")
async def authorize_card(request: CardAuthorizationRequest) -> dict[str, object]:
    return {
        "authorization_id": str(uuid4()),
        "booking_ref": request.booking_ref,
        "amount": request.amount,
        "currency": request.currency,
        "status": "approved",
        "card_last_four": "4242",
        "merchant": request.merchant,
    }
