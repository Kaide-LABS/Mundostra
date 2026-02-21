"""Tests for OCR extraction module."""

from __future__ import annotations

import pytest

from backend.ocr.extractor import extract_from_image


class TestOcrExtractor:
    """Unit tests for boarding pass OCR extraction."""

    @pytest.mark.asyncio
    async def test_mock_extraction_returns_valid_fields(self) -> None:
        result = await extract_from_image("fake-base64-data", mock_llm=True)
        assert result.success is True
        assert result.flight_number == "UA 2381"
        assert result.origin == "SFO"
        assert result.destination == "JFK"
        assert result.passenger_name == "Sarah Chen"

    @pytest.mark.asyncio
    async def test_mock_extraction_all_required_fields_populated(self) -> None:
        result = await extract_from_image("fake-base64-data", mock_llm=True)
        assert result.flight_number is not None
        assert result.origin is not None
        assert result.destination is not None
        assert len(result.fields_found) >= 3

    @pytest.mark.asyncio
    async def test_mock_extraction_has_raw_text(self) -> None:
        result = await extract_from_image("fake-base64-data", mock_llm=True)
        assert result.raw_text != ""
