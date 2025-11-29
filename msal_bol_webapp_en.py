import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import os 
from PIL import Image as PilImage 

# تعريف الألوان
DARK_GREEN = colors.Color(0/255, 128/255, 0/255) 
DARK_GREEN_HEX = '#008000' 

# مسار الشعار (تأكد من وجود هذا الملف في نفس المجلد)
LOGO_PATH = "msal_logo.png" 

# 1. دالة إنشاء محتوى PDF
def create_pdf(data):
    """
    تنشئ محتوى سند الشحن كملف PDF، مع التركيز الدقيق على تقسيم الحقول ودعم الصفوف الديناميكية للبضائع.
    """
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        # الهوامش الخارجية للصفحة (لا يوجد كينار خارجي)
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
        textColor=colors.black 
    )
    
    # نمط النص الفرعي (البيانات)
    cell_style = styles['Normal']
    cell_style.fontSize = 8
    cell_style.leading = 10 
    
    # نمط النص الرئيسي للحقول (الأرقام والعناوين) - أخضر داكن وخط عريض
    field_label_style = ParagraphStyle(
        'FieldLabel',
        parent=cell_style,
        fontName='Helvetica-Bold',
        textColor=DARK_GREEN,
        alignment=0 
    )

    elements = []
    
    # --- إضافة الشعار وعنوان "BILL OF LADING" ---
    logo_cell = None 
    
    if os.path.exists(LOGO_PATH):
        try:
            logo_cell = Image(LOGO_PATH, width=1.0 * inch, height=0.5 * inch)
            logo_cell.hAlign = 'LEFT' 
        except Exception:
            logo_cell = Paragraph(f"<font color=\"{DARK_GREEN_HEX}\">MCL SHIPPING</font>", field_label_style)
    else:
        logo_cell = Paragraph(f"<font color=\"{DARK_GREEN_HEX}\">MCL SHIPPING</font>", field_label_style)

    title_cell = Paragraph("BILL OF LADING", main_title_style)

    header_table = Table(
        [[logo_cell, title_cell]], 
        [1.5 * inch, 6.5 * inch] 
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'), 
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('LEFTPADDING', (1, 0), (1, 0), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0), 
        ('TOPPADDING', (0,0), (-1,-1), 0), 
        ('ROWHEIGHTS', (0,0), (0,0), 0.7*inch) 
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.1 * inch))
    
    # دالة مساعدة لتنسيق الخلايا ذات الرقم والعنوان الأخضر (Primary/Secondary text)
    def format_numbered_cell(number_text, label_text, data_value):
        label_paragraph = Paragraph(f'<font color="{DARK_GREEN_HEX}"><b>{number_text}</b> {label_text}</font>', field_label_style)
        data_paragraph = Paragraph(str(data_value), cell_style)
        
        # نستخدم جدولاً داخليًا للمحاذاة العمودية الدقيقة
        inner_table = Table([[label_paragraph], [data_paragraph]], colWidths=[None], rowHeights=[0.2*inch, None])
        inner_table.setStyle(TableStyle([
            ('LEFTPADDING', (0,0), (-1,-1), 2), 
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        return inner_table

    # دالة لتنسيق رؤوس الجداول (نص أخضر في المنتصف)
    def format_main_header_cell(text):
        p = Paragraph(f'<font color="{DARK_GREEN_HEX}"><b>{text}</b></font>', ParagraphStyle(
            'TableHeader',
            parent=field_label_style,
            alignment=1, 
            fontSize=8,
            leading=10 
        ))
        return p

    # --- جداول المعلومات الرئيسية (الصف العلوي) ---
    
    info_data_upper = [
        [
            format_numbered_cell("2)", "Shipper / Exporter:", data.get('shipper', 'N/A')),
            format_numbered_cell("5)", "Document No.:", data.get('doc_no', 'N/A')),
        ],
        [
            format_numbered_cell("3)", "Consignee (complete name and address):", data.get('consignee', 'N/A')),
            format_numbered_cell("7)", "Forwarding Agent / References:", data.get('fwd_agent', 'N/A')),
        ],
        [
            format_numbered_cell("4)", "Notify Party (complete name and address):", data.get('notify_party', 'N/A')), 
            format_numbered_cell("8)", "Point and Country of Origin (for the Merchant's reference only):", data.get('origin', 'N/A')),
        ],
        [
             format_main_header_cell("(12) Imo Vessel No."), 
             format_main_header_cell("(9) Also Notify Party (complete name and address)")
        ],
        [
            format_numbered_cell("13)", "Place of Receipt/Date:", data.get('imo_place', 'N/A')), 
            format_numbered_cell("9)", "Also Notify Party:", data.get('also_notify_party', 'N/A')),
        ],
        [
            format_numbered_cell("14)", "Ocean Vessel / Voy. No. / (15) Port of Loading", data.get('vessel_voyage_loading', 'N/A')),
            format_numbered_cell("10)", "Onward Inland Routing/Export Instructions:", data.get('inland_export_inst', 'N/A')),
        ],
        [
            format_numbered_cell("16)", "Port of Discharge / (17) Place of Delivery", data.get('discharge_delivery', 'N/A')),
            Paragraph("", cell_style) 
        ],
    ]
    
    upper_col_widths = [4.0 * inch, 4.0 * inch]
    t_upper = Table(info_data_upper, upper_col_widths, repeatRows=0)
    
    t_upper.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, DARK_GREEN), 
        ('ROWHEIGHTS', (0, 0), (2, 2), 0.7 * inch), 
        ('ROWHEIGHTS', (3, 3), (3, 3), 0.25 * inch), 
        ('ROWHEIGHTS', (4, 4), (-1, -1), 0.7 * inch), 
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))

    elements.append(t_upper)
    elements.append(Spacer(1, 0.1 * inch))

    # --- جدول البضائع (الجزء الأوسط) ---
    
    goods_col_widths = [2.0 * inch, 1.5 * inch, 3.5 * inch, 1.0 * inch] 
    
    goods_header = [
        [
            format_main_header_cell("(18) Container No. And Seal No. / Marks & Nos."),
            format_main_header_cell("(19) Quantity and Kind of Packages"),
            format_main_header_cell("Particulars furnished by the Merchant"),
            Paragraph("", cell_style) 
        ],
        [
            Paragraph("CONTAINER NO./SEAL NO.", cell_style), 
            Paragraph("Marks & Nos.", cell_style),          
            Paragraph("(20) Description of Goods", cell_style), 
            Paragraph("(21) Measurement (M³)<br/>Gross Weight (KGS)", cell_style) 
        ]
    ]
    
    # إنشاء صفوف بيانات البضائع ديناميكيًا
    goods_data_rows = []
    num_rows = len(data.get('goods_list', []))
    
    # تحديد ارتفاع الصف الواحد ديناميكياً بناءً على عدد الصفوف للحفاظ على مساحة ثابتة
    single_row_height = (2.5 * inch) / max(1, num_rows)
    if single_row_height < 0.5 * inch:
        single_row_height = 0.5 * inch 

    if data.get('goods_list'):
        for item in data['goods_list']:
            goods_data_rows.append([
                Paragraph(item['container_no'], cell_style), 
                Paragraph(item['quantity'], cell_style), 
                Paragraph(item['description'], cell_style), 
                Paragraph(item['weight_measurement'], cell_style) 
            ])
    
    t_goods = Table(goods_header + goods_data_rows, goods_col_widths, repeatRows=2) 

    # تطبيق ارتفاع الصفوف الديناميكي
    style_commands = [
        ('GRID', (0, 0), (-1, -1), 1, DARK_GREEN),
        ('SPAN', (2, 0), (3, 0)), 
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWHEIGHTS', (0, 0), (0, 0), 0.3 * inch), 
        ('ROWHEIGHTS', (1, 1), (1, 1), 0.5 * inch), 
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]

    # تطبيق ارتفاع موحد على جميع صفوف البيانات (بدءاً من الصف 2)
    for row_index in range(num_rows):
        style_commands.append(('ROWHEIGHTS', (row_index + 2, row_index + 2), (row_index + 2, row_index + 2), single_row_height))

    t_goods.setStyle(TableStyle(style_commands))

    elements.append(t_goods)
    elements.append(Spacer(1, 0.1 * inch))
    
    # --- جدول الشحن والرسوم (الجزء السفلي) ---
    
    footer_data = [
        [
            format_numbered_cell("22)", "TOTAL NUMBER OF CONTAINERS OR PACKAGES (IN WORDS)", data.get('total_packages', 'N/A')),
            format_main_header_cell("Revenue Tons"),
            format_main_header_cell("Rate"),
            format_main_header_cell("Per Prepaid"),
            format_main_header_cell("Collect")
        ],
        [
            format_numbered_cell("24)", "FREIGHT & CHARGES", data.get('freight_charges', 'N/A')),
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
        ('ROWHEIGHTS', (0, 0), (0, 0), 0.4 * inch), 
        ('ROWHEIGHTS', (1, 1), (-1, -1), 0.7 * inch), 
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    
    elements.append(t_footer)
    elements.append(Spacer(1, 0.1 * inch))
    
    # --- الجدول النهائي (التوقيع والتواريخ) ---
    
    final_data = [
        [
            format_numbered_cell("25)", "B/L NO.", data.get('final_bl_no', 'N/A')),
            format_numbered_cell("27)", "Number of Original B(s)/L", data.get('original_bl_no', 'N/A')),
            format_numbered_cell("29)", "Prepaid at", data.get('prepaid_at', 'N/A')),
            format_numbered_cell("30)", "Collect at", data.get('collect_at', 'N/A')),
        ],
        [
            format_numbered_cell("26)", "Service Type/Mode", data.get('service_type', 'N/A')),
            format_numbered_cell("28)", "Place of B(s)/L Issue/Date", data.get('issue_place_date', 'N/A')),
            format_numbered_cell("31)", "Exchange Rate", data.get('exchange_rate', 'N/A')),
            format_numbered_cell("32)", "Exchange Rate", data.get('exchange_rate_2', 'N/A')),
        ],
        [
             format_numbered_cell("33)", "Laden on Board", data.get('laden_on_board', 'N/A')),
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
        ('ROWHEIGHTS', (0, 0), (-1, -1), 0.7 * inch),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    
    elements.append(t_final)

    doc.build(elements)
    
    buffer.seek(0)
    return buffer

# 2. دالة واجهة Streamlit (main)
def main():
    st.set_page_config(layout="wide", page_title="أداة سند الشحن")
    
    st.title("🚢 أداة إنشاء سند الشحن (النسخة النهائية)")
    
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=100) 
    else:
        st.markdown(f"**<font color='{DARK_GREEN_HEX}'>MCL SHIPPING</font>**", unsafe_allow_html=True)

    st.markdown("---")
    
    data = {}
    
    with st.expander("بيانات الشاحن والمستلم والموانئ"):
        col1, col2 = st.columns(2)
        with col1:
            data['shipper'] = st.text_area("2) Shipper / Exporter:", "M.L. General Trading LLC, Dubai", height=50)
            data['consignee'] = st.text_area("3) Consignee:", "Ahmad Logistics, Jeddah", height=50)
            data['notify_party'] = st.text_area("4) Notify Party:", "Same as Consignee", height=50)
            data['imo_place'] = st.text_input("13) Place of Receipt/Date:", "London, 01/01/2025")
            data['vessel_voyage_loading'] = st.text_input("14) Ocean Vessel / Voy. No. / (15) Port of Loading:", "Maersk-001 / Jebel Ali, UAE")
            data['discharge_delivery'] = st.text_input("16) Port of Discharge / (17) Place of Delivery:", "King Abdullah Port, KSA / Riyadh")

        with col2:
            data['doc_no'] = st.text_input("5) Document No.:", "MCL-BL-123456")
            data['fwd_agent'] = st.text_input("7) Forwarding Agent / References:", "Fast Global Movers")
            data['origin'] = st.text_input("8) Point and Country of Origin:", "Hamburg, Germany")
            data['also_notify_party'] = st.text_area("9) Also Notify Party:", "N/A", height=50)
            data['inland_export_inst'] = st.text_area("10) Onward Inland Routing/Export Instructions:", "Handle with care.", height=50)


    with st.expander("📦 تفاصيل البضائع والرسوم (صفوف ديناميكية)"):
        
        # التحكم في عدد صفوف البضائع
        num_goods_rows = st.number_input(
            "عدد صفوف تفاصيل البضائع المطلوبة (حاويات/بضائع)", 
            min_value=1, 
            value=1, 
            step=1,
            key='num_goods_rows'
        )
        
        data['goods_list'] = [] 
        
        # إنشاء حقول إدخال ديناميكية لكل صف
        for i in range(int(num_goods_rows)):
            st.subheader(f"بيانات الصف / الحاوية رقم {i+1}")
            
            # عمود (18) و (19)
            col_18, col_19 = st.columns([1, 1])
            cont_marks = col_18.text_area(f"18) Cont. No. / Marks (Row {i+1})", f"MSKU1234567 / 998877 ({i+1})", height=50, key=f'cont_{i}')
            quantity = col_19.text_area(f"19) Quantity (Row {i+1})", f"20 Pallets ({i+1})", height=50, key=f'qty_{i}')

            # عمود (20) و (21)
            col_20, col_21 = st.columns([3, 1])
            description = col_20.text_area(f"20) Description of Goods (Row {i+1})", "Assorted Consumer Electronics and Spare Parts", height=70, key=f'desc_{i}')
            weight_measurement = col_21.text_input(f"21) Weight / Meas. (Row {i+1})", f"15,500 KGS / 10 M³ ({i+1})", key=f'wgt_{i}')

            goods_entry = {
                'container_no': cont_marks,
                'quantity': quantity,
                'description': description,
                'weight_measurement': weight_measurement
            }
            data['goods_list'].append(goods_entry)
            st.markdown("---") 


        data['total_packages'] = st.text_area("22) TOTAL NUMBER OF CONTAINERS OR PACKAGES (IN WORDS)", "Twenty (20) Pallets", height=50)
        
        col4_f, col5_f, col6_f, col7_f, col8_f = st.columns(5)
        data['rev_tons'] = col4_f.text_input("Revenue Tons:", "10.00")
        data['rate'] = col5_f.text_input("Rate:", "150.00")
        data['per_prepaid'] = col6_f.text_input("Per Prepaid:", "1500.00")
        data['collect'] = col7_f.text_input("Collect:", "0.00")
        data['freight_charges'] = col8_f.text_input("24) FREIGHT & CHARGES:", "Prepaid")

    with st.expander("✍️ تفاصيل التوثيق النهائي"):
        col5, col6, col7 = st.columns(3)
        with col5:
            data['final_bl_no'] = st.text_input("25) B/L NO.", "MCL-123456")
            data['service_type'] = st.text_input("26) Service Type/Mode", "CY/CY")
        with col6:
            data['original_bl_no'] = st.text_input("27) Number of Original B(s)/L", "3")
            data['issue_place_date'] = st.text_input("28) Place of B(s)/L Issue/Date", "Dubai, 01/01/2025")
            data['laden_on_board'] = st.text_input("33) Laden on Board", "02/01/2025")
        with col7:
            data['prepaid_at'] = st.text_input("29) Prepaid at", "New York")
            data['collect_at'] = st.text_input("30) Collect at", "Riyadh")
            data['exchange_rate'] = st.text_input("31) Exchange Rate", "1.000")
            data['exchange_rate_2'] = st.text_input("32) Exchange Rate", "3.750")

    st.markdown("---")

    pdf_buffer = create_pdf(data)
    
    st.download_button(
        label="⬇️ تحميل سند الشحن كملف PDF",
        data=pdf_buffer,
        file_name="Bill_of_Lading_Final_Template.pdf",
        mime="application/pdf",
        type="primary"
    )

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        st.error(f"حدث خطأ غير متوقع: {e}")
