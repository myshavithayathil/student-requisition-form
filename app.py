
import os
import re
from io import BytesIO
from datetime import date
from xml.sax.saxutils import escape

import pandas as pd
import streamlit as st

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Student Academic Requisition Form",
    page_icon="📄",
    layout="wide"
)


# --------------------------------------------------
# PDF FONT CONFIGURATION
# --------------------------------------------------

FONT = "Helvetica"
BOLD_FONT = "Helvetica-Bold"

font_options = [
    (
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf"
    ),
    (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    )
]

for regular_path, bold_path in font_options:
    if os.path.exists(regular_path) and os.path.exists(bold_path):
        try:
            pdfmetrics.registerFont(
                TTFont("CustomRegular", regular_path)
            )
            pdfmetrics.registerFont(
                TTFont("CustomBold", bold_path)
            )

            FONT = "CustomRegular"
            BOLD_FONT = "CustomBold"
            break

        except Exception:
            continue


# --------------------------------------------------
# APPLICATION TITLE
# --------------------------------------------------

st.title("Student Academic Requisition Form")

st.caption(
    "Fill in your academic details and generate your "
    "Student Academic Requisition PDF."
)

st.divider()


# --------------------------------------------------
# STUDENT FORM
# --------------------------------------------------

with st.form("requisition_form"):

    st.subheader("Student Details")

    col1, col2, col3 = st.columns(3)

    with col1:
        department = st.text_input(
            "Name of Department *",
            placeholder="e.g. EXCS"
        )

    with col2:
        student_name = st.text_input(
            "Name of Student *",
            placeholder="Enter your full name"
        )

    with col3:
        roll_no = st.text_input(
            "Roll Number *",
            placeholder="Enter your roll number"
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        semester = st.selectbox(
            "Semester *",
            [
                "Select",
                "1", "2", "3", "4",
                "5", "6", "7", "8"
            ]
        )

    with col5:
        division = st.text_input(
            "Division *",
            placeholder="e.g. A"
        )

    with col6:
        contact = st.text_input(
            "Email / Mobile *",
            placeholder="Enter email or 10-digit mobile"
        )

    st.subheader("Application Details")

    application_type = st.selectbox(
        "Application Type *",
        [
            "Select",
            "Bonafide",
            "Student Certificate",
            "Scholarship",
            "NOC",
            "Academic Permission",
            "Examination",
            "Internship",
            "Placement",
            "Other Request"
        ]
    )

    purpose = st.text_area(
        "Purpose / Brief Details of Request *",
        placeholder=(
            "Explain why you need this request. "
            "For example: I require a bonafide certificate "
            "as proof of enrollment for bank account formalities."
        ),
        height=120
    )

    st.subheader("Supporting Documents")

    col7, col8 = st.columns(2)

    with col7:
        documents_attached = st.radio(
            "Are supporting documents attached?",
            ["Yes", "No"],
            horizontal=True
        )

    with col8:
        document_names = st.text_input(
            "Name of Supporting Document(s)",
            placeholder="e.g. Bank request letter"
        )

    request_date = st.date_input(
        "Date",
        value=date.today()
    )

    st.subheader("Student Declaration")

    declaration_text = (
        "I certify that the information provided above is correct "
        "and that the request is being submitted for academic "
        "purposes. I understand that the request will be processed "
        "as per applicable Institute/University rules and within "
        "the stipulated processing time."
    )

    st.info(declaration_text)

    declaration_accepted = st.checkbox(
        "I have read and accept the student declaration."
    )

    submitted = st.form_submit_button(
        "Generate PDF",
        type="primary",
        use_container_width=True
    )


# --------------------------------------------------
# PDF GENERATION FUNCTION
# --------------------------------------------------

def generate_pdf(data):

    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="Student Academic Requisition Form"
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "FormTitle",
        parent=styles["Title"],
        fontName=BOLD_FONT,
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        "FormSubtitle",
        parent=styles["Normal"],
        fontName=FONT,
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        spaceAfter=10
    )

    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading3"],
        fontName=BOLD_FONT,
        fontSize=10,
        leading=13,
        spaceBefore=9,
        spaceAfter=5
    )

    normal_style = ParagraphStyle(
        "FormBody",
        parent=styles["Normal"],
        fontName=FONT,
        fontSize=9,
        leading=12,
        spaceAfter=2,
        wordWrap="LTR"
    )

    small_style = ParagraphStyle(
        "SmallBody",
        parent=normal_style,
        fontSize=8,
        leading=10
    )

    story = []

    def P(value, style=normal_style):
        return Paragraph(
            escape(str(value)).replace("\n", "<br/>"),
            style
        )

    def section(title):
        story.append(Paragraph(title, section_style))

    def make_table(rows, widths, heights=None):
        table = Table(
            rows,
            colWidths=widths,
            rowHeights=heights,
            repeatRows=0,
            hAlign="LEFT"
        )

        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.65, colors.black),
            ("FONTNAME", (0, 0), (-1, -1), FONT),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))

        story.append(table)

    # Official form heading
    story.append(Paragraph(
        "STUDENT ACADEMIC REQUISITION FORM",
        title_style
    ))

    story.append(Paragraph(
        "(Autonomous College Affiliated to University of Mumbai)",
        subtitle_style
    ))

    # Department and date
    story.append(Paragraph(
        "<b>Name of the Department</b>",
        section_style
    ))

    make_table([
        [
            P("Department: " + data["Department"]),
            P("Department Outward No.: __________________")
        ],
        [
            P("Date: " + data["Date"]),
            P("Processing Time: Normally 4 working days")
        ]
    ], [85 * mm, 85 * mm])

    story.append(Spacer(1, 5))

    story.append(P(
        "Processing Time: The request will normally be processed "
        "within 4 working days after receiving the completed form "
        "and all required supporting documents. Students are advised "
        "to apply in advance, as incomplete applications may require "
        "additional processing time.",
        small_style
    ))

    # Student details
    section("1. STUDENT DETAILS")

    make_table([
        [P("Name of Student: " + data["Student Name"])],
        [
            P(
                "Roll No.: " + data["Roll Number"]
                + "       Semester: " + data["Semester"]
                + "       Division: " + data["Division"]
            )
        ],
        [P("Email / Mobile: " + data["Contact"])],
        [P("Application for: " + data["Application Type"])]
    ], [170 * mm])

    # Purpose
    section("2. PURPOSE / BRIEF DETAILS OF REQUEST")

    purpose_rows = [
        [P(data["Purpose"])]
    ]

    make_table(purpose_rows, [170 * mm])

    # Supporting documents
    section("3. SUPPORTING DOCUMENTS")

    make_table([
        [
            P(
                "Documents attached:     "
                + ("☐ Yes    ☒ No" if data["Documents Attached"] == "No"
                   else "☒ Yes    ☐ No")
            )
        ],
        [
            P(
                "Document name(s), if applicable: "
                + (data["Document Names"] or "N/A")
            )
        ]
    ], [170 * mm])

    # Declaration
    section("4. STUDENT DECLARATION")

    story.append(P(declaration_text))

    story.append(Spacer(1, 10))

    make_table([
        [
            P("Student Signature: ____________________"),
            P("Date: ____________________")
        ]
    ], [85 * mm, 85 * mm])

    # HoD approval
    section("5. HoD Signature")

    make_table([
        [
            P("HoD Signature: ____________________"),
            P("Remarks: ____________________")
        ],
        [
            P(
                "Forwarded to (VICE PRINCIPAL / CHIEF ACADEMIC "
                "OFFICER / ACCOUNTS / SPORTS / PLACEMENT CELL / "
                "SCHOLARSHIP CELL / EXAM CELL), if required",
                small_style
            ),
            P("")
        ],
        [
            P("Signature: ____________________"),
            P("Remarks: ____________________")
        ]
    ], [85 * mm, 85 * mm])

    # Principal office
    section("6. PRINCIPAL OFFICE USE ONLY")

    make_table([
        [
            P(
                "Decision by Principal: "
                "☐ Approved    ☐ Not Approved    "
                "☐ Clarification Required",
                small_style
            )
        ],
        [P("Remarks (if any):")],
        [P("Principal Signature: ____________________")]
    ], [170 * mm])

    pdf.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# --------------------------------------------------
# VALIDATION AND SUBMISSION
# --------------------------------------------------

if submitted:

    errors = []

    required_fields = {
        "Department": department,
        "Student Name": student_name,
        "Roll Number": roll_no,
        "Division": division,
        "Contact": contact,
        "Purpose": purpose
    }

    for field, value in required_fields.items():
        if not value.strip():
            errors.append(f"{field} is required.")

    if semester == "Select":
        errors.append("Please select your semester.")

    if application_type == "Select":
        errors.append("Please select an application type.")

    # Validate email or 10-digit mobile number
    contact_value = contact.strip()

    email_pattern = r"[^@\s]+@[^@\s]+\.[^@\s]+"
    mobile_pattern = r"[0-9]{10}"

    if contact_value:
        if not (
            re.fullmatch(email_pattern, contact_value)
            or re.fullmatch(mobile_pattern, contact_value)
        ):
            errors.append(
                "Enter a valid email address or a 10-digit mobile number."
            )

    if documents_attached == "Yes" and not document_names.strip():
        errors.append(
            "Enter the name of the supporting document(s)."
        )

    if not declaration_accepted:
        errors.append(
            "You must accept the student declaration before submission."
        )

    if errors:
        for error in errors:
            st.error(error)

    else:

        data = {
            "Department": department.strip(),
            "Student Name": student_name.strip(),
            "Roll Number": roll_no.strip(),
            "Semester": semester,
            "Division": division.strip(),
            "Contact": contact.strip(),
            "Application Type": application_type,
            "Purpose": purpose.strip(),
            "Documents Attached": documents_attached,
            "Document Names": document_names.strip(),
            "Date": str(request_date)
        }

        try:
            # Generate PDF
            pdf_bytes = generate_pdf(data)

            # Save submission to CSV
            csv_file = "submissions.csv"

            df = pd.DataFrame([data])

            df.to_csv(
                csv_file,
                mode="a",
                header=not os.path.exists(csv_file),
                index=False,
                encoding="utf-8"
            )

            # Prepare filename
            safe_roll = re.sub(
                r"[^A-Za-z0-9_-]", "_", roll_no.strip()
            )

            safe_name = re.sub(
                r"[^A-Za-z0-9_-]", "_", student_name.strip()
            )

            filename = (
                f"Requisition_{safe_roll}_{safe_name}.pdf"
            )

            st.success("Your requisition form is ready!")

            st.download_button(
                label="Download Requisition PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

        except Exception as error:
            st.error(
                "Something went wrong while generating the form. "
                "Please check the error and try again."
            )
            st.exception(error)
