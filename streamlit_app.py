import streamlit as st

st.set_page_config(page_title="CodeCraft AI", layout="centered")
st.title("📄 Get Your Project PDF")

if st.query_params.get("payment_success") == "1":
    st.success("✅ Payment successful! Download your project below.")
    with open("example.pdf", "rb") as f:
        st.download_button("📥 Download PDF", f, "project.pdf")
else:
    st.info("To download the project, you need to make a ₹2 payment.")
    st.link_button("💳 Pay ₹2", "http://localhost:5000/pay")
