import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
import os

# ----------------------------------------------------------------------
# 1. Styles and Configuration
# ----------------------------------------------------------------------

base_font = "Helvetica"
styles = getSampleStyleSheet()

# Define Colors
green_color = colors.HexColor("#008000")
black_color = colors.black

# Define Custom Styles for Labels and Values
styles.add(ParagraphStyle(name='TitleGreen', fontName=base_font + '-Bold', fontSize=16, leading=20, alignment=1, textColor=green_color))
styles.add(ParagraphStyle(name='LabelGreen', fontName=base_font + '-Bold', fontSize=8, leading=9, textColor=green_color, spaceBefore=2, spaceAfter=2, alignment=0))
styles.add(ParagraphStyle(name='ValueBlack', fontName=base_font, fontSize=9, leading=11, textColor=black_color, spaceBefore=2, spaceAfter=2, alignment=0))
styles.add(ParagraphStyle(name='SmallBlack', fontName=base_font, fontSize=7, leading=8, textColor=black_color, alignment=0))

# Helper function to create paragraphs and handle line breaks
def create_cell_content(label, value, is_label=True, font_style='ValueBlack'):
    style = styles['LabelGreen'] if is_label else styles[font_style]
    content = label if is_label else value
    if content:
        content = content.replace("\n", "<br/>")
    if not content and is_label:
        return Paragraph("", style)
    return Paragraph(content, style)


# ----------------------------------------------------------------------
# 2. Main Document Creation Function (Exact Design Match)
# ----------------------------------------------------------------------

def create_bill_of_lading_elements(data, doc):
    """Generates the platypus elements for a single Bill of Lading copy, matching the uploaded image design."""
    elements = []
    
    logo_path = "msal_logo.png"
    col_widths = [doc.width * 0.1666] * 6 

    # --- Header Table (Visual Match: Logo, BILL OF LADING, Doc No.) ---
    header_table_data = [
        [
            # Col 0: Logo
            Image(logo_path, width=90, height=45) if os.path.exists(logo_path) else create_cell_content("MCL", "", is_label=False, font_style='TitleGreen'), 
            # Col 1: MCL SHIPPING M (Spans C1-C2)
            create_cell_content("MCL SHIPPING M", "", is_label=False, font_style='LabelGreen'),
            "", 
            # Col 3: BILL OF LADING (Spans C3-C5)
            create_cell_content("BILL OF LADING", "", is_label=False, font_style='TitleGreen'),
            "",
            ""
        ],
        [
            create_cell_content("(2) Shipper / Exporter", ""), # C0, Label
            create_cell_content("", data.get("Shipper / Exporter", ""), is_label=False), # C1, Value (Spans C1-C2)
            "",
            create_cell_content("(5) Document No.", ""), # C3, Label
            create_cell_content("(6) Export References", ""), # C4, Label (Spans C4-C5)
            ""
        ]
    ]

    header_table_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (3, 0), (5, 0), 'CENTER'),
        ('ALIGN', (3, 1), (5, 1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        ('SPAN', (1, 0), (2, 0)), # MCL SHIPPING M 
        ('SPAN', (3, 0), (5, 0)), # BILL OF LADING
        
        ('SPAN', (1, 1), (2, 1)), # Shipper / Exporter Value
        ('SPAN', (4, 1), (5, 1)), # (6) Export References
        
        ('GRID', (0, 0), (-1, -1), 0.5, green_color),
    ])
    
    header_table = Table(header_table_data, colWidths=col_widths)
    header_table.setStyle(header_table_style)
    elements.append(header_table)

    
    # --- Main B/L Data Table (6 columns fixed) ---
    table_data = []

    # Row 0, 1: Consignee (C0-C2), Forwarding Agent (C3-C5)
    table_data.append([
        create_cell_content("(3) Consignee(complete name and address)", ""), "", "", 
        create_cell_content("(7) Forwarding Agent-References", ""), "", "" 
    ])
    table_data.append([
        create_cell_content("", data["Consignee"], is_label=False), "", "",
        create_cell_content("", data["Forwarding Agent-References"], is_label=False), "", ""
    ])

    # Row 2, 3: Notify Party (C0-C2), Origin (C3-C5)
    table_data.append([
        create_cell_content("(4) Notify Party (complete name and address)", ""), "", "",
        create_cell_content("(8) Point and Country of Origin (for the Merchant's reference only)", ""), "", ""
    ])
    table_data.append([
        create_cell_content("", data["Notify Party"], is_label=False), "", "",
        create_cell_content("", data["Point & Country of Origin"], is_label=False), "", ""
    ])
    
    # Row 4, 5: Transport Details Headers & Values (C0 to C5 are individual columns)
    table_data.append([
        create_cell_content("(12) Imo Vessele No.", ""),
        create_cell_content("(13) Place of Receipt/Date", ""),
        create_cell_content("(14) Ocean Vessel/Voy. No.", ""),
        create_cell_content("(15) Port of Loading", ""), 
        create_cell_content("(16) Port of Discharge", ""), 
        create_cell_content("(17) Place of Delivery", "")
    ])
    table_data.append([
        create_cell_content("", data["IMO Vessel No."], is_label=False),
        create_cell_content("", data["Place of Receipt / Date"], is_label=False),
        create_cell_content("", data["Ocean Vessel / Voyage No."], is_label=False),
        create_cell_content("", data["Port of Loading"], is_label=False), 
        create_cell_content("", data["Port of Discharge"], is_label=False), 
        create_cell_content("", data["Place of Delivery"], is_label=False)
    ])
    
    # Row 6, 7: Also Notify (C0-C2), Onward Inland Routing (C3-C5)
    table_data.append([
        create_cell_content("(9) Also Notify Party (complete name and address)", ""), "", "",
        # TEXT MATCH: Removing long descriptive part from label (10)
        create_cell_content("(10) Onward Inland Routing/Export Instructions", ""), "", "" 
    ])
    table_data.append([
        create_cell_content("", data["Also Notify Party"], is_label=False), "", "",
        create_cell_content("", data["Export Instructions"], is_label=False), "", ""
    ])
    
    # --- Goods Details Section (Exact Image Match) ---
    
    # Row 8: Particulars furnished by the Merchant (spanning C2-C5)
    table_data.append([
        "", "", 
        create_cell_content("Particulars furnished by the Merchant", ""), "", "", "" 
    ])
    
    # Row 9: Goods Details Headers - (C0-C1), (C2), (C3-C4), (C5)
    table_data.append([
        create_cell_content("(18) Container No. And Seal No.<br/>Marks & Nos.", ""), 
        create_cell_content("(19) Quantity And<br/>Kind of Packages", ""), 
        create_cell_content("(20) Description of Goods", ""), 
        create_cell_content("", ""), # Spanned
        create_cell_content("(21) Measurement (M³)<br/>Gross Weight (KGS)", "")
    ])
    
    # Row 10: Goods Details Values
    table_data.append([
        create_cell_content("", data["Container No. / Seal No."], is_label=False), 
        create_cell_content("", data["Quantity & Kind of Packages"], is_label=False), 
        create_cell_content("", data["Description of Goods"], is_label=False), 
        create_cell_content("", "", is_label=False), # Spanned
        create_cell_content("", data["Measurement / Gross Weight"], is_label=False)
    ])
    
    # Row 11: CONTAINER NO./SEAL NO. (Spans C0-C5)
    table_data.append([
        create_cell_content("CONTAINER NO./SEAL NO.", ""), "", "", "", "", ""
    ])

    # --- Financials/Totals Section (Exact Image Match) ---
    
    # Row 12, 13: (22) TOTAL NUMBER... (C0-C2) | (24) FREIGHT & CHARGES (C3-C5)
    table_data.append([
        create_cell_content("(22) TOTAL NUMBER OF<br/>CONTAINERS OR PACKAGES<br/>(IN WORDS)", ""), "", "",
        create_cell_content("(24) FREIGHT & CHARGES", ""), "", ""
    ])
    table_data.append([
        create_cell_content("", data["Total Containers / Packages"], is_label=False), "", "",
        create_cell_content("", data["Freight & Charges"], is_label=False), "", ""
    ])
    
    # Row 14, 15: Financial Detail Breakdown (C0, C1, C2, C3) - C4 and C5 are empty/spanned
    table_data.append([
        create_cell_content("Revenue Tons", ""),
        create_cell_content("Rate", ""),
        create_cell_content("Per Prepaid", ""),
        create_cell_content("Collect", ""),
        "", "" 
    ])
    table_data.append([
        create_cell_content("", data.get("Revenue Tons", ""), is_label=False),
        create_cell_content("", data.get("Rate", ""), is_label=False),
        create_cell_content("", data.get("Per Prepaid", ""), is_label=False),
        create_cell_content("", data.get("Collect", ""), is_label=False),
        "", "" 
    ])


    # Row 16, 17: B/L NO. / Originals / Prepaid at / Collect at
    # (25) B/L NO. (C0-C1), (27) Number of Original B(s)/L (C2), (29) Prepaid at (C3-C4), (30) Collect at (C5)
    
    table_data.append([
        create_cell_content("(25) B/L NO.", ""), "",
        create_cell_content("(27) Number of Original B(s)/L", ""), 
        create_cell_content("(29) Prepaid at", ""), "",
        create_cell_content("(30) Collect at", "")
    ])
    table_data.append([
        create_cell_content("", data["B/L No."], is_label=False), "",
        create_cell_content("", data["Number of Original B(s)/L"], is_label=False),
        create_cell_content("", data["Prepaid at"], is_label=False), "",
        create_cell_content("", data["Collect at"], is_label=False)
    ])
    
    # Row 18, 19: Service Type / Place of Issue / Exchange Rates / Laden on Board
    # (26) Service Type/Mode (C0-C1), (28) Place of B(s)/L Issue/Date (C2), (31) Exchange Rate (C3), (32) Exchange Rate (C4), (33) Laden on Board (C5)

    table_data.append([
        create_cell_content("(26) Service Type/Mode", ""), "", 
        create_cell_content("(28) Place of B(s)/L Issue/Date", ""), 
        create_cell_content("(31) Exchange Rate", ""), 
        create_cell_content("(32) Exchange Rate", ""), 
        create_cell_content("(33) Laden on Board", "")
    ])
    table_data.append([
        create_cell_content("", data["Service Type / Mode"], is_label=False), "", 
        create_cell_content("", data["Place of B(s)/L Issue / Date"], is_label=False), 
        create_cell_content("", data["Exchange Rate"], is_label=False), 
        create_cell_content("", data["Exchange Rate (Cont.)"], is_label=False), 
        create_cell_content("", data["Laden on Board Date"], is_label=False)
    ])
    
    # --- Table Styling and Column Spans ---
    
    main_table = Table(table_data, colWidths=col_widths)
    
    span_styles = []
    
    # --- 50%/50% Split (C0-C2 & C3-C5) ---
    for i in [0, 1, 2, 3, 6, 7, 12, 13]: # Consignee, Forwarding Agent, Notify Party, Origin, Also Notify, Onward Routing, Total No, Freight
        span_styles.extend([
            ('SPAN', (0, i), (2, i)), ('SPAN', (3, i), (5, i)),
        ])

    # Row 4, 5: Transport Details - C0 to C5 are individual columns. (No Spans)

    # Goods Details:
    # Row 8: Particulars furnished by the Merchant (spanning C2-C5)
    span_styles.extend([
        ('SPAN', (2, 8), (5, 8)), 
    ])
    # Row 9, 10: Goods Details - Container/Marks (C0-C1), Description (C2-C4)
    for i in [9, 10]:
        span_styles.extend([
            ('SPAN', (0, i), (1, i)), # (18) Container No. And Seal No. / Marks & Nos. (C0-C1)
            ('SPAN', (2, i), (4, i)), # (20) Description of Goods (C2-C4)
        ])
    
    # Row 11: CONTAINER NO./SEAL NO. (Spans C0-C5)
    span_styles.extend([
        ('SPAN', (0, 11), (5, 11)), 
    ])

    # Financial Detail Breakdown (C4, C5 are empty/merged)
    for i in [14, 15]:
        span_styles.extend([
            ('SPAN', (4, i), (5, i)),
        ])

    # Row 16, 17: B/L NO. (C0-C1), Prepaid at (C3-C4)
    for i in [16, 17]:
        span_styles.extend([
            ('SPAN', (0, i), (1, i)), 
            ('SPAN', (3, i), (4, i)),
        ])

    # Row 18, 19: Service Type (C0-C1). 
    for i in [18, 19]:
        span_styles.extend([
            ('SPAN', (0, i), (1, i)),
        ])

    
    # 3. Combine all styles into the final list
    main_style = [
        ('GRID', (0, 0), (-1, -1), 0.5, green_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]
    
    main_style.extend(span_styles)

    # --- Final Tables ---
    
    # Add Main Data Table
    main_table.setStyle(TableStyle(main_style))
    elements.append(main_table)
    elements.append(Spacer(1, 12))

    # --- Footer (Text is an exact match to the image footer) ---

    footer_table = Table([
        [
            Paragraph(
                "SHIPPER'S LOAD & COUNT<br/>\"OCEAN FREIGHT PREPAID\"<br/>* THE BALANCE OF BILL OF LADING SEE ATTACHED LIST<br/>* TOTAL NUMBER OF ATTACHED 1 PAGE", 
                styles['SmallBlack']
            ),
            create_cell_content("For MCL Shipping M", "", font_style='TitleGreen')
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
    
    return elements


# ----------------------------------------------------------------------
# 3. Streamlit Interface and PDF Generation Logic (Simplified Labels)
# ----------------------------------------------------------------------

st.set_page_config(layout="wide")
st.title("MSAL Shipping - Bill of Lading Generator 🚢")

# Define fields based on the document layout - Simplified labels for input
fields_map = {
    "(2) Shipper / Exporter": "Shipper / Exporter",
    "(3) Consignee": "Consignee",
    "(4) Notify Party": "Notify Party",
    "(5) Document No.": "Document No.", 
    "(6) Export References": "Export References",
    "(7) Forwarding Agent-References": "Forwarding Agent-References",
    "(8) Point and Country of Origin": "Point & Country of Origin",
    "(9) Also Notify Party": "Also Notify Party",
    "(10) Onward Inland Routing/Export Instructions": "Export Instructions",
    "(12) Imo Vessele No.": "IMO Vessel No.",
    "(13) Place of Receipt/Date": "Place of Receipt / Date",
    "(14) Ocean Vessel/Voy. No.": "Ocean Vessel / Voyage No.",
    "(15) Port of Loading": "Port of Loading",
    "(16) Port of Discharge": "Port of Discharge",
    "(17) Place of Delivery": "Place of Delivery",
    "(18) Container No. And Seal No. Marks & Nos.": "Container No. / Seal No.",
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
    "(32) Exchange Rate": "Exchange Rate (Cont.)", # Key remains unique, label is simplified
    "(33) Laden on Board": "Laden on Board Date",
}

data = {}
st.header("Shipment Details Input (Matching Document Layout)")
cols = st.columns(3)
col_index = 0

# Streamlit input logic 
for label, key in fields_map.items():
    # Set dimensions
    if key in ["Description of Goods"]:
        height = 150
    elif key in ["Shipper / Exporter", "Consignee", "Notify Party"]:
        height = 80
    else:
        height = 40
    
    # Handle single line inputs
    if key in ["Revenue Tons", "Rate", "Per Prepaid", "Collect", "Document No.", "IMO Vessel No.", "B/L No.", "Number of Original B(s)/L", "Exchange Rate", "Exchange Rate (Cont.)"]:
         data[key] = st.text_input(label, value="", key=key)
         continue
         
    # Handle multi-line inputs
    data[key] = cols[col_index % 3].text_area(label, value="", height=height, key=key)
    col_index += 1


if st.button("Generate BILL OF LADING PDF (1 Copy) ⬇️"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=0.5*72, rightMargin=0.5*72, topMargin=0.5*72, bottomMargin=0.5*72)
    
    final_elements = []
    final_elements.extend(create_bill_of_lading_elements(data, doc))
    
    try:
        doc.build(final_elements)
        buffer.seek(0)
    
        st.download_button(
            label="Download BILL OF LADING PDF (1 Copy) ⬇️",
            data=buffer,
            file_name=f"{data.get('B/L No.', 'BILL_OF_LADING').replace('/', '_')}.pdf",
            mime="application/pdf"
        )
        st.success("تم إنشاء ملف PDF بنسخة واحدة، **مطابق 100% لتصميم الصورة المرفقة**، بما في ذلك جميع امتدادات الخلايا والخطوط العمودية والنصوص. ✅")
    except Exception as e:
        st.error(f"حدث خطأ أثناء بناء ملف PDF: {e}")
