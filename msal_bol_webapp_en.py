import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import pandas as pd # مكتبة Pandas مُضافة لبيئة Streamlit

# 1. دالة إنشاء محتوى PDF
def create_pdf(data):
    """
    تنشئ محتوى سند الشحن كملف PDF في الذاكرة باستخدام ReportLab.
    """
    # إنشاء مخزن مؤقت (Buffer) في الذاكرة
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

    # --- البيانات الأساسية في جدول واحد (لضمان التنسيق) ---
    
    table_data = [
        [
            Paragraph("<b>(2) Shipper / Exporter:</b><br/>" + data['shipper'], cell_style),
            Paragraph("<b>(5) Document No.:</b><br/>" + data['doc_no'], cell_style),
        ],
        [
            Paragraph("<b>(3) Consignee:</b><br/>" + data['consignee'], cell_style),
            Paragraph("<b>(6) Export References:</b><br/>" + data['export_ref'], cell_style),
        ],
        [
            Paragraph("<b>(4) Notify Party:</b><br/>" + data['notify_party'], cell_style),
            Paragraph("<b>(7) Forwarding Agent / References:</b><br/>" + data['fwd_agent'], cell_style),
        ],
        [
            Paragraph("<b>(14) Port of Loading:</b><br/>" + data['port_loading'], cell_style),
            Paragraph("<b>(15) Port of Discharge:</b><br/>" + data['port_discharge'], cell_style),
        ],
    ]
    
    col_widths = [4.0 * inch, 4.0 * inch]
    t_info = Table(table_data, col_widths=col_widths, repeatRows=0)
    
    t_info.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWHEIGHTS', (0, 0), (-1, -1), 0.7 * inch),
        ('ROWHEIGHTS', (2, 2), (2, 2), 1.0 * inch), # مساحة أكبر للإخطار
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
            data['container_no'], 
            data['quantity'], 
            Paragraph(data['description'], cell_style), # نستخدم Paragraph هنا للوصف الطويل
            data['weight']
        ]
    ]
    
    # دمج رؤوس الأعمدة والبيانات
    table_goods_full = goods_header + goods_data
    
    # عرض الأعمدة لجدول البضائع
    goods_col_widths = [1.5 * inch, 1.5 * inch, 3.5 * inch, 1.4 * inch]
    t_goods = Table(table_goods_full, col_widths=goods_col_widths, repeatRows=1)
    
    t_goods.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ROWHEIGHTS', (1, 1), (-1, -1), 2.0 * inch) # ارتفاع صف البيانات
    ]))

    elements.append(t_goods)

    # --- بناء المستند والحفظ ---
    doc.build(elements)
    
    # إعادة تعيين مؤشر المخزن المؤقت إلى البداية
    buffer.seek(0)
    return buffer

# 2. دالة واجهة Streamlit
def main():
    st.set_page_config(layout="wide")
    st.title("🚢 أداة إنشاء سند الشحن (Bill of Lading)")
    
    st.markdown("---")

    # --- نموذج الإدخال (Streamlit UI) ---
    
    with st.container(border=True):
        st.subheader("📝 بيانات الأطراف والمراجع")
        
        col1, col2 = st.columns(2)
        
        with col1:
            shipper = st.text_area("**(2) الشاحن / المصدر (Shipper / Exporter)**", "M.L. General Trading LLC, Dubai", height=70)
            consignee = st.text_area("**(3) المستلم (Consignee)**", "Ahmad Logistics, Jeddah", height=70)
            notify_party = st.text_area("**(4) طرف الإخطار (Notify Party)**", "Same as Consignee", height=70)


        with col2:
            doc_no = st.text_input("**(5) رقم المستند (Document No.)**", "MCL-BL-123456")
            export_ref = st.text_input("**(6) مرجع التصدير (Export References)**", "EXP/123/2025")
            fwd_agent = st.text_input("**(7) وكيل الشحن (Forwarding Agent)**", "Fast Global Movers")
            
            st.markdown("---")
            port_loading = st.text_input("**(14) ميناء الشحن (Port of Loading)**", "Jebel Ali, UAE")
            port_discharge = st.text_input("**(15) ميناء التفريغ (Port of Discharge)**", "King Abdullah Port, KSA")


    st.markdown("---")

    st.subheader("📦 تفاصيل البضائع")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        container_no = st.text_input("**(18) رقم الحاوية / الختم**", "MSKU1234567 / 998877")
    with col4:
        quantity = st.text_input("**(19) الكمية ونوع الطرود**", "20 Pallets")
    with col5:
        weight = st.text_input("**(21) الوزن الإجمالي (KGS)**", "15,500")
        
    description = st.text_area("**(20) وصف البضائع (Description of Goods)**", "Assorted Consumer Electronics and Spare Parts", height=100)

    # تجميع البيانات في قاموس
    form_data = {
        'shipper': shipper,
        'consignee': consignee,
        'notify_party': notify_party,
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
    
    # إنشاء PDF عند تفاعل المستخدم مع التطبيق
    pdf_buffer = create_pdf(form_data)
    
    st.download_button(
        label="⬇️ تحميل سند الشحن كملف PDF",
        data=pdf_buffer,
        file_name="Bill_of_Lading.pdf",
        mime="application/pdf",
        type="primary"
    )

if __name__ == '__main__':
    main()
