from docx import Document
import PyPDF2
import os

def docx_to_text(docx_path):
    """Extrait le texte d'un fichier DOCX"""
    try:
        print(f"Tentative d'extraction du texte du DOCX: {docx_path}")
        doc = Document(docx_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        print(f"Texte extrait du DOCX (longueur: {len(text)}): {text[:100]}...")
        return text
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte du DOCX: {str(e)}")
        return ""

# docx_text = docx_to_text("./docs/examples/doc/exemple1.docx")
# print(docx_text)


def pdf_to_text(pdf_path):
    """Extrait le texte d'un fichier PDF"""
    try:
        print(f"Tentative d'extraction du texte du PDF: {pdf_path}")
        
        # Vérifier si le fichier existe
        if not os.path.exists(pdf_path):
            raise ValueError(f"Le fichier PDF n'existe pas: {pdf_path}")
        
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            
            # Vérifier si le PDF est vide
            if len(reader.pages) == 0:
                print("Le PDF est vide")
                return ""
            
            text = ""
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                print(f"Texte extrait de la page {i+1} (longueur: {len(page_text)}): {page_text[:100]}...")
                text += page_text + "\n"
            
            print(f"Texte total extrait du PDF (longueur: {len(text)}): {text[:100]}...")
            return text
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte du PDF: {str(e)}")
        return ""

# pdf_text = pdf_to_text("./docs/examples/pdf/exemple1_diff.pdf")
# print(pdf_text)