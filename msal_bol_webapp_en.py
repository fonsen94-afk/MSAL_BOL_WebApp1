# 1. دالة إنشاء محتوى PDF
def create_pdf(data):
    """
    تنشئ محتوى سند الشحن كملف PDF في الذاكرة باستخدام ReportLab.
    (تم تطبيق الحل النهائي لخطأ TypeError في جدول الرأس)
    """
    buffer = io.BytesIO()
    
    # إعداد قالب المستند
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )
    
    styles = getSampleStyleSheet()
    
    # تصميم الأنماط
    main_title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['h1'],
        fontSize=18,
        alignment=1, # مركز
        spaceAfter=5
    )
    
    # نمط الخطوط الصغيرة داخل الخلايا
    cell_style = styles['Normal']
    cell_style.fontSize = 8
    cell_style.leading = 11
    
    elements = []
    
    # --- إضافة الشعار والعنوان ---
    
    # القيمة الافتراضية للخلية الأولى - يجب أن تكون فارغة في البداية
    logo_cell = None 
    
    # 1. إعداد خلية الشعار
    if os.path.exists(LOGO_PATH):
        try:
            # ReportLab Image - محاولة إنشاء الكائن
            logo_cell = Image(str(LOGO_PATH), width=1.0 * inch, height=0.5 * inch)
        except Exception:
             # في حالة حدوث خطأ في القراءة، نستخدم نص بسيط (String) كإجراء احتياطي
            logo_cell = "[LOGO ERROR]"
    else:
        # إذا لم يتم العثور على الملف، نستخدم نص بسيط (String) كإجراء احتياطي
        logo_cell = "MCL SHIPPING"
    
    # 🚨 إذا كانت الخلية نصاً بسيطاً، نقوم بتحويلها إلى Paragraph قبل الجدول
    # (لكن هنا سنعتمد على أن ReportLab تقبل النص في هذه الحالة)
    if isinstance(logo_cell, str):
        logo_cell = Paragraph(f"<b>{logo_cell}</b>", styles['Normal'])

    # 2. إعداد خلية العنوان
    title_cell = Paragraph("BILL OF LADING", main_title_style)

    # دمج الشعار والعنوان في جدول برأس الصفحة (السطر 65 سابقاً)
    header_table = Table(
        [[logo_cell, title_cell]], 
        col_widths=[1.5 * inch, 6.5 * inch]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('LEFTPADDING', (1, 0), (1, 0), 0)
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.2 * inch))
    
    # --- البيانات الأساسية في جدول واحد ---
    
    table_data = [
        [
            Paragraph("<b>(2) Shipper / Exporter:</b><br/>" + str(data.get('shipper', 'N/A')), cell_style),
            Paragraph("<b>(5) Document No.:</b><br/>" + str(data.get('doc_no', 'N/A')), cell_style),
        ],
        [
            Paragraph("<b>(3) Consignee:</b><br/>" + str(data.get('consignee', 'N/A')), cell_style),
            Paragraph("<b>(6) Export References:</b><br/>" + str(data.get('export_ref', 'N/A')), cell_style),
        ],
        [
            Paragraph("<b>(4) Notify Party:</b><br/>" + str(data.get('notify_party', 'N/A')), cell_style),
            Paragraph("<b>(7) Forwarding Agent / References:</b><br/>" + str(data.get('fwd_agent', 'N/A')), cell_style),
        ],
        [
            Paragraph("<b>(14) Port of Loading:</b><br/>" + str(data.get('port_loading', 'N/A')), cell_style),
            Paragraph("<b>(15) Port of Discharge:</b><br/>" + str(data.get('port_discharge', 'N/A')), cell_style),
        ],
    ]
    
    col_widths = [4.0 * inch, 4.0 * inch]
    t_info = Table(table_data, col_widths=col_widths, repeatRows=0)
    
    t_info.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWHEIGHTS', (0, 0), (0, 0), 0.7 * inch),
        ('ROWHEIGHTS', (1, 1), (1, 1), 0.7 * inch),
        ('ROWHEIGHTS', (2, 2), (2, 2), 1.0 * inch),
        ('ROWHEIGHTS', (3, 3), (3, 3), 0.7 * inch),
    ]))

    elements.append(t_info)
    
    # --- قسم البضائع (الجدول الرئيسي) ---
    
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("<b>Particulars furnished by the Merchant</b>", styles['h3']))
    
    # رؤوس الأعمدة
    goods_header = [
        [
            Paragraph("<b>(18) Container No. And Seal No.</b>", cell_style), 
            Paragraph("<b>(19) Quantity and Kind of Packages</b>", cell_style), 
            Paragraph("<b>(20) Description of Goods</b>", cell_style), 
            Paragraph("<b>(21) Gross Weight (KGS)</b>", cell_style)
        ],
    ]
    
    # بيانات البضائع
    goods_data = [
        [
            str(data.get('container_no', 'N/A')), 
            str(data.get('quantity', 'N/A')), 
            Paragraph(str(data.get('description', 'N/A')), cell_style), 
            str(data.get('weight', 'N/A'))
        ]
    ]
    
    table_goods_full = goods_header + goods_data
    
    # عرض الأعمدة لجدول البضائع
    goods_col_widths = [1.5 * inch, 1.5 * inch, 3.5 * inch, 1.4 * inch]
    t_goods = Table(table_goods_full, col_widths=goods_col_widths, repeatRows=1)
    
    t_goods.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ROWHEIGHTS', (1, 1), (-1, -1), 2.0 * inch)
    ]))

    elements.append(t_goods)

    # --- بناء المستند والحفظ ---
    doc.build(elements)
    
    # إعادة تعيين مؤشر المخزن المؤقت إلى البداية
    buffer.seek(0)
    return buffer
