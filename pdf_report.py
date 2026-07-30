from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)


def generate_pdf(
    result,
    rank,
    course,
    college_type,
    candidate_category,
    alloted_category,
    best_match_college,
    best_match_rank
):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(8.27 * inch, 11.69 * inch),  # A4
        rightMargin=25,
        leftMargin=25,
        topMargin=15,
        bottomMargin=25
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=22,
        alignment=TA_CENTER,
        textColor=colors.white,
        spaceAfter=10
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=colors.HexColor("#0F4C81"),
        spaceBefore=15,
        spaceAfter=10
    )

    normal_style = ParagraphStyle(
        "Normal",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=11,
        leading=18,
        alignment=TA_LEFT
    )

    elements = []

    # ==================================================
    # Logo
    # ==================================================

    logo = Image("logo.jpg")
    logo.drawWidth = 200
    logo.drawHeight = logo.imageHeight * 200 / logo.imageWidth
    logo.hAlign = "CENTER"

    elements.append(logo)
    # ==================================================
    # Candidate Information
    # ==================================================

    elements.append(
        Paragraph(
            "Candidate Information",
            heading_style
        )
    )

    candidate_data = [
        ["Your Rank", str(int(rank))],
        ["Course", course],
        ["College Type", college_type],
        ["Candidate Category", candidate_category],
        ["Allotted Category", alloted_category],
    ]

    candidate_table = Table(
        candidate_data,
        colWidths=[170, 330]
    )

    candidate_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F1FB")),
        ("BACKGROUND", (1, 0), (1, -1), colors.white),

        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#0F4C81")),

        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),

        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(candidate_table)
    elements.append(Spacer(1, 20))

    # ==================================================
    # Best Match College
    # ==================================================

    elements.append(
        Paragraph(
            "Best Match College",
            heading_style
        )
    )

    best_match = Table(
        [[
            Paragraph(
                f"""
                <font size=15>
                <b>{best_match_college}</b>
                </font>

                <br/><br/>

                <b>Previous Year Closing Rank:</b> {best_match_rank}
                """,
                normal_style
            )
        ]],
        colWidths=[500]
    )

    best_match.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF8E6")),
        ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#F4B400")),
        ("TOPPADDING", (0, 0), (-1, -1), 15),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
        ("LEFTPADDING", (0, 0), (-1, -1), 15),
        ("RIGHTPADDING", (0, 0), (-1, -1), 15),
    ]))

    elements.append(best_match)
    elements.append(Spacer(1, 20))
    # ==================================================
    # Prediction Summary
    # ==================================================

    high = (result["Chance"] == "🟢 High Chance").sum()
    borderline = (result["Chance"] == "🟡 Borderline").sum()
    tough = (result["Chance"] == "🔴 Tough Chance").sum()

    elements.append(
        Paragraph(
            "Prediction Summary",
            heading_style
        )
    )

    summary_data = [
        ["Total Colleges", str(len(result))],
        ["High Chance", str(high)],
        ["Borderline", str(borderline)],
        ["Tough Chance", str(tough)]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[220, 100]
    )

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#D9EDF7")),
        ("BACKGROUND", (1, 0), (1, -1), colors.white),

        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#0F4C81")),

        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),

        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 20))
        # ==================================================
    # Recommended Colleges
    # ==================================================

    elements.append(
        Paragraph(
            "Recommended Colleges",
            heading_style
        )
    )

    table_data = [
        ["S.No", "College Name", "Closing Rank", "Chance"]
    ]

    for _, row in result.iterrows():

        table_data.append([
            str(row["S.No"]),
            Paragraph(str(row["College Name"]), normal_style),
            str(int(row["Closing Rank"])),  
            row["Chance"]
        ])

    college_table = Table(
        table_data,
        colWidths=[45, 285, 70, 100],
        repeatRows=1
    )

    style = [

        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F4C81")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),

        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]

    for i in range(1, len(table_data)):

        if i % 2 == 0:
            style.append(
                ("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F7FBFF"))
            )
        else:
            style.append(
                ("BACKGROUND", (0, i), (-1, i), colors.white)
            )

    for i in range(1, len(table_data)):

        chance = table_data[i][3]

        if "High" in chance:
            style.append(("TEXTCOLOR", (3, i), (3, i), colors.green))
            style.append(("FONTNAME", (3, i), (3, i), "Helvetica-Bold"))

        elif "Borderline" in chance:
            style.append(("TEXTCOLOR", (3, i), (3, i), colors.orange))
            style.append(("FONTNAME", (3, i), (3, i), "Helvetica-Bold"))

        else:
            style.append(("TEXTCOLOR", (3, i), (3, i), colors.red))
            style.append(("FONTNAME", (3, i), (3, i), "Helvetica-Bold"))

    college_table.setStyle(TableStyle(style))

    elements.append(college_table)

    elements.append(Spacer(1, 20))

    # ==================================================
    # Footer
    # ==================================================

    elements.append(
        Paragraph(
            "<b>Prepared By:</b> KunaL",
            normal_style
        )
    )

    elements.append(Spacer(1, 6))

    elements.append(
        Paragraph(
            "<b>Team:</b> Pulse Point",
            normal_style
        )
    )

    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(
            """
            <font color="grey" size="9">
            This report is generated using previous year's Kerala Medical College
            counselling data. Predictions are for guidance purposes only and
            should not be considered official admission results.
            </font>
            """,
            styles["BodyText"]
        )
    )

    elements.append(Spacer(1, 8))

    elements.append(
        Paragraph(
            "<font color='grey' size='9'><b>© 2026 Pulse Point | All Rights Reserved</b></font>",
            styles["BodyText"]
        )
    )

    # ==================================================
    # Build PDF
    # ==================================================

    doc.build(elements)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf