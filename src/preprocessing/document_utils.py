import os
import base64
from pathlib import Path
import streamlit as st
import pypandoc

from src.preprocessing.text_extract import docx_to_text, pdf_to_text
from src.preprocessing.scan_text_extract import image_to_text
from src.preprocessing.pdf_to_image import pdf_to_images

def rotate_image_to_portrait(image):
    """Rotate image to portrait orientation if needed"""
    width, height = image.size
    if width > height:
        return image.rotate(270, expand=True)
    return image

def extract_text_from_file(file_path, file_type):
    """Extrait le texte d'un fichier selon son type"""
    try:
        print(f"Tentative d'extraction du texte de: {file_path}")

        if file_type in ['.jpg', '.jpeg', '.png']:
            text = image_to_text(file_path)
            print(f"Texte extrait de l'image (longueur: {len(text)}): {text[:100]}...")
            return text

        elif file_type == '.pdf':
            text = pdf_to_text(file_path)
            print(f"Texte extrait du PDF (longueur: {len(text)}): {text[:100]}...")

            if not text.strip() or len(text.strip()) < 50:
                print("PDF probablement scanné, conversion en images...")
                image_paths = pdf_to_images(file_path)
                if not image_paths:
                    raise ValueError("Impossible de convertir le PDF en images")

                all_text = []
                for img_path in image_paths:
                    print(f"Traitement de l'image: {img_path}")
                    page_text = image_to_text(img_path)
                    print(f"Texte extrait de la page (longueur: {len(page_text)}): {page_text[:100]}...")
                    if page_text:
                        all_text.append(page_text)

                for img_path in image_paths:
                    if os.path.exists(img_path):
                        os.remove(img_path)

                final_text = "\n".join(all_text)
                print(f"Texte final du PDF scanné (longueur: {len(final_text)}): {final_text[:100]}...")
                return final_text
            return text

        elif file_type == '.docx':
            text = docx_to_text(file_path)
            print(f"Texte extrait du DOCX (longueur: {len(text)}): {text[:100]}...")
            return text

        else:
            raise ValueError(f"Type de fichier non supporté: {file_type}")

    except Exception as e:
        print(f"Erreur lors de l'extraction du texte: {str(e)}")
        return ""

def display_pdf(file_path):
    """Affiche un fichier PDF dans Streamlit via une iframe"""
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def convert_docx_to_pdf(docx_path, output_dir="temp"):
    """Convertit un fichier DOCX en PDF avec Pandoc"""
    pdf_path = Path(output_dir) / (Path(docx_path).stem + ".pdf")
    try:
        pypandoc.convert_file(str(docx_path), 'pdf', outputfile=str(pdf_path))
        return str(pdf_path)
    except Exception as e:
        print(f"Erreur lors de la conversion DOCX → PDF : {e}")
        return None
