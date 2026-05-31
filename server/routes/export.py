from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from database import searches_collection
from datetime import datetime
import json
import csv
import io
from dicttoxml import dicttoxml
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

router = APIRouter(prefix="/api/export", tags=["Data Export"])


async def get_all_searches() -> list:
    """Fetch all searches from database for export."""
    cursor = searches_collection.find().sort("created_at", -1)
    searches = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        # Convert datetime fields to strings
        for field in ["date_from", "date_to", "created_at", "updated_at"]:
            if isinstance(doc.get(field), datetime):
                doc[field] = doc[field].isoformat()
        searches.append(doc)
    return searches


def flatten_search(doc: dict) -> dict:
    """Flatten nested weather data for tabular export."""
    flat = {
        "id": doc.get("_id", ""),
        "location": doc.get("location", ""),
        "latitude": doc.get("latitude", ""),
        "longitude": doc.get("longitude", ""),
        "country": doc.get("country", ""),
        "date_from": doc.get("date_from", ""),
        "date_to": doc.get("date_to", ""),
        "created_at": doc.get("created_at", ""),
        "updated_at": doc.get("updated_at", ""),
    }
    weather = doc.get("weather_data") or {}
    flat["temperature"] = weather.get("temperature", "")
    flat["feels_like"] = weather.get("feels_like", "")
    flat["humidity"] = weather.get("humidity", "")
    flat["pressure"] = weather.get("pressure", "")
    flat["wind_speed"] = weather.get("wind_speed", "")
    flat["description"] = weather.get("description", "")
    return flat


@router.get("/json")
async def export_json():
    """Export all search records as JSON."""
    searches = await get_all_searches()
    content = json.dumps(searches, indent=2, default=str)
    return StreamingResponse(
        io.BytesIO(content.encode()),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=weather_searches.json"},
    )


@router.get("/csv")
async def export_csv():
    """Export all search records as CSV."""
    searches = await get_all_searches()
    if not searches:
        return StreamingResponse(
            io.BytesIO(b"No data to export"),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=weather_searches.csv"},
        )

    flat_data = [flatten_search(doc) for doc in searches]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=flat_data[0].keys())
    writer.writeheader()
    writer.writerows(flat_data)

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=weather_searches.csv"},
    )


@router.get("/xml")
async def export_xml():
    """Export all search records as XML."""
    searches = await get_all_searches()
    xml_bytes = dicttoxml(searches, custom_root="weather_searches", attr_type=False)

    return StreamingResponse(
        io.BytesIO(xml_bytes),
        media_type="application/xml",
        headers={"Content-Disposition": "attachment; filename=weather_searches.xml"},
    )


@router.get("/markdown")
async def export_markdown():
    """Export all search records as Markdown."""
    searches = await get_all_searches()

    md_lines = ["# Weather Search Records\n"]
    md_lines.append(f"*Exported on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*\n")
    md_lines.append(f"**Total Records:** {len(searches)}\n")
    md_lines.append("---\n")

    for i, doc in enumerate(searches, 1):
        weather = doc.get("weather_data") or {}
        md_lines.append(f"## {i}. {doc.get('location', 'Unknown')}\n")
        md_lines.append(f"- **Coordinates:** {doc.get('latitude', 'N/A')}, {doc.get('longitude', 'N/A')}")
        md_lines.append(f"- **Date Range:** {doc.get('date_from', 'N/A')} to {doc.get('date_to', 'N/A')}")
        md_lines.append(f"- **Temperature:** {weather.get('temperature', 'N/A')}°C (Feels like {weather.get('feels_like', 'N/A')}°C)")
        md_lines.append(f"- **Humidity:** {weather.get('humidity', 'N/A')}%")
        md_lines.append(f"- **Wind Speed:** {weather.get('wind_speed', 'N/A')} m/s")
        md_lines.append(f"- **Pressure:** {weather.get('pressure', 'N/A')} hPa")
        md_lines.append(f"- **Description:** {weather.get('description', 'N/A')}")
        md_lines.append(f"- **Created:** {doc.get('created_at', 'N/A')}")
        md_lines.append("")

        # Include forecast if available
        forecast = doc.get("forecast") or []
        if forecast:
            md_lines.append("### 5-Day Forecast\n")
            md_lines.append("| Date | High | Low | Humidity | Wind | Description |")
            md_lines.append("|------|------|-----|----------|------|-------------|")
            for day in forecast:
                md_lines.append(
                    f"| {day.get('date', '')} | {day.get('temp_high', '')}°C | {day.get('temp_low', '')}°C | "
                    f"{day.get('humidity', '')}% | {day.get('wind_speed', '')} m/s | {day.get('description', '')} |"
                )
            md_lines.append("")

        md_lines.append("---\n")

    content = "\n".join(md_lines)
    return StreamingResponse(
        io.BytesIO(content.encode()),
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=weather_searches.md"},
    )


@router.get("/pdf")
async def export_pdf():
    """Export all search records as PDF."""
    searches = await get_all_searches()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("Weather Search Records", styles["Title"]))
    elements.append(Paragraph(
        f"Exported on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} | Total Records: {len(searches)}",
        styles["Normal"],
    ))
    elements.append(Spacer(1, 20))

    if not searches:
        elements.append(Paragraph("No data to export.", styles["Normal"]))
    else:
        # Table data
        headers = ["Location", "Lat", "Lon", "Temp (°C)", "Humidity", "Wind", "Description", "Date From"]
        table_data = [headers]

        for doc_item in searches:
            weather = doc_item.get("weather_data") or {}
            row = [
                str(doc_item.get("location", ""))[:20],
                str(round(doc_item.get("latitude", 0), 2)),
                str(round(doc_item.get("longitude", 0), 2)),
                str(weather.get("temperature", "N/A")),
                str(weather.get("humidity", "N/A")),
                str(weather.get("wind_speed", "N/A")),
                str(weather.get("description", "N/A"))[:20],
                str(doc_item.get("date_from", "N/A"))[:10],
            ]
            table_data.append(row)

        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f5")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=weather_searches.pdf"},
    )
