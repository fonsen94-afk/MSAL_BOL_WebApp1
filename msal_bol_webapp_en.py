import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
import os

# ----------------------------------------------------------------------
# 1. Styles and Configuration
# ----------------------------------------------------------------------

# Using standard ReportLab fonts (Helvetica)
base_font = "Helvetica"
styles = getSampleStyleSheet()

# Define Colors
green_color = colors.HexColor("#008000")
black_color = colors.black
light_gray_color = colors.HexColor("#EEEEEE")

# Define styles using standard fonts (The font sizes are maintained to ensure proper relative spacing)
styles.add(ParagraphStyle(name='MyTitleGreen', fontName=base_font + '-Bold', fontSize=16, leading=20, alignment=1, textColor=green_color, allowOrphans=0, allowWidows=0))
styles.add(ParagraphStyle(name='MyFieldLabelGreen', fontName=base_font + '-Bold', fontSize=8, leading=10, textColor=green_color, spaceBefore=2, spaceAfter=2, alignment=0, allowOrphans=0, allowWidows=0))
styles.add(ParagraphStyle(name='MyFieldValueBlack', fontName=base_font, fontSize=9, leading=11, textColor=black_color, spaceBefore=2, spaceAfter=2, alignment=0, allowOrphans=0, allowWidows=0))
styles.add(ParagraphStyle(name='SmallBlack', fontName=base_font, fontSize=7, leading=9, textColor=black_color, alignment=0, allowOrphans=0, allowWidows=0))


# Helper function to create paragraphs and handle line breaks
def create_cell_content(label, value, is_label=True, font_style='MyFieldValueBlack'):
    style = styles['MyFieldLabelGreen'] if is_label else styles[font_style]
    content = value.replace("\n", "<br/>") if not is_label else label
    # Handle empty content for padding cells
    if not label and not value and is_label:
        return ""
    if not content and is_label:
        return Paragraph("", style)
    return Paragraph(content, style)


# ----------------------------------------------------------------------
# 2. Main Document Creation Function (Contains the exact design/structure)
# ----------------------------------------------------------------------

def create_bill_of_lading_elements(data, doc):
    """Generates the platypus elements for a single Bill of Lading copy, matching the requested design."""
    elements = []
    
    logo_path = "msal_logo.png"

    # --- Header (Logo and Title) ---
    header_data = []

    if logo_path and os.path.exists(logo_path):
        logo_img = Image(logo_path, width=100, height=50)
    else:
        logo_img = create_cell_content("MCL", "", is_label=False, font_style='MyTitleGreen')

    # Change the title as requested: BILLOF-LADING
    title_para = Paragraph("<b>BILLOF-LADING</b>", styles['MyTitleGreen'])

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
        # No GRID or BOX on the header table as requested
        ('SPAN', (1, 0), (2, 0)),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 6))

    # --- Main B/L Data Table - Building Data (All rows must have 6 elements) ---
    
    table_data = []

    # Row 0, 1: Shipper (Col 0-2), Consignee (Col 3-4), (5) B/L No. (Col 5) - MODIFIED LABEL HERE
    table_data.append([
        create_cell_content("(2) Shipper / Exporter", ""), "", "", 
        create_cell_content("(3) Consignee(complete name and address)", ""), "", 
        create_cell_content("(5) B/L No.", "") # Changed from Document No.
    ])
    table_data.append([
        create_cell_content("", data["Shipper / Exporter"], is_label=False), "", "",
        create_cell_content("", data["Consignee"], is_label=False), "",
        create_cell_content("", data["Document No."], is_label=False) # Data field remains "Document No." for consistency
    ])

    # Row 2, 3: Notify Party / Export References (50%/50% split - Col 0-2 and Col 3-5)
    table_data.append([
        create_cell_content("(4) Notify Party (complete name and address)", ""), "", "",
        create_cell_content("(6) Export References", ""), "", ""
    ])
    table_data.append([
        create_cell_content("", data["Notify Party"], is_label=False), "", "",
        create_cell_content("", data["Export References"], is_label=False), "", ""
    ])
    
    # Row 4, 5: Forwarding Agent / Origin (50%/50% split)
    table_data.append([
        create_cell_content("(7) Forwarding Agent-References", ""), "", "",
        create_cell_content("(8) Point and Country of Origin (for the Merchant's reference only)", ""), "", ""
    ])
    table_data.append([
        create_cell_content("", data["Forwarding Agent-References"], is_label=False), "", "",
        create_cell_content("", data["Point & Country of Origin"], is_label=False), "", ""
    ])

    # Row 6, 7: Also Notify / Instructions (50%/50% split)
    table_data.append([
        create_cell_content("(9) Also Notify Party (complete name and address)", ""), "", "",
        create_cell_content("(10) Onward Inland Routing/Export Instructions (which are contracted separately by Merchants entirely for their own account and risk)", ""), "", ""
    ])
    table_data.append([
        create_cell_content("", data["Also Notify Party"], is_label=False), "", "",
        create_cell_content("", data["Export Instructions"], is_label=False), "", ""
    ])

    # Row 8, 9: Transport Details - (Col 0-1), (Col 2-3), (Col 4), (Col 5)
    table_data.append([
        create_cell_content("(13) Place of Receipt/Date", ""), "", 
        create_cell_content("(14) Ocean Vessel/Voy. No.", ""), "", 
        create_cell_content("(15) Port of Loading", ""), 
        create_cell_content("(16) Port of Discharge", "")
    ])
    table_data.append([
        create_cell_content("", data["Place of Receipt / Date"], is_label=False), "", 
        create_cell_content("", data["Ocean Vessel / Voyage No."], is_label=False), "", 
        create_cell_content("", data["Port of Loading"], is_label=False), 
        create_cell_content("", data["Port of Discharge"], is_label=False)
    ])
    
    # Row 10, 11: Place of Delivery / IMO Vessel No. (50%/50% split)
    table_data.append([
        create_cell_content("(17) Place of Delivery", ""), "", "",
        create_cell_content("(12) Imo Vessele No.", ""), "", ""
    ])
    table_data.append([
        create_cell_content("", data["Place of Delivery"], is_label=False), "", "",
        create_cell_content("", data["IMO Vessel No."], is_label=False), "", ""
    ])

    # Row 12, 13: Goods Details - (Col 0), (Col 1), (Col 2), (Col 3-5)
    table_data.append([
        create_cell_content("Marks & Nos.", ""), 
        create_cell_content("(18) Container No. And Seal No.", ""), 
        create_cell_content("(19) Quantity And Kind of Packages", ""), 
        create_cell_content("(20) Description of Goods", ""), "", ""
    ])
    table_data.append([
        create_cell_content("", data["Marks & Nos."], is_label=False), 
        create_cell_content("", data["Container No. / Seal No."], is_label=False), 
        create_cell_content("", data["Quantity & Kind of Packages"], is_label=False), 
        create_cell_content("", data["Description of Goods"], is_label=False), "", ""
    ])

    # Row 14, 15: Financials/Measurement - (Col 0-3 are 1 col each), Measurement (Col 4-5)
    table_data.append([
        create_cell_content("Revenue Tons", ""),
        create_cell_content("Rate", ""),
        create_cell_content("Per Prepaid", ""),
        create_cell_content("Collect", ""),
        create_cell_content("(21) Measurement (M³) Gross Weight (KGS)", ""), ""
    ])
    table_data.append([
        create_cell_content("", data.get("Revenue Tons", ""), is_label=False),
        create_cell_content("", data.get("Rate", ""), is_label=False),
        create_cell_content("", data.get("Per Prepaid", ""), is_label=False),
        create_cell_content("", data.get("Collect", ""), is_label=False),
        create_cell_content("", data["Measurement / Gross Weight"], is_label=False), ""
    ])
    
    # Row 16, 17: Total Packages / Freight & Charges (50%/50% split)
    table_data.append([
        create_cell_content("(22) TOTAL NUMBER OF CONTAINERS OR PACKAGES (IN WORDS)", ""), "", "",
        create_cell_content("(24) FREIGHT & CHARGES", ""), "", ""
    ])
    table_data.append([
        create_cell_content("", data["Total Containers / Packages"], is_label=False), "", "",
        create_cell_content("", data["Freight & Charges"], is_label=False), "", ""
    ])


    # Row 18, 19: B/L No. / Service Type (50%/50% split)
    table_data.append([
        create_cell_content("(25) B/L NO.", ""), "", "",
        create_cell_content("(26) Service Type/Mode", ""), "", ""
    ])
    table_data.append([
        create_cell_content("", data["B/L No."], is_label=False), "", "",
        create_cell_content("", data["Service Type / Mode"], is_label=False), "", ""
    ])

    # Row 20, 21: Originals / Issue Date (50%/50% split)
    table_data.append([
        create_cell_content("(27) Number of Original B(s)/L", ""), "", "",
        create_cell_content("(28) Place of B(s)/L Issue/Date", ""), "", ""
    ])
    table_data.append([
        create_cell_content("", data["Number of Original B(s)/L"], is_label=False), "", "",
        create_cell_content("", data["Place of B(s)/L Issue / Date"], is_label=False), "", ""
    ])

    # Row 22, 23: Prepaid at / Collect at (50%/50% split)
    table_data.append([
        create_cell_content("(29) Prepaid at", ""), "", "",
        create_cell_content("(30) Collect at", ""), "", ""
    ])
    table_data.append([
        create_cell_content("", data["Prepaid at"], is_label=False), "", "",
        create_cell_content("", data["Collect at"], is_label=False), "", ""
    ])
    
    # Row 24, 25: Exchange Rate / Laden on Board (50%/50% split)
    table_data.append([
        create_cell_content("(31) Exchange Rate / (32) Exchange Rate (Cont.)", ""), "", "",
        create_cell_content("(33) Laden on Board", ""), "", ""
    ])
    table_data.append([
        create_cell_content("", data["Exchange Rate"], is_label=False), "", "",
        create_cell_content("", data["Laden on Board Date"], is_label=False), "", ""
    ])
    
    # --- Table Styling and Column Spans ---
    
    col_widths = [doc.width * 0.166] * 6
    main_table = Table(table_data, colWidths=col_widths)
    
    # 1. Generate background styles 
    background_styles = []
    for i in range(len(table_data)):
        if i % 2 == 0:
            background_styles.append(('BACKGROUND', (0, i), (-1, i), light_gray_color))
    
    # 2. Generate SPAN styles 
    span_styles = []
    
    # --- 2.1 Fixed SPANS (Rows 0, 1) ---
    # Shipper/Consignee/(5)B/L No.: Col 0-2 (Shipper), Col 3-4 (Consignee), Col 5 (DocNo/B/L No.)
    span_styles.extend([
        ('SPAN', (0, 0), (2, 0)), ('SPAN', (3, 0), (4, 0)),
        ('SPAN', (0, 1), (2, 1)), ('SPAN', (3, 1), (4, 1)),
    ])
    
    # --- 2.2 Looping SPANS (Simple 50%/50% Split - Col 0-2 and Col 3-5) ---
    # Rows: 2, 4, 6, 10, 16, 18, 20, 22, 24 (Labels and Values)
    for i in [2, 4, 6, 10, 16, 18, 20, 22, 24]:
        span_styles.extend([
            ('SPAN', (0, i), (2, i)), ('SPAN', (3, i), (5, i)),
            ('SPAN', (0, i+1), (2, i+1)), ('SPAN', (3, i+1), (5, i+1)),
        ])

    # --- 2.3 Complex/Individual SPANS ---
    
    # Row 8, 9: Transport Details - (Col 0-1), (Col 2-3), (Col 4), (Col 5)
    span_styles.extend([
        ('SPAN', (0, 8), (1, 8)), 
        ('SPAN', (2, 8), (3, 8)), 
        ('SPAN', (0, 9), (1, 9)), 
        ('SPAN', (2, 9), (3, 9)), 
    ])
    
    # Row 12, 13: Goods Details - Marks/Container/Packages (1 col each), Description (Col 3-5)
    span_styles.extend([
        ('SPAN', (3, 12), (5, 12)), 
        ('SPAN', (3, 13), (5, 13)), 
    ])
    
    # Row 14, 15: Financials/Measurement - (Col 0-3 are 1 col each), Measurement (Col 4-5)
    span_styles.extend([
        ('SPAN', (4, 14), (5, 14)), 
        ('SPAN', (4, 15), (5, 15)), 
    ])
    
    # 3. Combine all styles into the final list
    main_style = [
        # Keep internal GRID lines with green color
        ('GRID', (0, 0), (-1, -1), 0.5, green_color),
        # BOX style is REMOVED to satisfy "لا اريد ان يكون في اطارة"
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]
    
    main_style.extend(background_styles)
    main_style.extend(span_styles)

    main_table.setStyle(TableStyle(main_style))
    elements.append(main_table)
    elements.append(Spacer(1, 12))

    # --- Footer ---

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
        # BOX style is REMOVED
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

# Define fields based on the document layout (Updated field 5 label)
fields_map = {
    "(2) Shipper / Exporter": "Shipper / Exporter",
    "(3) Consignee(complete name and address)": "Consignee",
    "(4) Notify Party (complete name and address)": "Notify Party",
    "(5) B/L No. (as Document No.)": "Document No.", # Updated label
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
    
    if key == "Exchange Rate (Cont.)":
        continue
    
    if key in ["Revenue Tons", "Rate", "Per Prepaid", "Collect", "Document No.", "IMO Vessel No.", "B/L No.", "Number of Original B(s)/L"]:
         # Note: 'Document No.' here corresponds to field (5)
         data[key] = st.text_input(label, value="", key=key)
         continue
         
    data[key] = cols[col_index % 3].text_area(label, value="", height=height, key=key)
    col_index += 1


if st.button("Generate Bill of Lading PDF (3 Copies) ⬇️"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=0.5*72, rightMargin=0.5*72, topMargin=0.5*72, bottomMargin=0.5*72)
    
    final_elements = []

    # --- 1st Copy ---
    final_elements.extend(create_bill_of_lading_elements(data, doc))
    final_elements.append(PageBreak()) 

    # --- 2nd Copy ---
    final_elements.extend(create_bill_of_lading_elements(data, doc))
    final_elements.append(PageBreak())

    # --- 3rd Copy (No page break after the last one) ---
    final_elements.extend(create_bill_of_lading_elements(data, doc))
    
    # --- Build Document and Download ---
    
    try:
        doc.build(final_elements)
        buffer.seek(0)
    
        st.download_button(
            label="Download BILLOF-LADING PDF (3 Copies) ⬇️",
            data=buffer,
            file_name=f"{data.get('B/L No.', 'BILLOF_LADING_3_COPIES').replace('/', '_')}.pdf",
            mime="application/pdf"
        )
        st.success("تم إنشاء ملف PDF بثلاث نسخ مطابقة للتصميم المطلوب وبدون إطار خارجي، وتم تعديل العنوان وحقل (5).")
    except Exception as e:
        st.error(f"حدث خطأ أثناء بناء ملف PDF: {e}")
