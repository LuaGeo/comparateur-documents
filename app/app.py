import streamlit as st
import sys
import os
from pathlib import Path
from PIL import Image
import io

# Adicionar o diretório raiz ao path para importar os módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.comparaison_tesseract import compare_documents
from src.preprocessing.text_extract import docx_to_text, pdf_to_text
from src.preprocessing.scan_text_extract import image_to_text

st.set_page_config(
    page_title="Comparateur de Documents",
    page_icon="📄",
    layout="centered"
)

st.title("Comparateur de Documents 📄")

st.markdown("""
Cette application permet de comparer deux documents (images, PDF ou DOCX) et d'analyser leurs différences.
""")

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
            return image_to_text(file_path)
        elif file_type == '.pdf':
            return pdf_to_text(file_path)
        elif file_type == '.docx':
            return docx_to_text(file_path)
        else:
            raise ValueError(f"Type de fichier non supporté: {file_type}")
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte: {str(e)}")
        return ""

# Sidebar para upload de arquivos
with st.sidebar:
    st.header("Upload des Documents")
    
    # Upload do primeiro documento
    doc1 = st.file_uploader("Document 1", type=['jpg', 'jpeg', 'png', 'pdf', 'docx'])
    
    # Upload do segundo documento
    doc2 = st.file_uploader("Document 2", type=['jpg', 'jpeg', 'png', 'pdf', 'docx'])
    
    # Botão para iniciar a comparação
    compare_button = st.button("Comparer les Documents")

# Área principal para resultados
if doc1 and doc2 and compare_button:
    # Criar diretório temporário se não existir
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    # Salvar os arquivos temporariamente
    doc1_path = temp_dir / doc1.name
    doc2_path = temp_dir / doc2.name
    
    with open(doc1_path, "wb") as f:
        f.write(doc1.getbuffer())
    with open(doc2_path, "wb") as f:
        f.write(doc2.getbuffer())
    
    try:
        # Extrair texto dos documentos
        file_type1 = Path(doc1.name).suffix.lower()
        file_type2 = Path(doc2.name).suffix.lower()
        
        print(f"Traitement du document 1: {doc1_path}")
        text1 = extract_text_from_file(str(doc1_path), file_type1)
        
        print(f"Traitement du document 2: {doc2_path}")
        text2 = extract_text_from_file(str(doc2_path), file_type2)
        
        if not text1 or not text2:
            raise ValueError("Un des documents n'a pas pu être lu")
        
        # Calcular métricas de comparação
        from Levenshtein import distance
        lev_distance = distance(text1, text2)
        max_len = max(len(text1), len(text2))
        similarity = 1 - (lev_distance / max_len) if max_len > 0 else 0
        
        result = {
            'distance': lev_distance,
            'similarity': similarity,
            'text1_length': len(text1),
            'text2_length': len(text2)
        }
        
        # Exibir resultados
        st.header("Résultats de la Comparaison")
        
        # Configurar o layout para melhor visualização em retrato
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Document 1")
            if file_type1 in ['.jpg', '.jpeg', '.png']:
                img1 = Image.open(io.BytesIO(doc1.getvalue()))
                img1 = rotate_image_to_portrait(img1)
                st.image(img1, use_column_width=True)
            else:
                st.write(f"Type de fichier: {file_type1}")
        
        with col2:
            st.subheader("Document 2")
            if file_type2 in ['.jpg', '.jpeg', '.png']:
                img2 = Image.open(io.BytesIO(doc2.getvalue()))
                img2 = rotate_image_to_portrait(img2)
                st.image(img2, use_column_width=True)
            else:
                st.write(f"Type de fichier: {file_type2}")
        
        # Métricas de comparação em um container separado
        with st.container():
            st.subheader("Métriques de Comparaison")
            col_metrics1, col_metrics2 = st.columns(2)
            
            with col_metrics1:
                st.metric("Similarité", f"{result['similarity']:.2%}")
                st.metric("Distance de Levenshtein", result['distance'])
            
            with col_metrics2:
                st.metric("Longueur Document 1", f"{result['text1_length']} caractères")
                st.metric("Longueur Document 2", f"{result['text2_length']} caractères")
        
        # Exibir os textos extraídos
        with st.expander("Voir les textes extraits"):
            col_text1, col_text2 = st.columns(2)
            with col_text1:
                st.subheader("Texte Document 1")
                st.text_area("", text1, height=300)
            with col_text2:
                st.subheader("Texte Document 2")
                st.text_area("", text2, height=300)
        
    except Exception as e:
        st.error(f"Erreur lors de la comparaison: {str(e)}")
    
    finally:
        # Limpar arquivos temporários
        if doc1_path.exists():
            doc1_path.unlink()
        if doc2_path.exists():
            doc2_path.unlink()

elif compare_button and (not doc1 or not doc2):
    st.warning("Veuillez uploader les deux documents avant de lancer la comparaison.") 