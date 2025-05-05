import streamlit as st
import sys
import os
from pathlib import Path
from PIL import Image
import io

# Ajoutez le répertoire racine au chemin d'accès pour importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent))

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
            text = image_to_text(file_path)
            print(f"Texte extrait de l'image (longueur: {len(text)}): {text[:100]}...")
            return text
        elif file_type == '.pdf':
            # Tenter d'abord d'extraire le texte directement
            text = pdf_to_text(file_path)
            print(f"Texte extrait du PDF (longueur: {len(text)}): {text[:100]}...")
            
            # Si le texte est vide ou très court, c'est probablement un PDF scanné
            if not text.strip() or len(text.strip()) < 50:
                print("PDF probablement scanné, conversion en images...")
                from src.preprocessing.pdf_to_image import pdf_to_images
                
                # Convertir le PDF en images
                image_paths = pdf_to_images(file_path)
                if not image_paths:
                    raise ValueError("Impossible de convertir le PDF en images")
                
                # Extraire le texte de chaque page
                all_text = []
                for img_path in image_paths:
                    print(f"Traitement de l'image: {img_path}")
                    page_text = image_to_text(img_path)
                    print(f"Texte extrait de la page (longueur: {len(page_text)}): {page_text[:100]}...")
                    if page_text:
                        all_text.append(page_text)
                
                # Nettoyer les fichiers temporaires
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

# Barre latérale pour télécharger des fichiers
with st.sidebar:
    st.header("Upload des Documents")
    
    # Téléchargement du premier document
    doc1 = st.file_uploader("Document 1", type=['jpg', 'jpeg', 'png', 'pdf', 'docx'])
    
    # Téléchargement du deuxième document
    doc2 = st.file_uploader("Document 2", type=['jpg', 'jpeg', 'png', 'pdf', 'docx'])
    
    # Bouton pour lancer la comparaison
    compare_button = st.button("Comparer les Documents")

# Champ principal pour les résultats
if doc1 and doc2 and compare_button:
    # Créer un répertoire temporaire si ce n'est pas déjà fait
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    # Enregistrer les fichiers temporairement
    doc1_path = temp_dir / doc1.name
    doc2_path = temp_dir / doc2.name
    
    with open(doc1_path, "wb") as f:
        f.write(doc1.getbuffer())
    with open(doc2_path, "wb") as f:
        f.write(doc2.getbuffer())
    
    try:
        # Extraire le texte des documents
        file_type1 = Path(doc1.name).suffix.lower()
        file_type2 = Path(doc2.name).suffix.lower()
        
        print(f"Traitement du document 1: {doc1_path} (type: {file_type1})")
        text1 = extract_text_from_file(str(doc1_path), file_type1)
        print(f"Texte extrait du document 1 (longueur: {len(text1)}): {text1[:100]}...")
        
        print(f"Traitement du document 2: {doc2_path} (type: {file_type2})")
        text2 = extract_text_from_file(str(doc2_path), file_type2)
        print(f"Texte extrait du document 2 (longueur: {len(text2)}): {text2[:100]}...")
        
        if not text1:
            raise ValueError(f"Le document 1 n'a pas pu être lu (type: {file_type1})")
        if not text2:
            raise ValueError(f"Le document 2 n'a pas pu être lu (type: {file_type2})")
        
        # Calculer les métriques de comparaison
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
        
        # Afficher les résultats
        st.header("Résultats de la Comparaison")
        
        # Configurer le layout pour une meilleure visualisation en portrait
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
        
        # Métriques de comparaison dans un conteneur séparé
        with st.container():
            st.subheader("Métriques de Comparaison")
            col_metrics1, col_metrics2 = st.columns(2)
            
            with col_metrics1:
                st.metric("Similarité", f"{result['similarity']:.2%}")
                st.metric("Distance de Levenshtein", result['distance'])
            
            with col_metrics2:
                st.metric("Longueur Document 1", f"{result['text1_length']} caractères")
                st.metric("Longueur Document 2", f"{result['text2_length']} caractères")
        
        # Afficher les textes extraits
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
        # Nettoyer les fichiers temporaires
        if doc1_path.exists():
            doc1_path.unlink()
        if doc2_path.exists():
            doc2_path.unlink()

elif compare_button and (not doc1 or not doc2):
    st.warning("Veuillez uploader les deux documents avant de lancer la comparaison.") 