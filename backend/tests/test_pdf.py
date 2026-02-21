"""Tests for ticket PDF generation."""

from __future__ import annotations

from backend.pdf.ticket import generate_ticket_pdf


class TestTicketPdf:
    """Unit tests for PDF generation."""

    def test_generates_valid_pdf_bytes(self) -> None:
        pdf_bytes = generate_ticket_pdf(
            passenger_name="Sarah Chen",
            flight_number="UA 2381",
            origin="SFO",
            destination="JFK",
            departure="2026-02-21 14:30",
            arrival="2026-02-21 23:15",
            booking_ref="MUN-CHAT-abc12345",
            price=450.00,
            event_id="test-event-123",
        )
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes[:5] == b"%PDF-"

    def test_reasonable_file_size(self) -> None:
        pdf_bytes = generate_ticket_pdf(
            passenger_name="Sarah Chen",
            flight_number="UA 2381",
            origin="SFO",
            destination="JFK",
            departure="2026-02-21 14:30",
            arrival="2026-02-21 23:15",
            booking_ref="MUN-CHAT-abc12345",
            price=450.00,
            event_id="test-event-123",
        )
        # Should be a small, single-page PDF (under 50KB)
        assert len(pdf_bytes) > 100
        assert len(pdf_bytes) < 50_000

    def test_different_inputs_produce_different_pdfs(self) -> None:
        pdf1 = generate_ticket_pdf(
            passenger_name="Alice",
            flight_number="DL 100",
            origin="LAX",
            destination="ORD",
            departure="2026-03-01 08:00",
            arrival="2026-03-01 14:00",
            booking_ref="REF-001",
            price=200.00,
            event_id="evt-1",
        )
        pdf2 = generate_ticket_pdf(
            passenger_name="Bob",
            flight_number="AA 200",
            origin="JFK",
            destination="MIA",
            departure="2026-03-02 10:00",
            arrival="2026-03-02 13:00",
            booking_ref="REF-002",
            price=300.00,
            event_id="evt-2",
        )
        assert pdf1 != pdf2
