import fitz


def extract_text_from_pdf(pdf_file):
    """
    Extract text and total pages from uploaded PDF.
    """

    # Reset file pointer
    pdf_file.seek(0)

    # Read PDF bytes
    pdf_bytes = pdf_file.read()

    # Open PDF
    pdf = fitz.open(stream=pdf_bytes, filetype="pdf")

    text = ""

    for page in pdf:
        text += page.get_text("text")

    total_pages = pdf.page_count

    pdf.close()

    return text, total_pages