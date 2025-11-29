# msal_bol_webapp_ar_fields_tables.py
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
import io
import os

# ----- إعداد الخطوط العربية (استبدل المسار باسم خط يدعم العربية) -----
# تأكد من أن ملف الخط (مثل Arial.ttf) موجود في نفس المجلد أو قم بتوفير مسار صحيح.
# إذا لم يعمل Arial.ttf، استخدم خطوطًا قياسية مثل NotoSansArabic-Regular.ttf
# For simplicity, we use a basic font here but ReportLab's built-in fonts do not support Arabic well.
# We register one standard font for better rendering, though the built-in 'Helvetica' is used for styles.
pdfmetrics.registerFont(TTFont('ArabicFont', 'Arial.ttf'))
pdfmetrics.registerFont(TTFont('ArabicFont-Bold', 'Arial_Bold.ttf')) # افتراض أن لديك ملف خط للنسخة العريضة

base_font = "Helvetica" # ReportLab internal reference
arabic_font = "ArabicFont"

# ----- Font and Styles -----
styles = getSampleStyleSheet()

green_color = colors.HexColor("#008000") 
black_color = colors.black
light_gray_color = colors.HexColor("#EEEEEE")

# أسماء Styles فريدة - تم تحديث الخط لاستخدام الخط المسجل (إذا كانت الأسماء متوفرة)
styles.add(ParagraphStyle(name='MyTitleGreen', fontName=arabic_font + '-Bold', fontSize=16, leading=20, alignment=1, textColor=green_color, allowOrphans=0, allowWidows=0))
styles.add(ParagraphStyle(name='MyFieldLabelGreen', fontName=arabic_font + '-Bold', fontSize=8, leading=10, textColor=green_color, spaceBefore=2, spaceAfter=2, alignment=0, allowOrphans=0, allowWidows=0))
styles.add(ParagraphStyle(name='MyFieldValueBlack', fontName=arabic_font, fontSize=9, leading=11, textColor=black_color, spaceBefore=2, spaceAfter=2, alignment=0, allowOrphans=0, allowWidows=0))

st.set_page_config(layout="wide")
st.title("MSAL Shipping - Bill of Lading Generator (نموذج المستند) 🚢")

# ----- Logo -----
logo_path = "msal_logo.png"

# ----- Input Fields Definition - مطابقة للمستند المرفق -----
fields_map = {
    "(2) Shipper / Exporter": "Shipper / Exporter",
    "(3) Consignee(complete name and address)": "Consignee",
    "(4) Notify Party (complete name and address)": "Notify Party",
    "(5) Document No.": "Document No.",
    "(6) Export References": "Export References",
    "(7) Forwarding Agent-References": "Forwarding Agent-References",
    "(8) Point and Country of Origin (for the Merchant's reference only)": "Point & Country of Origin",
    "(9) Also Notify Party (complete name and address)": "Also Notify Party",
    "(10) Onward Inland Routing/Export Instructions": "Export Instructions", # اختصار
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
    "(32) Exchange Rate (Cont.)": "Exchange Rate (Cont.)", # تعديل بسيط
    "(33) Laden on Board": "Laden on Board Date",
    "Tracking URL (for QR Code)": "Tracking URL (for QR Code)"
}

data = {}
st.header("إدخال تفاصيل الشحن (مطابقة لتخطيط المستند)")
cols = st.columns(3)
col_index = 0

for label, key in fields_map.items():
    if key == "Description of Goods":
        height = 150
    elif "Shipper" in key or "Consignee" in key or "Notify Party" in key:
        height = 80
    else:
        height = 40
    data[key] = cols[col_index % 3].text_area(label, value="", height=height)
    col_index += 1

# ----- Generate PDF -----
if st.button("توليد ملف PDF مع رمز QR 📄"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=0.5*72, rightMargin=0.5*72, topMargin=0.5*72, bottomMargin=0.5*72)
    elements = []

    # دالة مساعدة لإنشاء الفقرات وإدارة فواصل الأسطر
    def create_cell_content(label, value, is_label=True, font_style='MyFieldValueBlack'):
        style = styles['MyFieldLabelGreen'] if is_label else styles[font_style]
        content = value.replace("\n", "<br/>") if not is_label else label
        return Paragraph(content, style)

    # ----------------------------------------------------
    # 1. Header (Logo and Title) - مطابقة MCL SHIPPING
    # ----------------------------------------------------
    header_data = []

    if logo_path and os.path.exists(logo_path):
        logo_img = Image(logo_path, width=100, height=50)
    else:
        logo_img = create_cell_content("MCL SHIPPING M", "", is_label=False, font_style='MyTitleGreen') # Placeholder [cite: 2]

    title_para = Paragraph("<b>BILL OF LADING</b>", styles['MyTitleGreen']) # [cite: 4]

    header_data.append([
        logo_img,
        title_para,
        create_cell_content("FOR: MCL SHIPPING M", "", is_label=False, font_style='MyFieldValueBlack') # إضافة افتراضية
    ])

    header_table = Table(header_data, colWidths=[doc.width * 0.35, doc.width * 0.40, doc.width * 0.25])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, green_color),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 6))

    # ----------------------------------------------------
    # 2. Main B/L Data Table - تخطيط مشابه للمستند
    # ----------------------------------------------------

    table_data = []

    # تم دمج الصفوف في أزواج (Label + Value) لسهولة التعامل مع SPAN
    # Row 1-2: Shipper (50%) / Consignee (50%)
    table_data.append([
        create_cell_content("(2) Shipper / Exporter", ""), # [cite: 3]
        create_cell_content("(3) Consignee(complete name and address)", "") # [cite: 7]
    ])
    table_data.append([
        create_cell_content("", data["Shipper / Exporter"], is_label=False),
        create_cell_content("", data["Consignee"], is_label=False)
    ])

    # Row 3-4: Notify Party (50%) / Document No. (25%) / Export References (25%)
    # Note: Consignee in original doc often takes 50%, and below it is Notify.
    table_data.append([
        create_cell_content("(4) Notify Party (complete name and address)", ""), # [cite: 9]
        create_cell_content("(5) Document No.", ""), # [cite: 5]
        create_cell_content("(6) Export References", "") # [cite: 6]
    ])
    table_data.append([
        create_cell_content("", data["Notify Party"], is_label=False),
        create_cell_content("", data["Document No."], is_label=False),
        create_cell_content("", data["Export References"], is_label=False)
    ])

    # Row 5-6: Forwarding Agent / Origin
    table_data.append([
        create_cell_content("(7) Forwarding Agent-References", ""), # [cite: 8]
        create_cell_content("(8) Point and Country of Origin (for the Merchant's reference only)", "") # [cite: 22]
    ])
    table_data.append([
        create_cell_content("", data["Forwarding Agent-References"], is_label=False),
        create_cell_content("", data["Point & Country of Origin"], is_label=False)
    ])

    # Row 7-8: Also Notify / Instructions
    table_data.append([
        create_cell_content("(9) Also Notify Party (complete name and address)", ""), # [cite: 23]
        create_cell_content("(10) Onward Inland Routing/Export Instructions (which are contracted separately by Merchants entirely for their own account and risk)", "") # [cite: 24]
    ])
    table_data.append([
        create_cell_content("", data["Also Notify Party"], is_label=False),
        create_cell_content("", data["Export Instructions"], is_label=False)
    ])

    # Row 9-10: Transport Details - Place of Receipt (25%) / Ocean Vessel (25%) / IMO No. (25%) / Port of Loading (25%)
    table_data.append([
        create_cell_content("(13) Place of Receipt/Date", ""), # [cite: 13]
        create_cell_content("(14) Ocean Vessel/Voy. No.", ""), # [cite: 11]
        create_cell_content("(12) Imo Vessele No.", ""), # [cite: 10]
        create_cell_content("(15) Port of Loading", "") # [cite: 14]
    ])
    table_data.append([
        create_cell_content("", data["Place of Receipt / Date"], is_label=False),
        create_cell_content("", data["Ocean Vessel / Voyage No."], is_label=False),
        create_cell_content("", data["IMO Vessel No."], is_label=False),
        create_cell_content("", data["Port of Loading"], is_label=False)
    ])

    # Row 11-12: Port of Discharge (50%) / Place of Delivery (50%)
    table_data.append([
        create_cell_content("(16) Port of Discharge", ""), # [cite: 12]
        create_cell_content("(17) Place of Delivery", "") # [cite: 15]
    ])
    table_data.append([
        create_cell_content("", data["Port of Discharge"], is_label=False),
        create_cell_content("", data["Place of Delivery"], is_label=False)
    ])

    # Row 13-14: Marks & Nos. (20%) / Container No./Seal No. (20%) / Packages (10%) / Description (50%)
    table_data.append([
        create_cell_content("Marks & Nos.", ""), # [cite: 16]
        create_cell_content("(18) Container No. And Seal No.", ""), # [cite: 16]
        create_cell_content("(19) Quantity And Kind of Packages", ""), # [cite: 20]
        create_cell_content("(20) Description of Goods", "") # 
    ])
    table_data.append([
        create_cell_content("", data["Marks & Nos."], is_label=False),
        create_cell_content("", data["Container No. / Seal No."], is_label=False),
        create_cell_content("", data["Quantity & Kind of Packages"], is_label=False),
        create_cell_content("", data["Description of Goods"], is_label=False)
    ])

    # Row 15-16: Revenue Tons (10%) / Rate (10%) / Per Prepaid (10%) / Collect (10%) / Measurement (30%) / Total Containers (30%)
    table_data.append([
        create_cell_content("Revenue Tons", ""), # [cite: 30]
        create_cell_content("Rate", ""), # [cite: 31]
        create_cell_content("Per Prepaid", ""), # [cite: 32]
        create_cell_content("Collect", ""), # [cite: 33]
        create_cell_content("(21) Measurement (M³) Gross Weight (KGS)", ""), # [cite: 34]
        create_cell_content("(22) TOTAL NUMBER OF CONTAINERS OR PACKAGES (IN WORDS)", "") # [cite: 18]
    ])
    table_data.append([
        create_cell_content("", data.get("Revenue Tons", ""), is_label=False),
        create_cell_content("", data.get("Rate", ""), is_label=False),
        create_cell_content("", data.get("Per Prepaid", ""), is_label=False),
        create_cell_content("", data.get("Collect", ""), is_label=False),
        create_cell_content("", data["Measurement / Gross Weight"], is_label=False),
        create_cell_content("", data["Total Containers / Packages"], is_label=False)
    ])

    # Row 17-18: Freight & Charges (50%) / B/L No. (25%) / Service Type (25%)
    table_data.append([
        create_cell_content("(24) FREIGHT & CHARGES", ""), # [cite: 19]
        create_cell_content("(25) B/L NO.", ""), # [cite: 35]
        create_cell_content("(26) Service Type/Mode", "") # [cite: 42]
    ])
    table_data.append([
        create_cell_content("", data["Freight & Charges"], is_label=False),
        create_cell_content("", data["B/L No."], is_label=False),
        create_cell_content("", data["Service Type / Mode"], is_label=False)
    ])

    # Row 19-20: Originals (25%) / Issue Date (25%) / Prepaid at (25%) / Collect at (25%)
    table_data.append([
        create_cell_content("(27) Number of Original B(s)/L", ""), # [cite: 36]
        create_cell_content("(28) Place of B(s)/L Issue/Date", ""), # [cite: 39]
        create_cell_content("(29) Prepaid at", ""), # [cite: 37]
        create_cell_content("(30) Collect at", "") # [cite: 38]
    ])
    table_data.append([
        create_cell_content("", data["Number of Original B(s)/L"], is_label=False),
        create_cell_content("", data["Place of B(s)/L Issue / Date"], is_label=False),
        create_cell_content("", data["Prepaid at"], is_label=False),
        create_cell_content("", data["Collect at"], is_label=False)
    ])
    
    # Row 21-22: Exchange Rate (50%) / Laden on Board (50%)
    table_data.append([
        create_cell_content("(31) Exchange Rate / (32) Exchange Rate (Cont.)", ""), # [cite: 40, 41]
        create_cell_content("(33) Laden on Board", "") # [cite: 43]
    ])
    table_data.append([
        create_cell_content("", data["Exchange Rate"], is_label=False),
        create_cell_content("", data["Laden on Board Date"], is_label=False)
    ])


    # ----------------------------------------------------
    # Table Styling and Column Widths (Primary 4-column structure)
    # ----------------------------------------------------

    # استخدام 6 أعمدة أساسية لتمثيل التخطيطات المختلفة
    col_widths = [doc.width * 0.166] * 6 # 6 أعمدة متساوية 

    main_table = Table(table_data, colWidths=col_widths)

    main_style = [
        ('GRID', (0, 0), (-1, -1), 0.5, green_color),
        ('BOX', (0, 0), (-1, -1), 1, black_color),

        # خلفية خضراء خفيفة للعناوين (Labels) - الصفوف الزوجية (0, 2, 4, ...)
        for i in range(len(table_data)):
            if i % 2 == 0:
                 main_style.append(('BACKGROUND', (0, i), (-1, i), light_gray_color))
        
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),

        # --- دمج الخلايا لـ 50% / 50% ---
        # Shipper/Consignee (Row 0, 1) - Col 0-2 & Col 3-5
        ('SPAN', (0, 0), (2, 0)), ('SPAN', (3, 0), (5, 0)),
        ('SPAN', (0, 1), (2, 1)), ('SPAN', (3, 1), (5, 1)),
        # Notify Party (Row 2, 3) - Col 0-2
        ('SPAN', (0, 2), (2, 2)), ('SPAN', (0, 3), (2, 3)),
        # Forwarding Agent / Origin (Row 4, 5) - 50%/50%
        ('SPAN', (0, 4), (2, 4)), ('SPAN', (3, 4), (5, 4)),
        ('SPAN', (0, 5), (2, 5)), ('SPAN', (3, 5), (5, 5)),
        # Also Notify / Instructions (Row 6, 7) - 50%/50%
        ('SPAN', (0, 6), (2, 6)), ('SPAN', (3, 6), (5, 6)),
        ('SPAN', (0, 7), (2, 7)), ('SPAN', (3, 7), (5, 7)),
        # Port of Discharge / Place of Delivery (Row 10, 11) - 50%/50%
        ('SPAN', (0, 10), (2, 10)), ('SPAN', (3, 10), (5, 10)),
        ('SPAN', (0, 11), (2, 11)), ('SPAN', (3, 11), (5, 11)),
        # Freight & Charges (Row 16, 17) - Col 0-2
        ('SPAN', (0, 16), (2, 16)), ('SPAN', (0, 17), (2, 17)),
        # Exchange Rate / Laden on Board (Row 20, 21) - 50%/50%
        ('SPAN', (0, 20), (2, 20)), ('SPAN', (3, 20), (5, 20)),
        ('SPAN', (0, 21), (2, 21)), ('SPAN', (3, 21), (5, 21)),

        # --- دمج الخلايا لتغطية حقل Description of Goods (Row 12, 13) ---
        # Marks & Nos. (1/6) / Container No. (1/6) / Packages (1/6) / Description (3/6)
        # Packages (Col 2) / Description (Col 3-5)
        ('SPAN', (3, 12), (5, 12)), # Description Label
        ('SPAN', (3, 13), (5, 13)), # Description Value

        # --- دمج الخلايا لحقل Freight & Charges (Row 16, 17) ---
        # Freight & Charges (50%) / B/L No. (25%) / Service Type (25%)
        ('SPAN', (0, 16), (2, 16)),
        ('SPAN', (0, 17), (2, 17)),
        ('SPAN', (3, 16), (4, 16)), # B/L No. (2 columns - 3, 4)
        ('SPAN', (3, 17), (4, 17)), # B/L No. Value

        # --- دمج الخلايا لحقل Document No. & Export References (Row 2, 3) ---
        # Document No. (Col 3) / Export Ref (Col 4-5)
        ('SPAN', (4, 2), (5, 2)), # Export References Label
        ('SPAN', (4, 3), (5, 3)), # Export References Value

        # --- دمج الخلايا لحقل Revenue Tons (Row 14, 15) ---
        # Revenue Tons (1/6) / Rate (1/6) / Per Prepaid (1/6) / Collect (1/6) / Measurement (2/6) / Total Containers (2/6)
        ('SPAN', (4, 14), (5, 14)), # Measurement Label
        ('SPAN', (4, 15), (5, 15)), # Measurement Value
        ('SPAN', (4, 16), (5, 16)), # Total Containers Label
        ('SPAN', (4, 17), (5, 17)), # Total Containers Value
    ]

    main_table.setStyle(TableStyle(main_style))
    elements.append(main_table)
    elements.append(Spacer(1, 12))

    # ----------------------------------------------------
    # 3. Footer / QR Code
    # ----------------------------------------------------

    tracking_url = data.get("Tracking URL (for QR Code)", "")
    
    if tracking_url:
        qr = qrcode.QRCode(box_size=3, border=2)
        qr.add_data(tracking_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)
        qr_image = Image(qr_buffer, width=70, height=70)

        # جدول التوقيع و QR
        footer_table = Table([
            [
                create_cell_content("Tracking QR Code", ""),
                create_cell_content("", ""), # خلية فارغة
                create_cell_content("For MCL Shipping M", "", font_style='MyTitleGreen')
            ],
            [
                qr_image,
                create_cell_content("", "RECEIPT IS ACKNOWLEDGED BY THE SHIPPER", is_label=False),
                create_cell_content("", "Authorized Signature", is_label=False)
            ]
        ], colWidths=[doc.width * 0.2, doc.width * 0.4, doc.width * 0.4])

        footer_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, green_color),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(footer_table)
    
    # ----------------------------------------------------
    # Build Document and Download
    # ----------------------------------------------------
    
    try:
        doc.build(elements)
        buffer.seek(0)
    
        st.download_button(
            label="تحميل بوليصة الشحن PDF ⬇️",
            data=buffer,
            file_name=f"{data.get('B/L No.', 'BILL_OF_LADING').replace('/', '_')}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"حدث خطأ أثناء توليد ملف PDF. تأكد من توفر ملفات الخطوط العربية (Arial.ttf): {e}")