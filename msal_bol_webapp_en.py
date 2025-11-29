import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.cidfonts import CIDFont
import io
import os

# ----------------------------------------------------------------------
# 1. Styles and Configuration (English Only)
# ----------------------------------------------------------------------

# Using standard ReportLab fonts to avoid dependency issues (Arial.ttf)
base_font = "Helvetica"
styles = getSampleStyleSheet()

green_color = colors.HexColor("#008000")
black_color = colors.black
light_gray_color = colors.HexColor("#EEEEEE")

# Define styles using standard fonts
styles.add(ParagraphStyle(name='MyTitleGreen', fontName=base_font + '-Bold', fontSize=16, leading=20, alignment=1, textColor=green_color, allowOrphans=0, allowWidows=0))
styles.add(ParagraphStyle(name='MyFieldLabelGreen', fontName=base_font + '-Bold', fontSize=8, leading=10, textColor=green_color, spaceBefore=2, spaceAfter=2, alignment=0, allowOrphans=0, allowWidows=0))
styles.add(ParagraphStyle(name='MyFieldValueBlack', fontName=base_font, fontSize=9, leading=11, textColor=black_color, spaceBefore=2, spaceAfter=2, alignment=0, allowOrphans=0, allowWidows=0))
styles.add(ParagraphStyle(name='SmallBlack', fontName=base_font, fontSize=7, leading=9, textColor=black_color, alignment=0, allowOrphans=0, allowWidows=0))


# Helper function to create paragraphs and handle line breaks
def create_cell_content(label, value, is_label=True, font_style='MyFieldValueBlack'):
    style = styles['MyFieldLabelGreen'] if is_label else styles[font_style]
    content = value.replace("\n", "<br/>") if not is_label else label
    return Paragraph(content, style)


# ----------------------------------------------------------------------
# 2. Streamlit Interface and Data Input
# ----------------------------------------------------------------------

st.set_page_config(layout="wide")
st.title("MSAL Shipping - Bill of Lading Generator 🚢")

# NOTE: The logo file (msal_logo.png) must be present in the same directory.
logo_path = "msal_logo.png"

# Define fields based on the document layout
fields_map = {
    "(2) Shipper / Exporter": "Shipper / Exporter",
    "(3) Consignee(complete name and address)": "Consignee",
    "(4) Notify Party (complete name and address)": "Notify Party",
    "(5) Document No.": "Document No.",
    "(6) Export References": "Export References",
    "(7) Forwarding Agent-References": "Forwarding Agent-References",
    "(8) Point and Country of Origin (for the Merchant's reference only)": "Point & Country of Origin",
    "(9) Also Notify Party (complete name and address)": "Also Notify Party",
    "(10) Onward Inland Routing/Export Instructions": "Export Instructions",
    "(12) Imo Vessele No.": "IMO Vessel No.",
    "(13) Place of Receipt/Date": "Place of Receipt / Date",
    "(14) Ocean Vessel/Voy. No.": "Ocean Vessel / Voyage No.",
    "(15) Port of Loading": "Port of Loading",
    "(16) Port of Discharge": "Port of Discharge",
    "(17) Place of Delivery": "Place of Delivery",
    "Marks & Nos.": "Marks & Nos.",
    "(18) Container No. And Seal No.": "Container No. / Seal No.",
    "(19) Quantity And Kind of Packages": "Quantity & Kind of Packages",
    "(20) Description of Goods": "Description of Goods",
    "Revenue Tons": "Revenue Tons",
    "Rate": "Rate",
    "Per Prepaid": "Per Prepaid",
    "Collect": "Collect",
    "(21) Measurement (M³) Gross Weight (KGS)": "Measurement / Gross Weight",
    "(22) TOTAL NUMBER OF CONTAINERS OR PACKAGES (IN WORDS)": "Total Containers / Packages",
    "(24) FREIGHT & CHARGES": "Freight & Charges",
    "(25) B/L NO.": "B/L No.",
    "(26) Service Type/Mode": "Service Type / Mode",
    "(27) Number of Original B(s)/L": "Number of Original B(s)/L",
    "(28) Place of B(s)/L Issue/Date": "Place of B(s)/L Issue / Date",
    "(29) Prepaid at": "Prepaid at",
    "(30) Collect at": "Collect at",
    "(31) Exchange Rate": "Exchange Rate",
    "(32) Exchange Rate (Cont.)": "Exchange Rate (Cont.)",
    "(33) Laden on Board": "Laden on Board Date",
}

data = {}
st.header("Shipment Details Input (Matching Document Layout)")
cols = st.columns(3)
col_index = 0

for label, key in fields_map.items():
    # Set default text area height based on field importance
    if key in ["Description of Goods"]:
        height = 150
    elif key in ["Shipper / Exporter", "Consignee", "Notify Party"]:
        height = 80
    else:
        height = 40
    
    # Skip the second part of Exchange Rate in input, as it's often combined in display
    if key == "Exchange Rate (Cont.)":
        continue
    
    # Use text_input for small numerical/short fields
    if key in ["Revenue Tons", "Rate", "Per Prepaid", "Collect", "Document No.", "IMO Vessel No.", "B/L No.", "Number of Original B(s)/L"]:
         data[key] = st.text_input(label, value="", key=key)
         continue
         
    # Use text_area for multi-line address/description fields
    data[key] = cols[col_index % 3].text_area(label, value="", height=height, key=key)
    col_index += 1


# ----------------------------------------------------------------------
# 3. PDF Generation Logic
# ----------------------------------------------------------------------

if st.button("Generate Bill of Lading PDF ⬇️"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=0.5*72, rightMargin=0.5*72, topMargin=0.5*72, bottomMargin=0.5*72)
    elements = []

    # --- Header (Logo and Title) ---
    header_data = []

    if logo_path and os.path.exists(logo_path):
        logo_img = Image(logo_path, width=100, height=50)
    else:
        logo_img = create_cell_content("MCL", "", is_label=False, font_style='MyTitleGreen')

    title_para = Paragraph("<b>BILL OF LADING</b>", styles['MyTitleGreen'])

    header_data.append([
        logo_img,
        create_cell_content("MCL SHIPPING M", "", is_label=False, font_style='MyTitleGreen'),
        title_para,
        create_cell_content("(1) Shipper's Booking No. / Freight Memo No. ...", "", is_label=False, font_style='SmallBlack')
    ])

    header_table = Table(header_data, colWidths=[doc.width * 0.15, doc.width * 0.40, doc.width * 0.25, doc.width * 0.20])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, green_color),
        ('SPAN', (1, 0), (2, 0)),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 6))

    # --- Main B/L Data Table - Building Data ---
    table_data = []

    # Row 1-2: Shipper (50%) / Consignee (50%) / Document No. (16.6%)
    table_data.append([
        create_cell_content("(2) Shipper / Exporter", ""),
        create_cell_content("(3) Consignee(complete name and address)", ""),
        create_cell_content("(5) Document No.", "")
    ])
    table_data.append([
        create_cell_content("", data["Shipper / Exporter"], is_label=False),
        create_cell_content("", data["Consignee"], is_label=False),
        create_cell_content("", data["Document No."], is_label=False)
    ])

    # Row 3-4: Notify Party (50%) / Export References (50%)
    table_data.append([
        create_cell_content("(4) Notify Party (complete name and address)", ""),
        create_cell_content("(6) Export References", "")
    ])
    table_data.append([
        create_cell_content("", data["Notify Party"], is_label=False),
        create_cell_content("", data["Export References"], is_label=False)
    ])
    
    # Row 5-6: Forwarding Agent / Origin
    table_data.append([
        create_cell_content("(7) Forwarding Agent-References", ""),
        create_cell_content("(8) Point and Country of Origin (for the Merchant's reference only)", "")
    ])
    table_data.append([
        create_cell_content("", data["Forwarding Agent-References"], is_label=False),
        create_cell_content("", data["Point & Country of Origin"], is_label=False)
    ])

    # Row 7-8: Also Notify / Instructions
    table_data.append([
        create_cell_content("(9) Also Notify Party (complete name and address)", ""),
        create_cell_content("(10) Onward Inland Routing/Export Instructions (which are contracted separately by Merchants entirely for their own account and risk)", "")
    ])
    table_data.append([
        create_cell_content("", data["Also Notify Party"], is_label=False),
        create_cell_content("", data["Export Instructions"], is_label=False)
    ])

    # Row 9-10: Transport Details - 4 columns
    table_data.append([
        create_cell_content("(13) Place of Receipt/Date", ""),
        create_cell_content("(14) Ocean Vessel/Voy. No.", ""),
        create_cell_content("(15) Port of Loading", ""),
        create_cell_content("(16) Port of Discharge", "")
    ])
    table_data.append([
        create_cell_content("", data["Place of Receipt / Date"], is_label=False),
        create_cell_content("", data["Ocean Vessel / Voyage No."], is_label=False),
        create_cell_content("", data["Port of Loading"], is_label=False),
        create_cell_content("", data["Port of Discharge"], is_label=False)
    ])
    
    # Row 11-12: Place of Delivery / IMO Vessel No.
    table_data.append([
        create_cell_content("(17) Place of Delivery", ""),
        create_cell_content("(12) Imo Vessele No.", "")
    ])
    table_data.append([
        create_cell_content("", data["Place of Delivery"], is_label=False),
        create_cell_content("", data["IMO Vessel No."], is_label=False)
    ])

    # Row 13-14: Marks & Nos. / Container No. / Packages / Description
    table_data.append([
        create_cell_content("Marks & Nos.", ""),
        create_cell_content("(18) Container No. And Seal No.", ""),
        create_cell_content("(19) Quantity And Kind of Packages", ""),
        create_cell_content("(20) Description of Goods", "")
    ])
    table_data.append([
        create_cell_content("", data["Marks & Nos."], is_label=False),
        create_cell_content("", data["Container No. / Seal No."], is_label=False),
        create_cell_content("", data["Quantity & Kind of Packages"], is_label=False),
        create_cell_content("", data["Description of Goods"], is_label=False)
    ])

    # Row 15-16: Financials / Measurement
    table_data.append([
        create_cell_content("Revenue Tons", ""),
        create_cell_content("Rate", ""),
        create_cell_content("Per Prepaid", ""),
        create_cell_content("Collect", ""),
        create_cell_content("(21) Measurement (M³) Gross Weight (KGS)", "")
    ])
    table_data.append([
        create_cell_content("", data.get("Revenue Tons", ""), is_label=False),
        create_cell_content("", data.get("Rate", ""), is_label=False),
        create_cell_content("", data.get("Per Prepaid", ""), is_label=False),
        create_cell_content("", data.get("Collect", ""), is_label=False),
        create_cell_content("", data["Measurement / Gross Weight"], is_label=False)
    ])
    
    # Row 17-18: Total Packages / Freight & Charges
    table_data.append([
        create_cell_content("(22) TOTAL NUMBER OF CONTAINERS OR PACKAGES (IN WORDS)", ""),
        create_cell_content("(24) FREIGHT & CHARGES", "")
    ])
    table_data.append([
        create_cell_content("", data["Total Containers / Packages"], is_label=False),
        create_cell_content("", data["Freight & Charges"], is_label=False)
    ])


    # Row 19-20: B/L No. / Service Type
    table_data.append([
        create_cell_content("(25) B/L NO.", ""),
        create_cell_content("(26) Service Type/Mode", "")
    ])
    table_data.append([
        create_cell_content("", data["B/L No."], is_label=False),
        create_cell_content("", data["Service Type / Mode"], is_label=False)
    ])

    # Row 21-22: Originals / Issue Date
    table_data.append([
        create_cell_content("(27) Number of Original B(s)/L", ""),
        create_cell_content("(28) Place of B(s)/L Issue/Date", "")
    ])
    table_data.append([
        create_cell_content("", data["Number of Original B(s)/L"], is_label=False),
        create_cell_content("", data["Place of B(s)/L Issue / Date"], is_label=False)
    ])

    # Row 23-24: Prepaid at / Collect at
    table_data.append([
        create_cell_content("(29) Prepaid at", ""),
        create_cell_content("(30) Collect at", "")
    ])
    table_data.append([
        create_cell_content("", data["Prepaid at"], is_label=False),
        create_cell_content("", data["Collect at"], is_label=False)
    ])
    
    # Row 25-26: Exchange Rate / Laden on Board
    table_data.append([
        create_cell_content("(31) Exchange Rate / (32) Exchange Rate (Cont.)", ""),
        create_cell_content("(33) Laden on Board", "")
    ])
    table_data.append([
        create_cell_content("", data["Exchange Rate"], is_label=False),
        create_cell_content("", data["Laden on Board Date"], is_label=False)
    ])
    
    # --- Table Styling and Column Spans ---
    
    col_widths = [doc.width * 0.166] * 6
    main_table = Table(table_data, colWidths=col_widths)
    
    # 1. Generate background styles separately (Fixes SyntaxError)
    background_styles = []
    for i in range(len(table_data)):
        if i % 2 == 0:
            background_styles.append(('BACKGROUND', (0, i), (-1, i), light_gray_color))
    
    # 2. Generate SPAN styles separately (Fixes SyntaxError)
    span_styles = []
    
    # Shipper/Consignee (Row 0, 1) - Col 0-2 & Col 3-4 (50%) & Col 5 (16.6%)
    span_styles.extend([
        ('SPAN', (0, 0), (2, 0)), ('SPAN', (3, 0), (4, 0)),
        ('SPAN', (0, 1), (2, 1)), ('SPAN', (3, 1), (4, 1)),
    ])
    
    # Rows with 50%/50% split on 6 columns (Label/Value)
    for i in [2, 4, 6, 10, 18, 20, 22, 24]:
        # Field 1 takes 3 columns (50%), Field 2 takes 3 columns (50%)
        span_styles.extend([
            ('SPAN', (0, i), (2, i)), ('SPAN', (3, i), (5, i)),
            ('SPAN', (0, i+1), (2, i+1)), ('SPAN', (3, i+1), (5, i+1)),
        ])

    # Individual SPAN styles
    
    # Instructions (takes 50% of the last two)
    span_styles.extend([
        ('SPAN', (3, 6), (5, 6)), ('SPAN', (3, 7), (5, 7)),
    ])
    
    # Port of Discharge (4 equal columns for transport details)
    span_styles.extend([
        ('SPAN', (4, 8), (5, 8)), 
        ('SPAN', (4, 9), (5, 9)),
    ])
    
    # Description (Col 3-5)
    span_styles.extend([
        ('SPAN', (3, 12), (5, 12)), ('SPAN', (3, 13), (5, 13)),
    ])
    
    # Measurement (Col 4-5)
    span_styles.extend([
        ('SPAN', (4, 14), (5, 14)), ('SPAN', (4, 15), (5, 15)),
    ])
    
    # Total Packages / Freight & Charges (50%/50%)
    span_styles.extend([
        ('SPAN', (0, 16), (2, 16)), ('SPAN', (3, 16), (5, 16)),
        ('SPAN', (0, 17), (2, 17)), ('SPAN', (3, 17), (5, 17)),
    ])
    
    # 3. Combine all styles into the final list
    main_style = [
        ('GRID', (0, 0), (-1, -1), 0.5, green_color),
        ('BOX', (0, 0), (-1, -1), 1, black_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]
    
    main_style.extend(background_styles)
    main_style.extend(span_styles)

    main_table.setStyle(TableStyle(main_style))
    elements.append(main_table)
    elements.append(Spacer(1, 12))

    # --- Footer (No QR Code) ---

    # Footer/Signature Table (2 rows, 2 columns)
    footer_table = Table([
        [
            Paragraph("SHIPPER'S LOAD & COUNT<br/>OCEAN FREIGHT PREPAID<br/>RECEIPT IS ACKNOWLEDGED BY THE SHIPPER", styles['SmallBlack']),
            create_cell_content("For MCL Shipping M", "", font_style='MyTitleGreen')
        ],
        [
            Spacer(1, 40), # Placeholder for signature area
            create_cell_content("", "Authorized Signature", is_label=False)
        ]
    ], colWidths=[doc.width * 0.5, doc.width * 0.5])

    footer_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, green_color),
        ('ALIGN', (0, 0), (-1, 1), 'LEFT'),
        ('ALIGN', (1, 0), (1, 1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (1, 1), 20),
    ]))
    elements.append(footer_table)
    
    # --- Build Document and Download ---
    
    try:
        doc.build(elements)
        buffer.seek(0)
    
        st.download_button(
            label="Download Bill of Lading PDF ⬇️",
            data=buffer,
            file_name=f"{data.get('B/L No.', 'BILL_OF_LADING').replace('/', '_')}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"An error occurred while generating the PDF: {e}")
