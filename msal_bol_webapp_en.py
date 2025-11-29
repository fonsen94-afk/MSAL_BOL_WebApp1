import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from PIL import Image # For Logo handling
import io

# --- 1. REPORTLAB PDF GENERATION LOGIC (NO QR CODE) ---

# Setup general styles
styles = getSampleStyleSheet()
styles['Normal'].fontName = 'Helvetica'
styles['Normal'].fontSize = 8
styles['Normal'].leading = 10 # Adjust line spacing for better fit

# Function to draw the header and logo
def header_layout(canvas, doc, data):
    canvas.saveState()
    
    # 1. Logo and Title (Top Left)
    try:
        logo_path = 'msal_logo.png'
        img = Image.open(logo_path)
        img_width = 1.0 * inch
        img_height = img.height * (img_width / img.width)
        # Draw the logo
        canvas.drawInlineImage(logo_path, 0.5 * inch, letter[1] - 0.9 * inch, width=img_width, height=img_height)
        
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(0.5 * inch, letter[1] - 0.5 * inch, "MCL SHIPPING")

    except FileNotFoundError:
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(0.5 * inch, letter[1] - 0.5 * inch, "MCL SHIPPING (Logo Placeholder)")
    
    # 2. BILL OF LADING Title (Top Right Center)
    canvas.setFont('Helvetica-Bold', 18)
    canvas.drawString(4.5 * inch, letter[1] - 0.75 * inch, "BILL OF LADING")
    
    # 3. Horizontal Separator Line
    canvas.line(0.5 * inch, letter[1] - 1.0 * inch, letter[0] - 0.5 * inch, letter[1] - 1.0 * inch)
    
    # 4. Document No. (5)
    doc_no = data.get('(5) Document No.', 'N/A')
    canvas.setFont('Helvetica-Bold', 8)
    canvas.drawString(4.5 * inch, letter[1] - 1.2 * inch, "(5) Document No.")
    canvas.setFont('Helvetica', 10)
    canvas.drawString(5.5 * inch, letter[1] - 1.2 * inch, doc_no) 

    canvas.restoreState()


# Main PDF generation function
def generate_bl_pdf(data):
    buffer = io.BytesIO()
    # Adjusted bottom margin back to standard since no QR code is added
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                            leftMargin=0.5*inch, 
                            rightMargin=0.5*inch, 
                            topMargin=1.5*inch, 
                            bottomMargin=0.5*inch) 

    Story = []
    
    # Style for borders and text alignment
    border_style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 3),
        ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke), # For header row in goods section
    ])
    
    # --- UPPER SECTION (Parties) ---
    data_upper = [
        [
            Paragraph("<b>(2) Shipper / Exporter</b><br/>" + data.get('(2) Shipper', ''), styles['Normal']), 
            Paragraph("<b>(6) Export References</b><br/>" + data.get('(6) Export References', ''), styles['Normal']),
        ],
        [
            Paragraph("<b>(3) Consignee (complete name and address)</b><br/>" + data.get('(3) Consignee', ''), styles['Normal']), 
            Paragraph("<b>(7) Forwarding Agent-References</b><br/>" + data.get('(7) Forwarding Agent', ''), styles['Normal']),
        ],
        [
            Paragraph("<b>(4) Notify Party (complete name and address)</b><br/>" + data.get('(4) Notify Party', ''), styles['Normal']), 
            Paragraph("<b>(8) Point and Country of Origin</b><br/>" + data.get('(8) Point and Country', ''), styles['Normal']),
        ],
        ['', Paragraph("<b>(9) Also Notify Party (complete name and address)</b><br/>" + data.get('(9) Also Notify Party', ''), styles['Normal'])],
    ]
    
    table_upper = Table(data_upper, colWidths=[3.75 * inch, 3.75 * inch])
    table_upper.setStyle(border_style)
    Story.append(table_upper)

    # --- MIDDLE SECTION (Transport) ---
    data_middle = [
        [
            Paragraph("<b>(12) Imo Vesselle No.</b><br/>" + data.get('(12) Imo Vesselle No.', ''), styles['Normal']), 
            Paragraph("<b>(13) Place of Receipt/Date</b><br/>" + data.get('(13) Place of Receipt/Date', ''), styles['Normal']),
            Paragraph("<b>(10) Onward Inland Routing/Export Instructions</b><br/>" + data.get('(10) Onward Inland Routing', ''), styles['Normal'])
        ],
        [
            Paragraph("<b>(14) Ocean Vessel/Voy. No.</b><br/>" + data.get('(14) Ocean Vessel/Voy. No.', ''), styles['Normal']), 
            Paragraph("<b>(15) Port of Loading</b><br/>" + data.get('(15) Port of Loading', ''), styles['Normal']),
            Paragraph("<b>(16) Port of Discharge</b><br/>" + data.get('(16) Port of Discharge', ''), styles['Normal'])
        ],
        [
            Paragraph("<b>(16) Port of Discharge</b><br/>" + data.get('(16) Port of Discharge (Repeat)', ''), styles['Normal']),
            Paragraph("<b>(17) Place of Delivery</b><br/>" + data.get('(17) Place of Delivery', ''), styles['Normal']),
            Paragraph("<b>(11) Ocean Freight Rate (for Merchant's reference)</b>", styles['Normal']),
        ]
    ]
    
    table_middle = Table(data_middle, colWidths=[2.5 * inch, 2.5 * inch, 2.5 * inch])
    table_middle.setStyle(border_style)
    Story.append(table_middle)

    # --- GOODS SECTION (Wide Table) ---
    Story.append(Paragraph("<br/><b>Particulars furnished by the Merchant</b>", styles['Normal']))

    data_goods = [
        # Header Row
        [
            Paragraph("<b>(18) Container No. And Seal No. Marks & Nos.</b><br/>CONTAINER NO./SEAL NO.", styles['Normal']),
            Paragraph("<b>(19) Quantity And Kind of Packages</b>", styles['Normal']),
            Paragraph("<b>(20) Description of Goods</b>", styles['Normal']),
            Paragraph("<b>(21) Measurement (M³) Gross Weight (KGS)</b>", styles['Normal']),
        ],
        # Data Row
        [
            data.get('Container No.', ''),
            data.get('Packages Qty.', ''),
            data.get('Description of Goods', ''),
            data.get('Weight/Measure', ''),
        ],
        # Placeholder rows for form appearance
        *[['','','',''] for _ in range(8)],
    ]
    
    table_goods = Table(data_goods, colWidths=[1.5 * inch, 1.125 * inch, 3.375 * inch, 1.5 * inch])
    table_goods.setStyle(border_style)
    Story.append(table_goods)
    
    # --- LOWER SECTION (Charges & Issue) ---
    
    # Columns for Freight & Charges section (24)
    charges_header = Table([
        ['(24) FREIGHT & CHARGES', 'Revenue Tons', 'Rate', 'Per Prepaid', 'Collect']
    ], colWidths=[1.875 * inch, 1.25 * inch, 1.25 * inch, 1.25 * inch, 1.875 * inch])
    charges_header.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
    ]))
    
    data_lower = [
        # Row 1: (22) Total & (24) Charges Header (merged with placeholder columns for alignment)
        [
            Paragraph("<b>(22) TOTAL NUMBER OF CONTAINERS OR PACKAGES (IN WORDS)</b><br/>" + data.get('(22) Total in Words', ''), styles['Normal']),
            Paragraph("<b>(24) FREIGHT & CHARGES</b><br/>", styles['Normal']), 
            '', 
            '', 
            '',
        ],
        # Row 2: B/L No., Number of Originals, Prepaid, Collect
        [
            Paragraph("<b>(25) B/L NO.</b><br/>" + data.get('(25) B/L No.', ''), styles['Normal']), 
            Paragraph("<b>(27) Number of Original B(s)/L</b><br/>" + str(data.get('(27) Number of Original', '')), styles['Normal']), 
            Paragraph("<b>(29) Prepaid at</b><br/>" + data.get('(29) Prepaid at', ''), styles['Normal']), 
            Paragraph("<b>(30) Collect at</b><br/>" + data.get('(30) Collect at', ''), styles['Normal']),
            Paragraph("<b>Signature/Stamp:</b><br/>" + data.get('Digital Signature', ''), styles['Normal']), # Addition Field
        ],
        # Row 3: Service Type, Laden on Board, Place/Date, Exchange Rates
        [
            Paragraph("<b>(26) Service Type/Mode</b><br/>" + data.get('(26) Service Type', ''), styles['Normal']), 
            Paragraph("<b>(33) Laden on Board</b><br/>" + data.get('(33) Laden on Board', ''), styles['Normal']), 
            Paragraph("<b>(28) Place of B(s)/L Issue/Date</b><br/>" + data.get('(28) Place of Issue', ''), styles['Normal']), 
            Paragraph("<b>(31) Exchange Rate</b><br/>" + data.get('(31) Exchange Rate', ''), styles['Normal']),
            Paragraph("<b>(32) Exchange Rate</b><br/>" + data.get('(32) Exchange Rate (Repeat)', ''), styles['Normal']),
        ]
    ]
    
    # Column widths adjusted slightly for better flow without the QR Code slot
    table_lower = Table(data_lower, colWidths=[1.875 * inch, 1.5 * inch, 1.25 * inch, 1.25 * inch, 1.625 * inch])
    table_lower.setStyle(border_style)
    Story.append(table_lower)
    
    # Build the document
    doc.build(Story, onFirstPage=lambda canvas, doc: header_layout(canvas, doc, data), onLaterPages=lambda canvas, doc: header_layout(canvas, doc, data))
    
    buffer.seek(0)
    return buffer

# --- 2. STREAMLIT WEB APPLICATION ---

st.set_page_config(layout="wide", page_title="MCL Bill of Lading Generator")

st.title("🚢 Electronic Bill of Lading (B/L) Generator")
st.caption("Enter the required data to generate a PDF document matching the B/L template.")

data_input = {}

with st.form("bl_form"):
    
    # --- PART 1: Parties and References ---
    st.header("1. Parties and References")
    
    col1, col2 = st.columns(2)
    
    with col1:
        data_input['(2) Shipper'] = st.text_area("2. Shipper / Exporter (Full Name and Address)", height=70, value="XYZ Trading Co. Ltd.\n123 Logistics Blvd, Dubai, UAE")
        data_input['(3) Consignee'] = st.text_area("3. Consignee (Full Name and Address)", height=70, value="ABC Importers Inc.\n456 Port Road, Rotterdam, NL")
        data_input['(4) Notify Party'] = st.text_area("4. Notify Party (Full Name and Address)", height=70, value="Same as Consignee")
    with col2:
        data_input['(5) Document No.'] = st.text_input("5. Document No. (B/L No.)", value="MCLDUBAIRDM24001")
        data_input['(6) Export References'] = st.text_input("6. Export References")
        data_input['(7) Forwarding Agent'] = st.text_area("7. Forwarding Agent-References", height=70)
        data_input['(8) Point and Country'] = st.text_input("8. Point and Country of Origin")
        data_input['(9) Also Notify Party'] = st.text_area("9. Also Notify Party", height=50)

    # --- PART 2: Transport and Ports ---
    st.header("2. Transport and Ports")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        data_input['(12) Imo Vesselle No.'] = st.text_input("12. Imo Vesselle No.")
        data_input['(14) Ocean Vessel/Voy. No.'] = st.text_input("14. Ocean Vessel/Voy. No.", value="MSC ROME V. 245A")
        data_input['(16) Port of Discharge (Repeat)'] = st.text_input("16. Port of Discharge (Repeat)", value="Rotterdam, NL")
    with col4:
        data_input['(13) Place of Receipt/Date'] = st.text_input("13. Place of Receipt/Date")
        data_input['(15) Port of Loading'] = st.text_input("15. Port of Loading", value="Jebel Ali, UAE")
        data_input['(17) Place of Delivery'] = st.text_input("17. Place of Delivery")
    with col5:
        data_input['(10) Onward Inland Routing'] = st.text_area("10. Onward Inland Routing/Export Instructions", height=50)
        data_input['(11) Ocean Freight Rate'] = st.text_input("11. Ocean Freight Rate (for reference)")
        data_input['(16) Port of Discharge'] = st.text_input("16. Port of Discharge", value="Rotterdam, NL")


    # --- PART 3: Goods Description ---
    st.header("3. Goods Description and Quantity")
    col6, col7 = st.columns([1, 2])
    
    with col6:
        data_input['Container No.'] = st.text_area("18. Container No. / Seal No. / Marks & Nos.", value="TGBU1234567 / SEAL001", height=100)
        data_input['Packages Qty.'] = st.text_input("19. Quantity And Kind of Packages", value="10 Cartons")
        data_input['Weight/Measure'] = st.text_input("21. Gross Weight (KGS) / Measurement (M³)", value="5,000 KGS / 10.5 M³")
    with col7:
        data_input['Description of Goods'] = st.text_area("20. Description of Goods", value="FROZEN SEAFOOD\nHS Code: 0306.90.00\nTemperature: -18°C", height=100)
        data_input['(22) Total in Words'] = st.text_input("22. Total Number of Containers or Packages (IN WORDS)", value="TEN CARTONS ONLY")

    # --- PART 4: Charges and Issue ---
    st.header("4. Freight, Charges, and Issue")
    col8, col9, col10 = st.columns(3)
    
    with col8:
        data_input['(25) B/L No.'] = st.text_input("25. B/L NO. (Repeat)", value=data_input['(5) Document No.'])
        data_input['(26) Service Type'] = st.text_input("26. Service Type/Mode", value="CY/CY")
        data_input['(33) Laden on Board'] = st.text_input("33. Laden on Board (Date/Time)")
    with col9:
        data_input['(27) Number of Original'] = st.number_input("27. Number of Original B(s)/L", min_value=1, value=3)
        data_input['(28) Place of Issue'] = st.text_input("28. Place of B(s)/L Issue/Date", value="DUBAI, 29/11/2025")
        data_input['Digital Signature'] = st.text_input("Digital Signature / Authorized Person (Addition)", value="Khaled A. - Operations Manager")
    with col10:
        data_input['(29) Prepaid at'] = st.text_input("29. Prepaid at")
        data_input['(30) Collect at'] = st.text_input("30. Collect at")
        data_input['(31) Exchange Rate'] = st.text_input("31. Exchange Rate")
        data_input['(32) Exchange Rate (Repeat)'] = st.text_input("32. Exchange Rate (Repeat)")
        
    submitted = st.form_submit_button("✅ Generate Bill of Lading (PDF)")


# --- 3. PROCESSING AND OUTPUT ---
if submitted:
    st.write("Generating Bill of Lading PDF...")
    
    try:
        # Generate PDF
        pdf_buffer = generate_bl_pdf(data_input)
        
        # Download Button
        st.download_button(
            label="⬇️ Download Bill of Lading PDF",
            data=pdf_buffer,
            file_name=f"BOL_{data_input['(5) Document No.']}.pdf",
            mime="application/pdf"
        )
        
        st.success("File created successfully! You can download it now.")
        
    except Exception as e:
        st.error(f"An error occurred during PDF creation: {e}")

st.markdown("---")
st.markdown("Powered by Streamlit and ReportLab.")
