from docx import Document
import PyPDF2

def docx_to_text(docx_path):
    doc = Document(docx_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

# docx_text = docx_to_text("./docs/examples/doc/exemple1.docx")
# print(docx_text)


def pdf_to_text(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

# pdf_text = pdf_to_text("./docs/examples/pdf/exemple1_diff.pdf")
# print(pdf_text)