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
    # Use different styles based on whether it's a label or a value
    style = styles['LabelGreen'] if is_label else styles[font_style]
    
    # Replace newline characters with HTML line breaks for ReportLab Paragraphs
    content = label if is_label else value
    if content:
        content = content.replace("\n", "<br/>")
    
    # Handle empty cells
    if not content:
        return Paragraph("", style)
        
    return Paragraph(content, style)


# ----------------------------------------------------------------------
# 2. Main Document Creation Function (Exact Design Match)
# ----------------------------------------------------------------------

def create_bill_of_lading_elements(data, doc):
    """Generates the platypus elements for a single Bill of Lading copy, matching the uploaded image design."""
    elements = []
    
    logo_path = "msal_logo.png"

    # --- Header (Logo and Title) ---
    header_data = []

    if logo_path and os.path.exists(logo_path):
        logo_img = Image(logo_path, width=90, height=45)
    else:
        # Placeholder for MCL and MCL SHIPPING M
        logo_img = create_cell_content("MCL", "", is_label=False, font_style='TitleGreen')

    # The actual image shows MCL SHIPPING M and MCL logo on the left, and TITLE/Doc No on the right.
    # Re-structure the header to reflect the image's division.

    header_table_data = [
        [
            logo_img, 
            create_cell_content("MCL SHIPPING M", "", is_label=False, font_style='LabelGreen'),
            create_cell_content("BILL OF LADING", "", is_label=False, font_style='TitleGreen'),
            create_cell_content("(5) Document No.", ""),
            create_cell_content("(6) Export References", "")
        ],
        [
            create_cell_content("(2) Shipper / Exporter", ""),
            "", "", # Spanned cells
            create_cell_content("", data.get("Document No.", ""), is_label=False),
            create_cell_content("", data.get("Export References", ""), is_label=False)
        ]
    ]

    header_table_style = TableStyle([
        ('ALIGN', (0, 0), (1, 0), 'LEFT'),
        ('ALIGN', (2, 0), (2, 0), 'CENTER'),
        ('ALIGN', (3, 0), (4, 1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Merge MCL SHIPPING M and Logo (visual alignment in first cell)
        ('SPAN', (0, 0), (0, 1)),
        ('SPAN', (1, 0), (1, 1)),
        ('SPAN', (2, 0), (2, 1)), # BILL OF LADING Spans two rows
        
        # Merge Shipper/Exporter (Row 1, Cols 0-1)
        ('SPAN', (0, 1), (1, 1)),

        ('GRID', (0, 0), (-1, -1), 0.5, green_color),
        ('LINEBELOW', (0, 0), (0, 0), 0.5, green_color),
        ('LINEBELOW', (1, 0), (1, 0), 0.5, green_color),

        # Column widths reflect 5 visible columns in the header
        ('COLWIDTHS', (0, 1), doc.width * 0.15),
        ('COLWIDTHS', (1, 1), doc.width * 0.25),
        ('COLWIDTHS', (2, 1), doc.width * 0.25),
        ('COLWIDTHS', (3, 1), doc.width * 0.175),
        ('COLWIDTHS', (4, 1), doc.width * 0.175),
    ])

    # Rebuilding with 6 logical columns for consistency, then applying spans
    # Column widths (approximate 6-column split)
    col_widths = [doc.width * 0.1666] * 6 

    # --- Main B/L Data Table - Building Data (6 columns fixed) ---
    
    table_data = []

    # Row 0, 1: Shipper (C0-C2), Consignee (C3-C5)
    table_data.append([
        create_cell_content("(2) Shipper / Exporter", ""), "", "", 
        create_cell_content("(3) Consignee(complete name and address)", ""), "", "" 
    ])
    table_data.append([
        create_cell_content("", data["Shipper / Exporter"], is_label=False), "", "",
        create_cell_content("", data["Consignee"], is_label=False), "", ""
    ])

    # Row 2, 3: Notify Party (C0-C2), Forwarding Agent (C3-C5)
    table_data.append([
        create_cell_content("(4) Notify Party (complete name and address)", ""), "", "",
        create_cell_content("(7) Forwarding Agent-References", ""), "", ""
    ])
    table_data.append([
        create_cell_content("", data["Notify Party"], is_label=False), "", "",
        create_cell_content("", data["Forwarding Agent-References"], is_label=False), "", ""
    ])
    
    # Row 4, 5: Point of Origin (C0-C2), Also Notify (C3-C5)
    table_data.append([
        create_cell_content("(8) Point and Country of Origin (for the Merchant's reference only)", ""), "", "",
        create_cell_content("(9) Also Notify Party (complete name and address)", ""), "", ""
    ])
    table_data.append([
        create_cell_content("", data["Point & Country of Origin"], is_label=False), "", "",
        create_cell_content("", data["Also Notify Party"], is_label=False), "", ""
    ])

    # Row 6: Transport Details Headers - (C0), (C1), (C2), (C3), (C4), (C5)
    table_data.append([
        create_cell_content("(12) Imo Vessele No.", ""),
        create_cell_content("(13) Place of Receipt/Date", ""),
        create_cell_content("(14) Ocean Vessel/Voy. No.", ""),
        create_cell_content("(15) Port of Loading", ""), 
        create_cell_content("(16) Port of Discharge", ""), 
        create_cell_content("(17) Place of Delivery", "")
    ])
    
    # Row 7: Transport Details Values
    table_data.append([
        create_cell_content("", data["IMO Vessel No."], is_label=False),
        create_cell_content("", data["Place of Receipt / Date"], is_label=False),
        create_cell_content("", data["Ocean Vessel / Voyage No."], is_label=False),
        create_cell_content("", data["Port of Loading"], is_label=False), 
        create_cell_content("", data["Port of Discharge"], is_label=False), 
        create_cell_content("", data["Place of Delivery"], is_label=False)
    ])

    # Row 8, 9: Export Instructions (Spans C0-C5)
    table_data.append([
        create_cell_content("(10) Onward Inland Routing/Export Instructions (which are contracted separately by Merchants entirely for their own account and risk)", ""), "", "", "", "", ""
    ])
    table_data.append([
        create_cell_content("", data["Export Instructions"], is_label=False), "", "", "", "", ""
    ])
    
    # --- Goods Details Section (Exact Image Match) ---
    
    # Row 10: Particulars furnished by the Merchant (spanning C2-C5)
    table_data.append([
        "", "", 
        create_cell_content("Particulars furnished by the Merchant", ""), "", "", "" 
    ])
    
    # Row 11: Goods Details Headers - (C0-C1), (C2), (C3-C4), (C5)
    table_data.append([
        create_cell_content("(18) Container No. And Seal No.<br/>Marks & Nos.", ""), 
        create_cell_content("(19) Quantity And<br/>Kind of Packages", ""), 
        create_cell_content("(20) Description of Goods", ""), 
        create_cell_content("", ""), # Spanned for Description
        create_cell_content("(21) Measurement (M³)<br/>Gross Weight (KGS)", "")
    ])
    
    # Row 12: Goods Details Values
    table_data.append([
        create_cell_content("", data["Container No. / Seal No."], is_label=False), 
        create_cell_content("", data["Quantity & Kind of Packages"], is_label=False), 
        create_cell_content("", data["Description of Goods"], is_label=False), 
        create_cell_content("", "", is_label=False), # Spanned for Description
        create_cell_content("", data["Measurement / Gross Weight"], is_label=False)
    ])
    
    # Row 13: CONTAINER NO./SEAL NO. (Spans C0-C5)
    table_data.append([
        create_cell_content("CONTAINER NO./SEAL NO.", ""), "", "", "", "", ""
    ])

    # --- Financials/Totals Section (Exact Image Match) ---
    
    # Row 14, 15: (22) TOTAL NUMBER... (C0-C2) | (24) FREIGHT & CHARGES (C3-C5)
    table_data.append([
        create_cell_content("(22) TOTAL NUMBER OF<br/>CONTAINERS OR PACKAGES<br/>(IN WORDS)", ""), "", "",
        create_cell_content("(24) FREIGHT & CHARGES", ""), "", ""
    ])
    table_data.append([
        create_cell_content("", data["Total Containers / Packages"], is_label=False), "", "",
        create_cell_content("", data["Freight & Charges"], is_label=False), "", ""
    ])
    
    # Row 16: Financial Detail Breakdown Headers (C0, C1, C2, C3) - C4 and C5 are empty in the image structure
    table_data.append([
        create_cell_content("Revenue Tons", ""),
        create_cell_content("Rate", ""),
        create_cell_content("Per Prepaid", ""),
        create_cell_content("Collect", ""),
        "", "" 
    ])
    
    # Row 17: Financial Detail Breakdown Values
    table_data.append([
        create_cell_content("", data.get("Revenue Tons", ""), is_label=False),
        create_cell_content("", data.get("Rate", ""), is_label=False),
        create_cell_content("", data.get("Per Prepaid", ""), is_label=False),
        create_cell_content("", data.get("Collect", ""), is_label=False),
        "", "" 
    ])


    # Row 18, 19: B/L NO. / Number of Original B(s)/L / Prepaid at / Collect at
    # This row has 4 distinct data columns (C0, C1, C2, C3)
    # The image structure is very compressed here, let's stick to the 6-column grid:
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
    
    # Row 20, 21: Service Type / Place of Issue / Exchange Rates / Laden on Board
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
    
    # --- 2.1 Fixed SPANS (50%/50% Split) ---
    # Rows: 0, 1, 2, 3, 4, 5 (Labels and Values)
    for i in range(6):
        if i % 2 == 0: # Labels
            span_styles.extend([
                ('SPAN', (0, i), (2, i)), ('SPAN', (3, i), (5, i)),
            ])
        else: # Values
            span_styles.extend([
                ('SPAN', (0, i), (2, i)), ('SPAN', (3, i), (5, i)),
            ])

    # Row 8, 9: Export Instructions (Spans C0-C5)
    span_styles.extend([
        ('SPAN', (0, 8), (5, 8)), ('SPAN', (0, 9), (5, 9)),
    ])
    
    # Goods Details Corrections:
    # Row 10: Particulars furnished by the Merchant (spanning C2-C5)
    span_styles.extend([
        ('SPAN', (2, 10), (5, 10)), 
    ])
    # Row 11, 12: Goods Details - Container/Marks (C0), Quantity (C1), Description (C2-C4), Measurement (C5)
    span_styles.extend([
        ('SPAN', (0, 11), (0, 11)), # C0 is single column
        ('SPAN', (1, 11), (1, 11)), # C1 is single column
        ('SPAN', (2, 11), (4, 11)), # C2, C3, C4 merged for Description
        ('SPAN', (0, 12), (0, 12)), # C0 is single column
        ('SPAN', (1, 12), (1, 12)), # C1 is single column
        ('SPAN', (2, 12), (4, 12)), # C2, C3, C4 merged for Description Value
    ])
    
    # Row 13: CONTAINER NO./SEAL NO. (Spans C0-C5)
    span_styles.extend([
        ('SPAN', (0, 13), (5, 13)), 
    ])

    # Financials/Totals Section:
    # Row 14, 15: (22) TOTAL NUMBER... (C0-C2) | (24) FREIGHT & CHARGES (C3-C5)
    for i in [14, 15]:
        span_styles.extend([
            ('SPAN', (0, i), (2, i)), ('SPAN', (3, i), (5, i)),
        ])
    
    # Row 16, 17: Financial Detail Breakdown (C4, C5 are empty/merged)
    span_styles.extend([
        ('SPAN', (4, 16), (5, 16)), ('SPAN', (4, 17), (5, 17)),
    ])

    # Row 18, 19: B/L NO. (C0-C1), Number of Original B(s)/L (C2), Prepaid at (C3-C4), Collect at (C5)
    for i in [18, 19]:
        span_styles.extend([
            ('SPAN', (0, i), (1, i)), ('SPAN', (3, i), (4, i)),
        ])

    # Row 20, 21: Service Type (C0-C1), Place of Issue (C2), Exchange Rate (C3), Exchange Rate (C4), Laden on Board (C5)
    for i in [20, 21]:
        span_styles.extend([
            ('SPAN', (0, i), (1, i)),
        ])

    
    # 3. Combine all styles into the final list
    main_style = [
        ('GRID', (0, 0), (-1, -1), 0.5, green_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        # Set padding to zero for tight fit in goods section
        ('LEFTPADDING', (0, 11), (-1, 12), 2),
        ('RIGHTPADDING', (0, 11), (-1, 12), 2),
        ('TOPPADDING', (0, 11), (-1, 12), 2),
        ('BOTTOMPADDING', (0, 11), (-1, 12), 2),
    ]
    
    main_style.extend(span_styles)

    # --- Final Tables ---
    
    # Add Header Table (with logo, B/L, Doc No.)
    elements.append(Table(header_table_data, colWidths=[doc.width*0.08, doc.width*0.28, doc.width*0.25, doc.width*0.195, doc.width*0.195]))
    elements.append(Spacer(1, 0)) # Remove space between tables

    # Add Main Data Table
    main_table.setStyle(TableStyle(main_style))
    elements.append(main_table)
    elements.append(Spacer(1, 12))

    # --- Footer (As per PDF snippet) ---

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
# 3. Streamlit Interface and PDF Generation Logic
# ----------------------------------------------------------------------

st.set_page_config(layout="wide")
st.title("MSAL Shipping - Bill of Lading Generator 🚢")

# Define fields based on the document layout 
# Note: Key names are kept simple for input mapping
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
    "(32) Exchange Rate (Cont.)": "Exchange Rate (Cont.)",
    "(33) Laden on Board": "Laden on Board Date",
}

data = {}
st.header("Shipment Details Input (Matching Document Layout)")
cols = st.columns(3)
col_index = 0

# Streamlit input logic 
for label, key in fields_map.items():
    if key in ["Description of Goods"]:
        height = 150
    elif key in ["Shipper / Exporter", "Consignee", "Notify Party"]:
        height = 80
    else:
        height = 40
    
    if key == "Exchange Rate (Cont.)":
        data[key] = st.text_input("Exchange Rate (Cont.)", value="", key=key)
        continue
    
    if key in ["Revenue Tons", "Rate", "Per Prepaid", "Collect", "Document No.", "IMO Vessel No.", "B/L No.", "Number of Original B(s)/L"]:
         data[key] = st.text_input(label, value="", key=key)
         continue
         
    data[key] = cols[col_index % 3].text_area(label, value="", height=height, key=key)
    col_index += 1


if st.button("Generate BILL OF LADING PDF (1 Copy) ⬇️"):
    buffer = io.BytesIO()
    # Use smaller margins for maximal document space
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=0.5*72, rightMargin=0.5*72, topMargin=0.5*72, bottomMargin=0.5*72)
    
    final_elements = []

    # --- Single Copy Generation ---
    final_elements.extend(create_bill_of_lading_elements(data, doc))
    
    # --- Build Document and Download ---
    
    try:
        doc.build(final_elements)
        buffer.seek(0)
    
        st.download_button(
            label="Download BILL OF LADING PDF (1 Copy) ⬇️",
            data=buffer,
            file_name=f"{data.get('B/L No.', 'BILL_OF_LADING').replace('/', '_')}.pdf",
            mime="application/pdf"
        )
        st.success("تم إنشاء ملف PDF بنسخة واحدة، مطابق تمامًا لتصميم الصورة المرفقة، وبدون إطار خارجي أو خلفية ملونة. ✅")
    except Exception as e:
        st.error(f"حدث خطأ أثناء بناء ملف PDF: {e}")
