import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io

# 1. دالة إنشاء محتوى PDF
def create_pdf(data):
    # إنشاء مخزن مؤقت (Buffer) في الذاكرة لتخزين ملف PDF
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
    # تصميم مخصص للعنوان الرئيسي
    main_title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['h1'],
        fontSize=18,
        alignment=1, # مركز
        spaceAfter=15
    )
    
    # قائمة العناصر التي سيتم إضافتها إلى المستند
    elements = []

    # --- العنوان ---
    elements.append(Paragraph("BILL OF LADING", main_title_style))
    elements.append(Paragraph(f"<b>MCL SHIPPING</b>", styles['Normal']))
    elements.append(Spacer(1, 0.2 * inch))

    # --- بيانات سند الشحن في شكل جدول ---
    
    # 📝 ملاحظة: سنستخدم جدول ReportLab لتقليد تخطيط الصناديق/الخلايا.
    
    # الصف الأول: Shipper, Document No., Export References
    data_table_1 = [
        [
            Paragraph("<b>(2) Shipper / Exporter:</b><br/>" + data.get('shipper', ''), styles['Normal']),
            Paragraph("<b>(5) Document No.:</b><br/>" + data.get('doc_no', ''), styles['Normal']),
            Paragraph("<b>(6) Export References:</b><br/>" + data.get('export_ref', ''), styles['Normal'])
        ],
        # الصف الثاني: Consignee, Forwarding Agent
        [
            Paragraph("<b>(3) Consignee:</b><br/>" + data.get('consignee', ''), styles['Normal']),
            Paragraph("<b>(7) Forwarding Agent / References:</b><br/>" + data.get('fwd_agent', ''), styles['Normal']),
            ''
        ],
        # الصف الثالث: Ports
        [
            Paragraph("<b>(14) Port of Loading:</b><br/>" + data.get('port_loading', ''), styles['Normal']),
            Paragraph("<b>(15) Port of Discharge:</b><br/>" + data.get('port_discharge', ''), styles['Normal']),
            ''
        ]
    ]

    # عرض الأعمدة: (عرض للعمود الأول، عرض للعمود الثاني، عرض للعمود الثالث)
    col_widths = [3 * inch, 2.2 * inch, 2.2 * inch]
    t1 = Table(data_table_1, col_widths=col_widths)
    
    # تنسيق الجدول (إضافة الحدود والمحاذاة)
    t1.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('SPAN', (2, 1), (2, 2)), # دمج الخلايا الفارغة
    ]))
    
    elements.append(t1)
    elements.append(Spacer(1, 0.2 * inch))
    
    # --- قسم البضائع (الجدول الرئيسي) ---
    
    elements.append(Paragraph("<b>Particulars furnished by the Merchant</b>", styles['h3']))
    
    # البيانات الافتراضية للبضائع (يفترض أن المستخدم قام بإدخالها)
    goods_data = [
        ["(18) Container No. And Seal No.", "(19) Quantity", "(20) Description of Goods", "(21) Gross Weight (KGS)"],
        [data.get('container_no', 'N/A'), data.get('quantity', '10'), data.get('description', 'Electronics'), data.get('weight', '500')]
    ]
    
    # عرض الأعمدة لجدول البضائع
    goods_col_widths = [1.5 * inch, 1.0 * inch, 3.5 * inch, 1.4 * inch]
    t_goods = Table(goods_data, col_widths=goods_col_widths, repeatRows=1)
    
    t_goods.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey), # تلوين رأس الجدول
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ROWHEIGHTS', (1, 1), (-1, -1), 1.5 * inch) # زيادة ارتفاع صفوف البيانات
    ]))

    elements.append(t_goods)

    # بناء المستند
    doc.build(elements)
    
    # إعادة تعيين مؤشر المخزن المؤقت إلى البداية
    buffer.seek(0)
    return buffer

### 2. دالة واجهة Streamlit

```python
def main():
    st.set_page_config(layout="wide")
    st.title("🚢 إنشاء سند شحن تفاعلي (Bill of Lading)")
    
    st.markdown("""
        هذا التطبيق يقوم بإنشاء ملف PDF لسند الشحن بناءً على البيانات التي تُدخلها، باستخدام مكتبة ReportLab.
    """)
    
    # --- نموذج الإدخال (Streamlit UI) ---
    
    with st.expander("📝 إدخال بيانات الشحنة", expanded=True):
        col1, col2 = st.columns(2)
        
        # العمود الأول: المرسل والمتلقي
        with col1:
            st.subheader("بيانات الأطراف")
            shipper = st.text_area("(2) Shipper / Exporter", "M.L. General Trading LLC, Dubai")
            consignee = st.text_area("(3) Consignee", "Ahmad Logistics, Jeddah")
            fwd_agent = st.text_input("(7) Forwarding Agent", "Fast Global Movers")

        # العمود الثاني: المراجع والأرقام
        with col2:
            st.subheader("بيانات المراجع")
            doc_no = st.text_input("(5) Document No.", "MCL-BL-123456")
            export_ref = st.text_input("(6) Export References", "EXP/123/2025")
            
            st.subheader("بيانات الموانئ")
            port_loading = st.text_input("(14) Port of Loading", "Jebel Ali, UAE")
            port_discharge = st.text_input("(15) Port of Discharge", "King Abdullah Port, KSA")

    # --- بيانات البضائع ---
    st.subheader("📦 تفاصيل البضائع")
    col3, col4, col5 = st.columns(3)
    with col3:
        container_no = st.text_input("(18) Container No. / Seal No.", "MSKU1234567 / 998877")
    with col4:
        quantity = st.text_input("(19) Quantity (Packages)", "20 Pallets")
    with col5:
        weight = st.text_input("(21) Gross Weight (KGS)", "15,500")
        
    description = st.text_area("(20) Description of Goods", "Assorted Consumer Electronics and Spare Parts")

    # تجميع البيانات في قاموس
    form_data = {
        'shipper': shipper,
        'consignee': consignee,
        'fwd_agent': fwd_agent,
        'doc_no': doc_no,
        'export_ref': export_ref,
        'port_loading': port_loading,
        'port_discharge': port_discharge,
        'container_no': container_no,
        'quantity': quantity,
        'weight': weight,
        'description': description
    }
    
    st.markdown("---")

    # --- زر التحميل ---
    
    # إنشاء PDF عند الضغط على زر التحميل
    pdf_buffer = create_pdf(form_data)
    
    st.download_button(
        label="⬇️ تحميل سند الشحن كملف PDF",
        data=pdf_buffer,
        file_name="Bill_of_Lading.pdf",
        mime="application/pdf"
    )

if __name__ == '__main__':
    main()
