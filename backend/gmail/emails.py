"""HTML email builders for Gmail integration."""

from __future__ import annotations

from typing import Any

GMAIL_RED = "#EA4335"
GMAIL_GREEN = "#34A853"


def _base_html(title: str, body_content: str, footer_text: str) -> str:
    """Wrap body content in a clean, inline-CSS email template."""
    return f"""\
<html>
<body style="margin:0;padding:0;font-family:Arial,Helvetica,sans-serif;background:#f4f4f4;">
<table width="100%" cellpadding="0" cellspacing="0" style="padding:20px;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;">
  <tr>
    <td style="background:#1a1a2e;padding:16px 24px;">
      <span style="color:#ffffff;font-size:18px;font-weight:bold;">{title}</span>
    </td>
  </tr>
  <tr>
    <td style="padding:24px;">
      {body_content}
    </td>
  </tr>
  <tr>
    <td style="padding:12px 24px;background:#f8f8f8;font-size:12px;color:#888;">
      {footer_text}
    </td>
  </tr>
</table>
</td></tr>
</table>
</body>
</html>"""


def build_resolution_email(
    *,
    event_id: str,
    traveler_name: str,
    cancelled_flight: str,
    origin: str,
    destination: str,
    chosen_flight: str,
    departure: str,
    arrival: str,
    price: float,
    price_delta: str,
    confidence: float,
    message_text: str,
) -> dict[str, str]:
    """Build an HTML email for a resolution proposal."""
    body = f"""\
<p style="font-size:15px;color:#333;line-height:1.6;">{message_text}</p>
<table width="100%" cellpadding="8" cellspacing="0" style="margin-top:16px;border-collapse:collapse;">
  <tr style="background:#f0f0f0;">
    <td style="font-size:13px;color:#666;font-weight:bold;">Cancelled</td>
    <td style="font-size:13px;color:#333;">{cancelled_flight}</td>
    <td style="font-size:13px;color:#666;font-weight:bold;">Route</td>
    <td style="font-size:13px;color:#333;">{origin} \u2192 {destination}</td>
  </tr>
  <tr>
    <td style="font-size:13px;color:#666;font-weight:bold;">Rebooked</td>
    <td style="font-size:13px;color:#333;">{chosen_flight}</td>
    <td style="font-size:13px;color:#666;font-weight:bold;">Price</td>
    <td style="font-size:13px;color:#333;">${price:.2f} ({price_delta})</td>
  </tr>
  <tr style="background:#f0f0f0;">
    <td style="font-size:13px;color:#666;font-weight:bold;">Departure</td>
    <td style="font-size:13px;color:#333;">{departure}</td>
    <td style="font-size:13px;color:#666;font-weight:bold;">Arrival</td>
    <td style="font-size:13px;color:#333;">{arrival}</td>
  </tr>
</table>"""

    subject = f"Flight Resolution for {traveler_name}"
    html_body = _base_html(
        title=subject,
        body_content=body,
        footer_text=f"Confidence: {confidence:.0%} | Mundostra Travel OS",
    )
    return {"subject": subject, "html_body": html_body}


def build_confirmation_email(
    *,
    traveler_name: str,
    chosen_flight: str,
    departure: str,
) -> dict[str, str]:
    """Build an HTML email for booking confirmation."""
    body = f"""\
<p style="font-size:15px;color:#333;line-height:1.6;">
  {traveler_name} &mdash; <strong>{chosen_flight}</strong> departing {departure}<br>
  Your card has been authorized and the seat is reserved.
</p>
<div style="margin-top:16px;padding:12px;background:#e6f4ea;border-radius:6px;text-align:center;">
  <span style="color:{GMAIL_GREEN};font-size:16px;font-weight:bold;">\u2713 Booking Confirmed</span>
</div>"""

    subject = "Booking Confirmed"
    html_body = _base_html(
        title=subject,
        body_content=body,
        footer_text="Mundostra Travel OS \u2014 confirmed",
    )
    return {"subject": subject, "html_body": html_body}


def build_options_email(
    *,
    traveler_name: str,
    alternatives: list[dict[str, Any]],
) -> dict[str, str]:
    """Build an HTML email listing alternatives."""
    rows = ""
    for i, alt in enumerate(alternatives[:5], 1):
        flight = alt.get("flight", "???")
        dep = alt.get("departure", "")
        price = alt.get("price", 0)
        conflict = ' <span style="color:#d93025;">\u26a0 calendar conflict</span>' if alt.get("calendar_conflict") else ""
        bg = "background:#f0f0f0;" if i % 2 == 0 else ""
        rows += (
            f'<tr style="{bg}">'
            f'<td style="padding:8px;font-size:13px;color:#333;">{i}.</td>'
            f'<td style="padding:8px;font-size:13px;color:#333;font-weight:bold;">{flight}</td>'
            f'<td style="padding:8px;font-size:13px;color:#333;">${price:.2f}</td>'
            f'<td style="padding:8px;font-size:13px;color:#333;">{dep}{conflict}</td>'
            f"</tr>"
        )

    body = f"""\
<p style="font-size:15px;color:#333;">Here are the available alternatives:</p>
<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;margin-top:12px;">
  <tr style="background:#1a1a2e;">
    <th style="padding:8px;font-size:12px;color:#fff;text-align:left;">#</th>
    <th style="padding:8px;font-size:12px;color:#fff;text-align:left;">Flight</th>
    <th style="padding:8px;font-size:12px;color:#fff;text-align:left;">Price</th>
    <th style="padding:8px;font-size:12px;color:#fff;text-align:left;">Departure</th>
  </tr>
  {rows}
</table>"""

    subject = f"Available Alternatives for {traveler_name}"
    html_body = _base_html(
        title=subject,
        body_content=body,
        footer_text="Mundostra Travel OS \u2014 options",
    )
    return {"subject": subject, "html_body": html_body}
