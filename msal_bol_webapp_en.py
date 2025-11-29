def main():
    st.set_page_config(layout="wide", page_title="أداة سند الشحن")
    
    st.title("🚢 أداة إنشاء سند الشحن (Bill of Lading)")
    
    # عرض الشعار في واجهة Streamlit إذا كان موجوداً
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=100)
    
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
            
            # 🚨 التصحيح هنا: استبدال '---' بـ st.markdown("---")
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
