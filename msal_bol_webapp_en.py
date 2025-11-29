import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import os 
from PIL import Image as PilImage 

# تعريف اللون الأخضر الداكن فقط للخطوط
DARK_GREEN = colors.Color(0/255, 128/255, 0/255) 
DARK_GREEN_HEX = '#008000' 

# مسار الشعار
LOGO_PATH = "msal_logo.png" 

# 1. دالة إنشاء محتوى PDF
def create_pdf(data):
    """
    تنشئ محتوى سند الشحن كملف PDF في الذاكرة، بدون خلفيات خضراء، مع لوجو واضح.
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
    
    cell_style = styles['Normal']
    cell_style.fontSize = 8
    cell_style.leading = 11
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=cell_style,
        fontName='Helvetica-Bold',
        textColor=DARK_GREEN
    )

    elements = []
    
    # --- إضافة الشعار والعنوان "BILL OF LADING" ---
    logo_cell = None 
    
    if os.path.exists(LOGO_PATH):
        try:
            pil_img = PilImage.open(LOGO_PATH)
            # تم تقليل عملية تغيير الحجم هنا لتجنب فقدان الجودة إلا إذا كان ضروريًا
            # يمكنك تعديل width و height هنا إذا كان الشعار كبيرًا جدًا
            logo_cell = Image(LOGO_PATH, width=1.0 * inch, height=0.5 * inch)
            logo_cell.hAlign = 'LEFT' # محاذاة اللوجو لليسار
        except Exception as e:
            # في حال وجود مشكلة في اللوجو، يتم عرض اسم الشركة كنص أخضر
            logo_cell = Paragraph(f"<font color=\"{DARK_GREEN_HEX}\"><b>MCL SHIPPING</b></font>", header_style)
            print(f"Error loading logo: {e}") # لغرض التصحيح
    else:
        logo_cell = Paragraph(f"<font color=\"{DARK_GREEN_HEX}\"><b>MCL SHIPPING</b></font>", header_style)

    title_cell = Paragraph("BILL OF LADING", main_title_style)

    header_table = Table(
        [[logo_cell, title_cell]], 
        [1.5 * inch, 6.5 * inch] # عرض الأعمدة للوجو والعنوان
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('LEFTPADDING', (1, 0), (1, 0), 0),
        # 🚨 إزالة أي خلفية من هنا
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.1 * inch))
    
    # دالة مساعدة لتنسيق البيانات في الخلايا 
    def format_cell(title, key, height=0.7 * inch, is_header_only=False):
        content = str(data.get(key, 'N/A'))
        
        if is_header_only: # إذا كانت الخلية تحتوي على عنوان أخضر فقط
            return Paragraph(f'<font color="{DARK_GREEN_HEX}"><b>({title})</b></font>', cell_style)
        else: # إذا كانت الخلية تحتوي على عنوان أخضر وبيانات سوداء
            title_html = f'<font color="{DARK_GREEN_HEX}"><b>({title})</b></font>'
            return Paragraph(f"{title_html}<br/>{content}", cell_style)

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
             # هذه الخلايا كانت رؤوس في السابق، الآن نجعل النص أخضر بالكامل
             format_cell("12) Imo Vessel No.", 'imo_vessel_header', is_header_only=True),
             format_cell("9) Also Notify Party (complete name and address)", 'also_notify_header', is_header_only=True)
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
        ('GRID', (0, 0), (-1, -1), 1, DARK_GREEN), # حدود خضراء داكنة
        ('ROWHEIGHTS', (0, 0), (1, -1), 0.7 * inch),
        ('ROWHEIGHTS', (2, 2), (2, 2), 0.8 * inch),
        ('ROWHEIGHTS', (3, 3), (3, 3), 0.3 * inch), # رؤوس قصيرة
        ('ROWHEIGHTS', (4, 4), (-1, -1), 0.7 * inch),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        # 🚨 إزالة الخلفية الخضراء الفاتحة من هنا
        # ('BACKGROUND', (0, 3), (-1, 3), LIGHT_GREEN_BG), 
    ]))

    elements.append(t_upper)
    elements.append(Spacer(1, 0.1 * inch))

    # --- جدول البضائع (الجزء الأوسط) ---
    
    goods_header = [
        [
            format_cell("18) Container No. And Seal No.<br/>Marks & Nos.", 'container_marks_header', is_header_only=True), 
            format_cell("19) Quantity and Kind of Packages", 'quantity_kind_header', is_header_only=True), 
            format_cell("Particulars furnished by the Merchant", 'particulars_merchant_header', is_header_only=True),
            format_cell("21) Measurement (M³)<br/>Gross Weight (KGS)", 'measurement_weight_header', is_header_only=True)
        ],
        [
            Paragraph("CONTAINER NO./SEAL NO.", cell_style), # بيانات فرعية بالأسود
            Paragraph("Marks & Nos.", cell_style),          # بيانات فرعية بالأسود
            Paragraph("(20) Description of Goods", cell_style), # بيانات فرعية بالأسود
            Paragraph("", cell_style) 
        ]
    ]
    
    goods_col_widths = [2.0 * inch, 1.5 * inch, 3.5 * inch, 1.0 * inch] 
    t_goods = Table(goods_header + [
        [
            str(data.get('container_no', 'N/A')), 
            str(data.get('quantity', 'N/A')), 
            Paragraph(str(data.get('description', 'N/A')), cell_style), 
            str(data.get('weight', 'N/A'))
        ]
    ], goods_col_widths, repeatRows=2)
    
    t_goods.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, DARK_GREEN),
        ('SPAN', (2, 0), (3, 0)), # دمج خلية "Particulars furnished by the Merchant"
        
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        # 🚨 إزالة الخلفية الخضراء الفاتحة من هنا
        # ('BACKGROUND', (0, 0), (-1, 1), LIGHT_GREEN_BG), 
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
            # هذه الأعمدة هي عناوين رئيسية
            format_cell("Revenue Tons", 'rev_tons_header', is_header_only=True),
            format_cell("Rate", 'rate_header', is_header_only=True),
            format_cell("Per Prepaid", 'per_prepaid_header', is_header_only=True),
            format_cell("Collect", 'collect_header', is_header_only=True)
        ],
        [
            format_cell("24) FREIGHT & CHARGES", 'freight_charges'),
            # هذه بيانات بالأسود
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
        #
