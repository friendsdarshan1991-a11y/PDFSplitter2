import streamlit as st
from pypdf import PdfReader, PdfWriter
import io
import zipfile

st.set_page_config(
    page_title="PDF Splitter",
    layout="centered"
)

st.title("📄 PDF Splitter by Size")

# Upload
uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

# Size Unit
unit = st.selectbox(
    "Select Size Unit",
    ["MB", "KB"]
)

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

if uploaded_file is not None:

    if st.button("🚀 Split PDF"):

        try:
            pdf_bytes = uploaded_file.read()
            reader = PdfReader(io.BytesIO(pdf_bytes))

            total_pages = len(reader.pages)

            zip_buffer = io.BytesIO()

            progress_bar = st.progress(0)

            with zipfile.ZipFile(
                zip_buffer,
                "w",
                zipfile.ZIP_DEFLATED
            ) as zip_file:

                writer = PdfWriter()
                part_num = 1

                for page_index, page in enumerate(reader.pages):

                    # Add page
                    writer.add_page(page)

                    # Check size only every 10 pages
                    should_check = (
                        (page_index + 1) % 10 == 0
                        or page_index == total_pages - 1
                    )

                    if should_check:

                        temp_buffer = io.BytesIO()
                        writer.write(temp_buffer)

                        current_size = temp_buffer.tell()

                        if current_size >= max_size_bytes:

                            # Save current part
                            zip_file.writestr(
                                f"part_{part_num}.pdf",
                                temp_buffer.getvalue()
                            )

                            part_num += 1

                            # Start new PDF
                            writer = PdfWriter()

                    progress_bar.progress(
                        (page_index + 1) / total_pages
                    )

                # Save remaining pages
                if len(writer.pages) > 0:

                    final_buffer = io.BytesIO()
                    writer.write(final_buffer)

                    if final_buffer.tell() > 0:
                        zip_file.writestr(
                            f"part_{part_num}.pdf",
                            final_buffer.getvalue()
                        )

            st.success("✅ PDF Split Successfully!")

            st.download_button(
                label="⬇️ Download Split PDFs (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="split_pdfs.zip",
                mime="application/zip"
            )

        except Exception as e:
            st.error(f"Error: {str(e)}")
