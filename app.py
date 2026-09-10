# Required installs:
# pip install streamlit PyPDF2

import streamlit as st
from pypdf import PdfReader, PdfWriter
import io
import zipfile

st.set_page_config(page_title="PDF Splitter", layout="centered")

st.title("📄 PDF Splitter by Size")

# Upload
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

# Unit selection
unit = st.selectbox("Select Size Unit", ["MB", "KB"])

# Dynamic input based on unit
if unit == "MB":
    size = st.number_input("Max size per file (MB)", min_value=1, value=25)
    max_size_bytes = size * 1024 * 1024
else:
    size = st.number_input("Max size per file (KB)", min_value=1, value=25000)
    max_size_bytes = size * 1024

# Button
if uploaded_file is not None:
    if st.button("🚀 Split PDF"):

        reader = PdfReader(uploaded_file)

        writer = PdfWriter()
        part_num = 1

        zip_buffer = io.BytesIO()
        zip_file = zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED)

        progress = st.progress(0)
        total_pages = len(reader.pages)

        for i, page in enumerate(reader.pages):
            writer.add_page(page)

            temp_buffer = io.BytesIO()
            writer.write(temp_buffer)

            # Size check
            if temp_buffer.tell() >= max_size_bytes:
                file_name = f"part_{part_num}.pdf"
                zip_file.writestr(file_name, temp_buffer.getvalue())

                part_num += 1
                writer = PdfWriter()

            # Update progress
            progress.progress((i + 1) / total_pages)

        # Save remaining pages
        if len(writer.pages) > 0:
            temp_buffer = io.BytesIO()
            writer.write(temp_buffer)
            file_name = f"part_{part_num}.pdf"
            zip_file.writestr(file_name, temp_buffer.getvalue())

        zip_file.close()

        st.success("✅ PDF Split Successfully!")

        # Download
        st.download_button(
            label="⬇️ Download Split PDFs (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="split_pdfs.zip",
            mime="application/zip"
        )
