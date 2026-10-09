import streamlit as st
import fitz  # PyMuPDF
import io
import zipfile

st.set_page_config(page_title="PDF Splitter", layout="centered")

st.title("📄 PDF Splitter by Size")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

unit = st.selectbox("Select Size Unit", ["MB", "KB"])

if unit == "MB":
    size = st.number_input(
        "Max size per file (MB)",
        min_value=1,
        value=25
    )
    max_size_bytes = size * 1024 * 1024
else:
    size = st.number_input(
        "Max size per file (KB)",
        min_value=1,
        value=25000
    )
    max_size_bytes = size * 1024

if uploaded_file and st.button("🚀 Split PDF"):

    pdf_bytes = uploaded_file.read()
    src_doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    zip_buffer = io.BytesIO()

    progress = st.progress(0)
    total_pages = len(src_doc)

    with zipfile.ZipFile(
        zip_buffer,
        "w",
        compression=zipfile.ZIP_DEFLATED
    ) as zip_file:

        current_doc = fitz.open()
        part_no = 1

        for page_num in range(total_pages):

            current_doc.insert_pdf(
                src_doc,
                from_page=page_num,
                to_page=page_num
            )

            current_bytes = current_doc.tobytes(
                garbage=3,
                deflate=True
            )

            if len(current_bytes) > max_size_bytes:

                current_doc.delete_page(
                    len(current_doc) - 1
                )

                split_bytes = current_doc.tobytes(
                    garbage=3,
                    deflate=True
                )

                zip_file.writestr(
                    f"part_{part_no}.pdf",
                    split_bytes
                )

                part_no += 1

                current_doc.close()
                current_doc = fitz.open()

                current_doc.insert_pdf(
                    src_doc,
                    from_page=page_num,
                    to_page=page_num
                )

            progress.progress(
                (page_num + 1) / total_pages
            )

        if len(current_doc) > 0:
            zip_file.writestr(
                f"part_{part_no}.pdf",
                current_doc.tobytes(
                    garbage=3,
                    deflate=True
                )
            )

        current_doc.close()

    src_doc.close()

    st.success("✅ PDF Split Successfully!")

    st.download_button(
        label="⬇️ Download Split PDFs (ZIP)",
        data=zip_buffer.getvalue(),
        file_name="split_pdfs.zip",
        mime="application/zip",
    )
