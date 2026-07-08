from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)

    resume_text = ""
    for page in reader.pages:
        text = page.extract_text()
        resume_text += text
    return resume_text
