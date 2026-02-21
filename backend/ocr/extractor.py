"""OCR extraction from boarding pass / ticket images via Gemini Vision."""

from __future__ import annotations

import asyncio
import base64
import json
from dataclasses import dataclass, field


@dataclass
class OcrResult:
    flight_number: str | None = None
    origin: str | None = None
    destination: str | None = None
    passenger_name: str | None = None
    departure_date: str | None = None
    success: bool = False
    raw_text: str = ""
    fields_found: list[str] = field(default_factory=list)


_EXTRACTION_PROMPT = """Analyze this boarding pass or flight ticket image. Extract the following fields as JSON:

{
  "flight_number": "airline code + number, e.g. UA 2381",
  "origin": "3-letter IATA airport code, e.g. SFO",
  "destination": "3-letter IATA airport code, e.g. JFK",
  "passenger_name": "full name on the ticket",
  "departure_date": "date in YYYY-MM-DD format if visible"
}

If a field is not visible or cannot be determined, set it to null.
Return ONLY the JSON object, no other text."""


def _mock_extract() -> OcrResult:
    """Deterministic mock extraction for demo/test mode."""
    return OcrResult(
        flight_number="UA 2381",
        origin="SFO",
        destination="JFK",
        passenger_name="Sarah Chen",
        departure_date=None,
        success=True,
        raw_text="[mock OCR extraction]",
        fields_found=["flight_number", "origin", "destination", "passenger_name"],
    )


async def extract_from_image(image_base64: str, mock_llm: bool = True) -> OcrResult:
    """Extract flight details from a boarding pass image.

    Args:
        image_base64: Base64-encoded image (may include data URI prefix).
        mock_llm: If True, return deterministic mock data.

    Returns:
        OcrResult with extracted fields.
    """
    if mock_llm:
        return _mock_extract()

    # Strip data URI prefix if present
    if "," in image_base64:
        header, image_base64 = image_base64.split(",", 1)
        mime_type = header.split(":")[1].split(";")[0] if ":" in header else "image/jpeg"
    else:
        mime_type = "image/jpeg"

    image_bytes = base64.b64decode(image_base64)

    def _sync_call() -> OcrResult:
        from google.cloud import aiplatform
        from vertexai.generative_models import GenerativeModel, Part

        from backend.config import get_settings

        settings = get_settings()
        aiplatform.init(project=settings.gcp_project_id, location=settings.gcp_location)

        model = GenerativeModel(settings.research_model_id)
        image_part = Part.from_data(data=image_bytes, mime_type=mime_type)

        response = model.generate_content(
            [image_part, _EXTRACTION_PROMPT],  # type: ignore[arg-type]
            generation_config={"response_mime_type": "application/json"},
        )

        raw = response.text
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return OcrResult(success=False, raw_text=raw)

        found = [k for k, v in data.items() if v is not None]
        return OcrResult(
            flight_number=data.get("flight_number"),
            origin=data.get("origin"),
            destination=data.get("destination"),
            passenger_name=data.get("passenger_name"),
            departure_date=data.get("departure_date"),
            success=True,
            raw_text=raw,
            fields_found=found,
        )

    return await asyncio.to_thread(_sync_call)
