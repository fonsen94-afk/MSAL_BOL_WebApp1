import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from PIL import Image
import io

# --- 1. منطق إنشاء PDF باستخدام ReportLab ---

# إعداد الأنماط العامة
styles = getSampleStyleSheet()
styles['Normal'].fontName = 'Helvetica'
styles['Normal'].fontSize = 8
styles['Normal'].leading = 10 

# دالة لرسم الرأس والشعار
def header_layout(canvas, doc, data):
    canvas.saveState()
    
    # 1. الشعار والعنوان (أعلى اليسار)
    try:
        logo_path = 'msal_logo.png'
        img = Image.open(logo_path)
        img_width = 1.0 * inch
        img_height = img.height * (img_width / img.width)
        canvas.drawInlineImage(logo_path, 0.5 * inch, letter[1] - 0.9 * inch, width=img_width, height=img_height)
        
        # العنوان بالأسود
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(0.5 * inch, letter[1] - 0.5 * inch, "MCL SHIPPING")

    except FileNotFoundError:
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(0.5 * inch, letter[1] - 0.5 * inch, "MCL SHIPPING (Logo Placeholder)")
    
    # 2. عنوان BILL OF LADING
    canvas.setFont('Helvetica-Bold', 18)
    canvas.drawString(4.5 * inch, letter[1] - 0.75 * inch, "BILL OF LADING")
    
    # 3. خط فاصل أفقي
    canvas.line(0.5 * inch, letter[1] - 1.0 * inch, letter[0] - 0.5 * inch, letter[1] - 1.0 * inch)
    
    # 4. رقم المستند (5) - بالأسود
    doc_no = data.get('(5) Document No.', 'N/A')
    canvas.setFont('Helvetica-Bold', 8)
    canvas.drawString(4.5 * inch, letter[1] - 1.2 * inch, "(5) Document No.")
    
    canvas.setFont('Helvetica', 10)
    canvas.drawString(5.5 * inch, letter[1] - 1.2 * inch, doc_no) 

    canvas.restoreState()


# دالة إنشاء PDF الرئيسية
def generate_bl_pdf(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                            leftMargin=0.5*inch, 
                            rightMargin=0.5*inch, 
                            topMargin=1.5*inch, 
                            bottomMargin=0.5*inch) 

    Story = []
    
    # نمط الحدود (بدون خلفيات)
    border_style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 3),
        # لا يوجد BACKGROUND
    ])
    
    # دالة مساعدة لإنشاء الفقرات بالعنوان الأسود الغامق
    def create_black_label_paragraph(label_text, data_key):
        content = data.get(data_key, '')
        # يتم تطبيق اللون الأسود والخط الغامق على العنوان الأساسي فقط
        return Paragraph(f'<b>{label_text}</b><br/>{content}', styles['Normal'])
    
    # --- القسم العلوي (Parties) ---
    data_upper = [
        [
            create_black_label_paragraph("(2) Shipper / Exporter", '(2) Shipper'), 
            create_black_label_paragraph("(6) Export References", '(6) Export References'),
        ],
        [
            create_black_label_paragraph("(3) Consignee (complete name and address)", '(3) Consignee'), 
            create_black_label_paragraph("(7) Forwarding Agent-References", '(7) Forwarding Agent'),
        ],
        [
            create_black_label_paragraph("(4) Notify Party (complete name and address)", '(4) Notify Party'), 
            create_black_label_paragraph("(8) Point and Country of Origin", '(8) Point and Country'),
        ],
        ['', create_black_label_paragraph("(9) Also Notify Party (complete name and address)", '(9) Also Notify Party')],
    ]
    
    table_upper = Table(data_upper, colWidths=[3.75 * inch, 3.75 * inch])
    table_upper.setStyle(border_style)
    Story.append(table_upper)

    # --- القسم الأوسط (Transport) ---
    data_middle = [
        [
            create_black_label_paragraph("(12) Imo Vesselle No.", '(12) Imo Vesselle No.'), 
            create_black_label_paragraph("(13) Place of Receipt/Date", '(13) Place of Receipt/Date'),
            create_black_label_paragraph("(10) Onward Inland Routing/Export Instructions", '(10) Onward Inland Routing')
        ],
        [
            create_black_label_paragraph("(14) Ocean Vessel/Voy. No.", '(14) Ocean Vessel/Voy. No.'), 
            create_black_label_paragraph("(15) Port of Loading", '(15) Port of Loading'),
            create_black_label_paragraph("(16) Port of Discharge", '(16) Port of Discharge')
        ],
        [
            create_black_label_paragraph("(16) Port of Discharge (Repeat)", '(16) Port of Discharge (Repeat)'),
            create_black_label_paragraph("(17) Place of Delivery", '(17) Place of Delivery'),
            create_black_label_paragraph("(11) Ocean Freight Rate (for Merchant's reference)", '(11) Ocean Freight Rate'),
        ]
    ]
    
    table_middle = Table(data_middle, colWidths=[2.5 * inch, 2.5 * inch, 2.5 * inch])
    table_middle.setStyle(border_style)
    Story.append(table_middle)

    # --- قسم البضائع (Wide Table) ---
    # العنوان بالأسود الغامق
    Story.append(Paragraph('<br/><b>Particulars furnished by the Merchant</b>', styles['Normal']))

    data_goods = [
        # صف العناوين (Headers) - بالأسود الغامق
        [
            Paragraph('<b>(18) Container No. And Seal No. Marks & Nos.</b><br/>CONTAINER NO./SEAL NO.', styles['Normal']),
            Paragraph('<b>(19) Quantity And Kind of Packages</b>', styles['Normal']),
            Paragraph('<b>(20) Description of Goods</b>', styles['Normal']),
            Paragraph('<b>(21) Measurement (M³) Gross Weight (KGS)</b>', styles['Normal']),
        ],
        # صف البيانات (Data)
        [
            data.get('Container No.', ''),
            data.get('Packages Qty.', ''),
            data.get('Description of Goods', ''),
            data.get('Weight/Measure', ''),
        ],
        # صفوف فارغة للمظهر
        *[['','','',''] for _ in range(8)],
    ]
    
    table_goods = Table(data_goods, colWidths=[1.5 * inch, 1.125 * inch, 3.375 * inch, 1.5 * inch])
    table_goods.setStyle(border_style)
    Story.append(table_goods)
    
    # --- القسم السفلي (Charges & Issue) ---
    data_lower = [
        [
            create_black_label_paragraph("(22) TOTAL NUMBER OF CONTAINERS OR PACKAGES (IN WORDS)", '(22) Total in Words'),
            create_black_label_paragraph("(24) FREIGHT & CHARGES", '(24) FREIGHT & CHARGES'), 
            'Revenue Tons', 'Rate', 'Per Prepaid', 'Collect',
        ],
        [
            create_black_label_paragraph("(25) B/L NO.", '(25) B/L No.'), 
            create_black_label_paragraph("(27) Number of Original B(s)/L", '(27) Number of Original'), 
            create_black_label_paragraph("(29) Prepaid at", '(29) Prepaid at'), 
            create_black_label_paragraph("(30) Collect at", '(30) Collect at'),
            create_black_label_paragraph("Signature/Stamp:", 'Digital Signature'), # حقل الإضافة
        ],
        [
            create_black_label_paragraph("(26) Service Type/Mode", '(26) Service Type'), 
            create_black_label_paragraph("(33) Laden on Board", '(33) Laden on Board'), 
            create_black_label_paragraph("(28) Place of B(s)/L Issue/Date", '(28) Place of Issue'), 
            create_black_label_paragraph("(31) Exchange Rate", '(31) Exchange Rate'),
            create_black_label_paragraph("(32) Exchange Rate", '(32) Exchange Rate (Repeat)'),
        ]
    ]
    
    table_lower = Table(data_lower, colWidths=[1.875 * inch, 1.5 * inch, 1.25 * inch, 1.25 * inch, 1.625 * inch])
    table_lower.setStyle(border_style)
    Story.append(table_lower)
    
    # بناء المستند
    doc.build(Story, onFirstPage=lambda canvas, doc: header_layout(canvas, doc, data), onLaterPages=lambda canvas, doc: header_layout(canvas, doc, data))
    
    buffer.seek(0)
    return buffer

# --- 2. تطبيق الويب Streamlit (بدون تغيير في الـ UI) ---

st.set_page_config(layout="wide", page_title="MCL Bill of Lading Generator")

st.title("🚢 نظام إنشاء بوليصة الشحن الإلكترونية (B/L) - النمط القياسي الاحترافي")
st.caption("أدخل البيانات اللازمة لإنشاء مستند PDF (العناوين والبيانات بالأسود، بدون خلفية).")

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
        
    submitted = st.form_submit_button("✅ إنشاء بوليصة الشحن (PDF)")


# --- 3. المعالجة والناتج ---
if submitted:
    st.write("يتم الآن إنشاء ملف بوليصة الشحن...")
    
    try:
        # إنشاء PDF
        pdf_buffer = generate_bl_pdf(data_input)
        
        # زر التحميل
        st.download_button(
            label="⬇️ تحميل بوليصة الشحن (PDF)",
            data=pdf_buffer,
            file_name=f"BOL_{data_input['(5) Document No.']}.pdf",
            mime="application/pdf"
        )
        
        st.success("تم إنشاء الملف بنجاح! يمكنك الآن تحميله. النمط المطبق هو الأسود/الأبيض القياسي.")
        
    except Exception as e:
        st.error(f"حدث خطأ أثناء إنشاء PDF: {e}")

st.markdown("---")
st.markdown("تم التصميم بواسطة Streamlit و ReportLab.")

هل تود تطبيق أي **لون محدد آخر** (مثل الأزرق الداكن أو الأحمر) على العناوين، أم أن النمط الأسود/الأبيض الاحترافي يناسبك؟
