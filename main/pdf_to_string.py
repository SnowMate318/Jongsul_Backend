from PyPDF2 import PdfReader

def pdfToString(pdf_file):
    pdf_file = open(pdf_file, 'rb')
    pdf_reader = PyPDFLoader(pdf_file)
    pdf_text = pdf_reader.load()
    return pdf_text

