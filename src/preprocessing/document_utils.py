import os
import base64
from pathlib import Path
import streamlit as st
import pypandoc
import PyPDF2
from docx import Document
from docx2pdf import convert
import pdfplumber
import re

from src.preprocessing.text_extract import docx_to_text, pdf_to_text
from src.preprocessing.scan_text_extract import image_to_text
from src.preprocessing.pdf_to_image import pdf_to_images

from difflib import HtmlDiff

def generate_diff_html(text1: str, text2: str) -> str:
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()
    diff = HtmlDiff().make_table(lines1, lines2, fromdesc="Document 1", todesc="Document 2")
    return diff


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
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    try:
        convert(str(docx_path), str(output_path))
        pdf_path = output_path / (Path(docx_path).stem + ".pdf")
        return str(pdf_path)
    except Exception as e:
        print(f"Erreur lors de la conversion DOCX → PDF avec docx2pdf: {e}")
        return None

def count_pages(file_path, file_type):
    """Compte le nombre de pages d'un document"""
    try:
        if file_type in ['.jpg', '.jpeg', '.png']:
            return 1
        elif file_type == '.pdf':
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                return len(reader.pages)
        elif file_type == '.docx':
            doc = Document(file_path)
            # Estimation basée sur le nombre de ruptures de section
            return len(doc.sections)
        else:
            raise ValueError(f"Type de fichier non supporté: {file_type}")
    except Exception as e:
        print(f"Erreur lors de la comptage des pages: {str(e)}")
        return 0

def segment_text_by_topics(text):
    """Segmente le texte en sections en fonction de modèles de numérotation"""
    import re
    
    # Modèle pour identifier les sections (ex: 1., 1.1., 2., etc)
    # topic_pattern = r'^\s*(\d+(?:\.\d+)*\.?)\s+(.+)$'
    topic_pattern = r'^\s*(\d+(?:\.\d+)*)(?:\.)?\s+(.+)$'

    
    # Diviser le texte en lignes
    lines = text.split('\n')
    
    # Dictionnaire pour stocker les sections
    topics = {}
    current_topic = None
    current_content = []
    
    for line in lines:
        print(f"[LIGNE] {line}")  # pour vérifier chaque ligne
        match = re.match(topic_pattern, line)
        if match:
            # Si nous avons une section actuel, la sauvegarder
            if current_topic:
                topics[current_topic] = '\n'.join(current_content)
            
            # Commencer un nouveau sujet
            current_topic = match.group(1)
            current_content = [match.group(2)]
        elif current_topic:
            current_content.append(line)
    
    # Ajouter la dernière section
    if current_topic:
        topics[current_topic] = '\n'.join(current_content)
    
    return topics



def detect_section_headings_by_layout(pdf_path, min_font_size=12):
    """ Ouvre un PDF avec pdfplumber. 
        Pour chaque page, lit chaque caractère.
        Si c'est un chiffre isolé avec une grande taille, on le considère comme candidat section.
        Retourne une liste triée par taille décroissante (les chiffres les plus gros d’abord)"""
    
    section_candidates = []
    section_pattern = re.compile(r'^(Article\s+)?\d+(\.\d+)*\.?\s')

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            lines = {}
            for char in page.chars:
                line_key = round(char["top"])  # Regrouper les caractères par ligne
                lines.setdefault(line_key, []).append(char)

            for top, chars in lines.items():
                # Trier les caractères de la ligne par position horizontale
                sorted_chars = sorted(chars, key=lambda c: c["x0"])
                full_text = "".join(c["text"] for c in sorted_chars).strip()

                # Vérifie si la ligne commence par un motif de section (ex: "1.2 Introduction")
                if section_pattern.match(full_text):
                    # Vérifie la taille de police des premiers caractères numériques uniquement
                    first_numeric_chars = [c for c in sorted_chars if c["text"].isdigit() or c["text"] == '.']
                    if first_numeric_chars:
                        avg_size = sum(c["size"] for c in first_numeric_chars) / len(first_numeric_chars)
                        if avg_size >= min_font_size:
                            section_candidates.append({
                                "page": page_num + 1,
                                "text": full_text,
                                "font_size": round(avg_size, 2),
                                "top": top,
                                "left": sorted_chars[0]["x0"]
                            })

    return sorted(section_candidates, key=lambda x: (x["page"], x["top"]))

