import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import os 
from PIL import Image as PilImage 

# 🚨 تعريف الألوان المطابقة للتصميم
DARK_GREEN = colors.Color(0/255, 128/255, 0/255) 
DARK_GREEN_HEX = '#008000' # اللون الأخضر بصيغة HEX للدمج مع نصوص ReportLab
LIGHT_GREEN_BG = colors.Color(230/255, 255/255, 230/255) 

# مسار الشعار
LOGO_PATH = "msal_logo.png" 

# 1. دالة إنشاء محتوى PDF
def create_pdf(data):
    """
    تنشئ محتوى سند الشحن كملف PDF في الذاكرة، بمطابقة تصميم الصورة وتوزيع الألوان.
    """
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )
    
    styles = getSampleStyleSheet()
    
    main_title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['h1'],
        fontSize=18,
        alignment=1,
        spaceAfter=5,
        textColor=DARK_GREEN 
    )
    
    # نمط النص الفرعي (يستخدم للبيانات) - لونه أسود افتراضيًا
    cell_style = styles['Normal']
    cell_style.fontSize = 8
    cell_style.leading = 11
    
    # نمط رؤوس الجداول الكبيرة (يكون النص فيه كاملاً بالأخضر)
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=cell_style,
        fontName='Helvetica-Bold',
        textColor=DARK_GREEN
    )

    elements = []
    
    # --- إضافة الشعار والعنوان ---
    logo_cell = None 
    
    if os.path.exists(LOGO_PATH):
        try:
            pil_img = PilImage.open(LOGO_PATH)
            pil_img_resized = pil_img.resize((int(1.0 * inch * 96), int(0.5 * inch * 96)))
            img_buffer = io.BytesIO()
            pil_img_resized.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            logo_cell = Image(img_buffer, width=1.0 * inch, height=0.5 * inch)
        except Exception:
            logo_cell = Paragraph("<b>MCL SHIPPING</b>", header_style)
    else:
        logo_cell = Paragraph("<b>MCL SHIPPING</b>", header_style)

    title_cell = Paragraph("BILL OF LADING", main_title_style)

    header_table = Table(
        [[logo_cell, title_cell]], 
        [1.5 * inch, 6.5 * inch] 
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('LEFTPADDING', (1, 0), (1, 0), 0)
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.1 * inch))
    
    # دالة مساعدة لتنسيق البيانات في الخلايا 
    def format_cell(title, key, height=0.7 * inch):
        content = str(data.get(key, 'N/A'))
        
        # 🚨 التعديل: جعل العنوان أخضر باستخدام وسم <font> والباقي أسود (لون cell_style الافتراضي)
        title_html = f'<font color="{DARK_GREEN_HEX}"><b>({title})</b></font>'
        
        p = Paragraph(f"{title_html}<br/>{content}", cell_style)
        return p

    # --- جداول المعلومات الرئيسية (الصف العلوي) ---
    
    info_data_upper = [
        [
            format_cell("2) Shipper / Exporter:", 'shipper'),
            format_cell("5) Document No.:", 'doc_no'),
        ],
        [
            format_cell("3) Consignee (complete name and address):", 'consignee'),
            format_cell("7) Forwarding Agent / References:", 'fwd_agent'),
        ],
        [
            format_cell("4) Notify Party (complete name and address):", 'notify_party', height=0.8 * inch), 
            format_cell("8) Point and Country of Origin (for the Merchant's reference only):", 'origin', height=0.8 * inch),
        ],
        [
             # هنا نستخدم header_style لأنها خلايا رؤوس كاملة
             Paragraph("<b>(12) Imo Vessel No.</b>", header_style),
             Paragraph("<b>(9) Also Notify Party (complete name and address)</b>", header_style)
        ],
        [
            format_cell("12) Imo Vessel No. / (13) Place of Receipt/Date", 'imo_place'),
            format_cell("9) Also Notify Party:", 'also_notify_party'),
        ],
        [
            format_cell("14) Ocean Vessel / Voy. No. / (15) Port of Loading", 'vessel_voyage_loading'),
            format_cell("10) Onward Inland Routing/Export Instructions:", 'inland_export_inst'),
        ],
        [
            format_cell("16) Port of Discharge / (17) Place of Delivery", 'discharge_delivery'),
            Paragraph("", cell_style) 
        ],
    ]
    
    upper_col_widths = [4.0 * inch, 4.0 * inch]
    t_upper = Table(info_data_upper, upper_col_widths, repeatRows=0)
    
    t_upper.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, DARK_GREEN), 
        ('ROWHEIGHTS', (0, 0), (1, -1), 0.7 * inch),
        ('ROWHEIGHTS', (2, 2), (2, 2), 0.8 * inch),
        ('ROWHEIGHTS', (3, 3), (3, 3), 0.3 * inch), 
        ('ROWHEIGHTS', (4, 4), (-1, -1), 0.7 * inch),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 3), (-1, 3), LIGHT_GREEN_BG), 
    ]))

    elements.append(t_upper)
    elements.append(Spacer(1, 0.1 * inch))

    # --- جدول البضائع (الجزء الأوسط) ---
    
    goods_header = [
        [
            Paragraph("<b>(18) Container No. And Seal No.<br/>Marks & Nos.</b>", header_style), 
            Paragraph("<b>(19) Quantity and Kind of Packages</b>", header_style), 
            Paragraph("<b>Particulars furnished by the Merchant</b>", header_style),
            Paragraph("<b>(21) Measurement (M³)<br/>Gross Weight (KGS)</b>", header_style)
        ],
        [
            # هنا نستخدم cell_style لأنها نصوص فرعية تحت العنوان الأخضر (18)
            Paragraph("CONTAINER NO./SEAL NO.", cell_style),
            Paragraph("Marks & Nos.", cell_style),
            Paragraph("(20) Description of Goods", cell_style),
            Paragraph("", cell_style) 
        ]
    ]
    
    # هذه الخلية يجب أن تكون خضراء بالكامل (رأس الجدول)
    goods_header[0][2] = Paragraph("<b>Particulars furnished by the Merchant</b>", header_style)

    goods_data = [
        [
            str(data.get('container_no', 'N/A')), 
            str(data.get('quantity', 'N/A')), 
            Paragraph(str(data.get('description', 'N/A')), cell_style), 
            str(data.get('weight', 'N/A'))
        ]
    ]
    
    table_goods_full = goods_header + goods_data
    
    goods_col_widths = [2.0 * inch, 1.5 * inch, 3.5 * inch, 1.0 * inch] 
    t_goods = Table(table_goods_full, goods_col_widths, repeatRows=2)
    
    t_goods.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, DARK_GREEN),
        ('SPAN', (2, 0), (3, 0)), 
        
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, 1), LIGHT_GREEN_BG), 
        ('ROWHEIGHTS', (0, 0), (0, 0), 0.4 * inch),
        ('ROWHEIGHTS', (1, 1), (1, 1), 0.4 * inch),
        ('ROWHEIGHTS', (2, 2), (-1, -1), 2.0 * inch) 
    ]))

    elements.append(t_goods)
    elements.append(Spacer(1, 0.1 * inch))
    
    # --- جدول الشحن والرسوم (الجزء السفلي) ---
    
    footer_data = [
        [
            format_cell("22) TOTAL NUMBER OF CONTAINERS OR PACKAGES (IN WORDS)", 'total_packages'),
            # هذه الأعمدة هي عناوين (Headers)
            Paragraph("Revenue Tons", header_style),
            Paragraph("Rate", header_style),
            Paragraph("Per Prepaid", header_style),
            Paragraph("Collect", header_style)
        ],
        [
            format_cell("24) FREIGHT & CHARGES", 'freight_charges'),
            # هذه بيانات (Data)
            Paragraph(str(data.get('rev_tons', 'N/A')), cell_style),
            Paragraph(str(data.get('rate', 'N/A')), cell_style),
            Paragraph(str(data.get('per_prepaid', 'N/A')), cell_style),
            Paragraph(str(data.get('collect', 'N/A')), cell_style),
        ],
    ]

    footer_col_widths = [3.0 * inch, 1.25 * inch, 1.25 * inch, 1.25 * inch, 1.25 * inch]
    t_footer = Table(footer_data, footer_col_widths, repeatRows=0)
    
    t_footer.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, DARK_GREEN),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (1, 0), (-1, 0), LIGHT_GREEN_BG), 
        ('ROWHEIGHTS', (0, 0), (0, 0), 0.5 * inch), 
        ('ROWHEIGHTS', (1, 1), (-1, -1), 0.7 * inch), 
    ]))
    
    elements.append(t_footer)
    elements.append(Spacer(1, 0.1 * inch))
    
    # --- الجدول النهائي (التوقيع والتواريخ) ---
    
    final_data = [
        [
            format_cell("25) B/L NO.", 'final_bl_no'),
            format_cell("27) Number of Original B(s)/L", 'original_bl_no'),
            format_cell("29) Prepaid at", 'prepaid_at'),
            format_cell("30) Collect at", 'collect_at'),
        ],
        [
            format_cell("26) Service Type/Mode", 'service_type'),
            format_cell("28) Place of B(s)/L Issue/Date", 'issue_place_date'),
            format_cell("31) Exchange Rate", 'exchange_rate'),
            format_cell("32) Exchange Rate", 'exchange_rate_2'),
        ],
        [
             format_cell("33) Laden on Board", 'laden_on_board'),
             Paragraph("", cell_style),
             Paragraph("", cell_style),
             Paragraph("", cell_style)
        ]
    ]

    final_col_widths = [2.0 * inch, 2.0 * inch, 2.0 * inch, 2.0 * inch]
    t_final = Table(final_data, final_col_widths, repeatRows=0)

    t_final.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, DARK_GREEN),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWHEIGHTS', (0, 0), (-1, -1), 0.5 * inch),
        ('ROWHEIGHTS', (2, 2), (2, 2), 0.7 * inch),
    ]))
    
    elements.append(t_final)

    # --- بناء المستند والحفظ ---
    doc.build(elements)
    
    buffer.seek(0)
    return buffer

# 2. دالة واجهة Streamlit (main)
def main():
    st.set_page_config(layout="wide", page_title="أداة سند الشحن (مطابق)")
    
    st.title("🚢 أداة إنشاء سند الشحن (مطابقة التصميم الأصلي)")
    
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=100)
    
    st.markdown("---")
    
    # --- جمع البيانات الافتراضية ---
    data = {}
    
    with st.expander("بيانات الشاحن والمستلم والموانئ"):
        col1, col2 = st.columns(2)
        with col1:
            data['shipper'] = st.text_area("(2) Shipper / Exporter:", "M.L. General Trading LLC, Dubai", height=50)
            data['consignee'] = st.text_area("(3) Consignee:", "Ahmad Logistics, Jeddah", height=50)
            data['notify_party'] = st.text_area("(4) Notify Party:", "Same as Consignee", height=50)
            data['imo_place'] = st.text_input("(12) Imo Vessel No. / (13) Place of Receipt/Date:", "IMO-12345 / London, 01/01/2025")
            data['vessel_voyage_loading'] = st.text_input("(14) Ocean Vessel / Voy. No. / (15) Port of Loading:", "Maersk-001 / Jebel Ali, UAE")
            data['discharge_delivery'] = st.text_input("(16) Port of Discharge / (17) Place of Delivery:", "King Abdullah Port, KSA / Riyadh")

        with col2:
            data['doc_no'] = st.text_input("(5) Document No.:", "MCL-BL-123456")
            data['fwd_agent'] = st.text_input("(7) Forwarding Agent / References:", "Fast Global Movers")
            data['origin'] = st.text_input("(8) Point and Country of Origin:", "Hamburg, Germany")
            data['also_notify_party'] = st.text_area("(9) Also Notify Party:", "N/A", height=50)
            data['inland_export_inst'] = st.text_area("(10) Onward Inland Routing/Export Instructions:", "Handle with care.", height=50)


    with st.expander("📦 تفاصيل البضائع والرسوم"):
        col3, col4 = st.columns([2, 1])
        with col3:
            data['container_no'] = st.text_area("(18) Container No. And Seal No. / Marks & Nos.", "MSKU1234567 / 998877", height=50)
            data['quantity'] = st.text_area("(19) Quantity and Kind of Packages", "20 Pallets", height=50)
            data['description'] = st.text_area("(20) Description of Goods", "Assorted Consumer Electronics and Spare Parts", height=100)
            data['total_packages'] = st.text_area("(22) TOTAL NUMBER OF CONTAINERS OR PACKAGES (IN WORDS)", "Twenty (20) Pallets", height=50)
        with col4:
            data['weight'] = st.text_input("Gross Weight (KGS):", "15,500")
            data['rev_tons'] = st.text_input("Revenue Tons:", "10.00")
            data['rate'] = st.text_input("Rate:", "150.00")
            data['per_prepaid'] = st.text_input("Per Prepaid:", "1500.00")
            data['collect'] = st.text_input("Collect:", "0.00")
            data['freight_charges'] = st.text_input("(24) FREIGHT & CHARGES:", "Prepaid")

    with st.expander("✍️ تفاصيل التوثيق النهائي"):
        col5, col6, col7 = st.columns(3)
        with col5:
            data['final_bl_no'] = st.text_input("(25) B/L NO.", "MCL-123456")
            data['service_type'] = st.text_input("(26) Service Type/Mode", "CY/CY")
        with col6:
            data['original_bl_no'] = st.text_input("(27) Number of Original B(s)/L", "3")
            data['issue_place_date'] = st.text_input("(28) Place of B(s)/L Issue/Date", "Dubai, 01/01/2025")
            data['laden_on_board'] = st.text_input("(33) Laden on Board", "02/01/2025")
        with col7:
            data['prepaid_at'] = st.text_input("(29) Prepaid at", "New York")
            data['collect_at'] = st.text_input("(30) Collect at", "Riyadh")
            data['exchange_rate'] = st.text_input("(31) Exchange Rate", "1.000")
            data['exchange_rate_2'] = st.text_input("(32) Exchange Rate", "3.750")

    st.markdown("---")

    pdf_buffer = create_pdf(data)
    
    st.download_button(
        label="⬇️ تحميل سند الشحن كملف PDF",
        data=pdf_buffer,
        file_name="Bill_of_Lading_Matched.pdf",
        mime="application/pdf",
        type="primary"
    )

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        st.error(f"حدث خطأ غير متوقع: {e}")
