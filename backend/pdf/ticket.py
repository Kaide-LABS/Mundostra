"""Generate branded ticket PDF using fpdf2."""

from __future__ import annotations

from fpdf import FPDF


def generate_ticket_pdf(
    passenger_name: str,
    flight_number: str,
    origin: str,
    destination: str,
    departure: str,
    arrival: str,
    booking_ref: str,
    price: float,
    event_id: str,
) -> bytes:
    """Generate a single-page branded ticket PDF.

    Returns:
        PDF file content as bytes.
    """
    pdf = FPDF(orientation="L", unit="mm", format=(100, 210))
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    # Purple header bar
    pdf.set_fill_color(124, 58, 237)  # purple-600
    pdf.rect(0, 0, 210, 22, "F")

    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(8, 4)
    pdf.cell(0, 14, "MUNDOSTRA", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 7)
    pdf.set_xy(8, 15)
    pdf.cell(0, 5, "Electronic Ticket / Boarding Pass", new_x="LMARGIN", new_y="NEXT")

    # Passenger info
    pdf.set_text_color(80, 80, 80)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_xy(8, 28)
    pdf.cell(0, 5, "PASSENGER", new_x="LMARGIN", new_y="NEXT")

    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_xy(8, 33)
    pdf.cell(0, 6, passenger_name.upper(), new_x="LMARGIN", new_y="NEXT")

    # Flight info grid
    y = 44
    col_w = 48

    labels = ["FLIGHT", "FROM", "TO", "BOOKING REF"]
    values = [flight_number, origin, destination, booking_ref]

    for i, (label, value) in enumerate(zip(labels, values, strict=True)):
        x = 8 + i * col_w
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(120, 120, 120)
        pdf.set_xy(x, y)
        pdf.cell(col_w, 4, label)

        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(30, 30, 30)
        pdf.set_xy(x, y + 5)
        pdf.cell(col_w, 6, value)

    # Times row
    y2 = 60
    time_labels = ["DEPARTURE", "ARRIVAL", "PRICE"]
    time_values = [departure, arrival, f"${price:.2f} USD"]

    for i, (label, value) in enumerate(zip(time_labels, time_values, strict=True)):
        x = 8 + i * 65
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(120, 120, 120)
        pdf.set_xy(x, y2)
        pdf.cell(65, 4, label)

        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(30, 30, 30)
        pdf.set_xy(x, y2 + 5)
        pdf.cell(65, 5, value)

    # Dashed separator
    pdf.set_draw_color(200, 200, 200)
    pdf.set_dash_pattern(dash=2, gap=2)
    pdf.line(8, 76, 202, 76)

    # Footer
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(150, 150, 150)
    pdf.set_xy(8, 80)
    pdf.cell(0, 4, f"Event ID: {event_id}")
    pdf.set_xy(8, 85)
    pdf.cell(0, 4, "This is an electronic ticket. Please present this document at check-in.")

    # Purple bottom bar
    pdf.set_fill_color(124, 58, 237)
    pdf.rect(0, 94, 210, 6, "F")

    return bytes(pdf.output())  # type: ignore[arg-type]
