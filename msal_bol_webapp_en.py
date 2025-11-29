# msal_bol_webapp_en.py
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
from PIL import Image as PilImage
import io
import os

base_font = "Helvetica"
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Title', fontName=base_font, fontSize=16, leading=18, alignment=1))
styles.add(ParagraphStyle(name='FieldLabel', fontName=base_font, fontSize=9, leading=11))
styles.add(ParagraphStyle(name='FieldValue', fontName=base_font, fontSize=9, leading=11))

st.title("MSAL Shipping - Bill of Lading Generator")

logo_path = "msal_logo.png"  # replace with your logo file or None

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
    data[field] = st.text_area(field, value="", height=50 if len(field)>20 else 30)

if st.button("Generate PDF with QR Code"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,leftMargin=12*10, rightMargin=12*10, topMargin=12*10, bottomMargin=12*10)
    elements = []

    if logo_path and os.path.exists(logo_path):
        logo_img = Image(logo_path, width=80, height=40)
        elements.append(logo_img)
        elements.append(Spacer(1, 6))

    elements.append(Paragraph("<b>MSAL SHIPPING</b><br/><b>BILL OF LADING</b>", styles['Title']))
    elements.append(Spacer(1, 8))

    rows = []
    for key, value in data.items():
        if key != "Tracking URL":
            rows.append([Paragraph(f"<b>{key}</b>", styles['FieldLabel']), Paragraph(value.replace("\n", "<br/>"), styles['FieldValue'])])
    table = Table(rows, colWidths=[80*10, 110*10])
    table.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 0.5, colors.black),('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),('VALIGN', (0,0), (-1,-1), 'TOP'),('LEFTPADDING', (0,0), (-1,-1), 4),('RIGHTPADDING', (0,0), (-1,-1), 4)]))
    elements.append(table)
    elements.append(Spacer(1, 8))

    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(data["Tracking URL"])
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    elements.append(Paragraph("<b>Tracking QR Code</b>", styles['FieldLabel']))
    qr_image = Image(qr_buffer, width=80, height=80)
    elements.append(qr_image)

    doc.build(elements)
    buffer.seek(0)

    st.download_button(label="Download Bill of Lading PDF", data=buffer, file_name=f"{data.get('B/L No.', 'BILL_OF_LADING')}.pdf", mime="application/pdf")
