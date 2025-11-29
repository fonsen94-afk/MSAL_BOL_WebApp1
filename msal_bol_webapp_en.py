# ... (استيراد المكتبات كما هي)

# 1. دالة إنشاء محتوى PDF
def create_pdf(data):
    """
    تنشئ محتوى سند الشحن كملف PDF في الذاكرة باستخدام ReportLab.
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
        spaceAfter=15
    )
    
    # نمط الخطوط الصغيرة داخل الخلايا
    cell_style = styles['Normal']
    cell_style.fontSize = 8
    cell_style.leading = 11
    
    elements = []

    # --- العنوان والشعار ---
    elements.append(Paragraph("BILL OF LADING", main_title_style))
    elements.append(Paragraph(f"<b>MCL SHIPPING</b>", styles['Normal']))
    elements.append(Spacer(1, 0.2 * inch))

    # --- البيانات الأساسية في جدول واحد ---
    
    # 🚨 تم التأكد من استخدام str() حول كل قيمة لتجنب TypeError
    table_data = [
        [
            Paragraph("<b>(2) Shipper / Exporter:</b><br/>" + str(data['shipper']), cell_style),
            Paragraph("<b>(5) Document No.:</b><br/>" + str(data['doc_no']), cell_style),
        ],
        [
            Paragraph("<b>(3) Consignee:</b><br/>" + str(data['consignee']), cell_style),
            Paragraph("<b>(6) Export References:</b><br/>" + str(data['export_ref']), cell_style),
        ],
        [
            Paragraph("<b>(4) Notify Party:</b><br/>" + str(data['notify_party']), cell_style),
            Paragraph("<b>(7) Forwarding Agent / References:</b><br/>" + str(data['fwd_agent']), cell_style),
        ],
        [
            Paragraph("<b>(14) Port of Loading:</b><br/>" + str(data['port_loading']), cell_style),
            Paragraph("<b>(15) Port of Discharge:</b><br/>" + str(data['port_discharge']), cell_style),
        ],
    ]
    
    col_widths = [4.0 * inch, 4.0 * inch]
    # السطر 73 حيث حدث الخطأ
    t_info = Table(table_data, col_widths=col_widths, repeatRows=0)
    
    t_info.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWHEIGHTS', (0, 0), (-1, -1), 0.7 * inch),
        ('ROWHEIGHTS', (2, 2), (2, 2), 1.0 * inch), 
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
            str(data['container_no']), 
            str(data['quantity']), 
            Paragraph(str(data['description']), cell_style), 
            str(data['weight'])
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

# ... (دالة main() كما هي)

if __name__ == '__main__':
    main()
