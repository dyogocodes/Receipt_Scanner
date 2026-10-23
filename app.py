"""Streamlit web interface for the DyogoCodes receipt scanner."""
import hashlib
import os

import streamlit as st
from receipt_scanner import (
    items_csv, receipt_json, scan_with_ai, scan_with_local_ocr, summary_csv,
)

st.set_page_config(page_title="Receipt Scanner | DyogoCodes", page_icon="🧾", layout="centered")
st.markdown("# 🧾 Python Receipt Scanner")
st.caption("Photo → Python + OCR/AI → structured data → CSV  |  DyogoCodes")
st.write("Upload a receipt photo or use your camera. Extract the items and download your data.")

mode = st.radio("Extraction method", ["AI Vision (most accurate)", "Free local OCR"], horizontal=True)
if mode.startswith("AI") and not os.getenv("OPENAI_API_KEY"):
    st.info("AI Vision needs an OPENAI_API_KEY in your .env file. Or select Free local OCR.")
if mode.startswith("Free"):
    st.caption("Runs on your computer without an API key. Install Tesseract separately. Some receipt layouts need manual correction.")

upload_tab, camera_tab = st.tabs(["📁 Upload photo", "📷 Take photo"])
with upload_tab:
    upload = st.file_uploader("Choose JPG or PNG", type=["jpg", "jpeg", "png"])
with camera_tab:
    camera = st.camera_input("Capture a receipt")

image_file = camera if camera is not None else upload
if image_file is not None:
    data = image_file.getvalue()
    digest = hashlib.sha256(data).hexdigest()
    st.image(data, caption="Selected receipt", use_container_width=True)
    if upload is not None and camera is not None:
        st.caption("Both images are selected; the camera photo takes priority.")
    if st.button("🔍 Scan receipt", type="primary", use_container_width=True):
        with st.spinner("Reading receipt..."):
            try:
                receipt = scan_with_ai(data) if mode.startswith("AI") else scan_with_local_ocr(data)
            except Exception as exc:
                st.session_state.pop("receipt_result", None)
                st.error(f"Scan failed: {exc}")
            else:
                st.session_state["receipt_result"] = (digest, mode, receipt)

    saved = st.session_state.get("receipt_result")
    if saved is not None and saved[0] == digest and saved[1] == mode:
        receipt = saved[2]
        st.success("Receipt processed. Review the extracted values before using them.")
        a, b, c = st.columns(3)
        a.metric("Store", receipt.store or "Not found")
        b.metric("Date", receipt.date or "Not found")
        c.metric("Total", (f"{receipt.total:.2f} {receipt.currency or ''}" if receipt.total is not None else "Not found"))
        st.write("**Time:**", receipt.time or "Not found")
        st.subheader("Purchased items")
        if receipt.items:
            st.dataframe([item.model_dump() for item in receipt.items], hide_index=True, use_container_width=True)
        else:
            st.warning("No line items detected. Try a brighter photo or AI Vision.")
        with st.expander("Full structured JSON"):
            st.json(receipt.model_dump())
        st.subheader("Download")
        st.download_button("⬇️ Receipt summary CSV", data=summary_csv(receipt).encode("utf-8-sig"),
                           file_name="receipt_summary.csv", mime="text/csv", use_container_width=True)
        st.download_button("⬇️ Purchased items CSV", data=items_csv(receipt).encode("utf-8-sig"),
                           file_name="receipt_items.csv", mime="text/csv", use_container_width=True)
        st.download_button("⬇️ JSON", data=receipt_json(receipt),
                           file_name="receipt.json", mime="application/json", use_container_width=True)

st.divider()
st.caption("🔐 Local OCR processes photos on your machine. AI Vision sends photos to the OpenAI API and may incur charges. Never put your API key in public code.")
