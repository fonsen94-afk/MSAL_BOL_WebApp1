# msal_bol_webapp_en_green.py
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import qrcode
import io
import os

# ----- Font and Styles -----
base_font = "Helvetica"
styles = getSampleStyleSheet()

green_color = colors.HexColor("#008000")  # اللون الأخضر للحقول
black_color = colors.black               # اللون الأسود للقيم

styles.add(ParagraphStyle(name='FieldLabelGreen', fontName=base_font, fontSize=10, leading=12, textColor=green_color))
styles.add(ParagraphStyle(name='FieldValueBlack', fontName=base_font, fontSize=10, leading=12, textColor=black_color))
styles.add(ParagraphStyle(name='Title', fontName=base_font, fontSize=18, leading=20, alignment=1, textColor=green_color))

st.title("MSAL Shipping - Bill of Lading Generator")

# ----- Logo -----
logo_path = "msal_logo.png"  # ضع شعارك هنا

# ----- Input Fields -----
fields = [
    "Shipper / Exporter","Consignee","Notify Party","Document No.","Export References",
    "Forwarding Agent","Point & Country of Origin","Also Notify Party","IMO Vessel No.",
    "Place of Receipt / Date","Ocean Vessel / Voyage No.","Port of Loading","Port of Discharge",
    "Place of Delivery","Container No. / Seal No.","Quantity & Kind of Packages","Description of Goods",
    "Measurement (M³) / Gross Weight (KGS)","Total Containers / Packages","Freight & Charges",
    "B/L No.","Service Type / Mode","Number of Original B(s)/L","Place of B(s)/L Issue / Date",
    "Prepaid at","Collect at","Exchange Rate","Laden on Board","Tracking URL"
]

data = {}
for field in fields:
    data[field] = st.text_area(field, value="", height=50 if len(field) > 20 else 30)

# ----- Generate PDF -----
if st.button("Generate PDF with QR Code"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=12*10, rightMargin=12*10, topMargin=12*10, bottomMargin=12*10)
    elements = []

    # Logo
    if logo_path and os.path.exists(logo_path):
        logo_img = Image(logo_path, width=120, height=60)  # حجم أكبر للشعار
        elements.append(logo_img)
        elements.append(Spacer(1, 12))

    # Title
    elements.append(Paragraph("<b>MSAL SHIPPING</b><br/><b>BILL OF LADING</b>", styles['Title']))
    elements.append(Spacer(1, 12))

    # Table
    rows = []
    for key, value in data.items():
        if key != "Tracking URL":
            rows.append([
                Paragraph(key, styles['FieldLabelGreen']),
                Paragraph(value.replace("\n", "<br/>"), styles['FieldValueBlack'])
            ])
    table = Table(rows, colWidths=[80*10, 110*10])
    table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.green),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.green),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # QR Code
    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(data["Tracking URL"])
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    elements.append(Paragraph("<b>Tracking QR Code</b>", styles['FieldLabelGreen']))
    qr_image = Image(qr_buffer, width=80, height=80)
    elements.append(qr_image)

    doc.build(elements)
    buffer.seek(0)

    st.download_button(
        label="Download Bill of Lading PDF",
        data=buffer,
        file_name=f"{data.get('B/L No.', 'BILL_OF_LADING')}.pdf",
        mime="application/pdf"
    )
